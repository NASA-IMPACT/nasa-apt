"""Utility script for loading existing data from disk to the APT backend."""
import argparse
import json
import re
import subprocess
import time
from typing import Dict, List

import boto3
import requests  # type: ignore

parser = argparse.ArgumentParser()

parser.add_argument(
    "--target-stack-name", help="Name of the CDK stack to migrate data TO"
)

parser.add_argument(
    "--source-cognito-users",
    help="CSV file containing the user info of the source stack's cognito users",
)
parser.add_argument(
    "--source-database-dump",
    help="SQL File containing the contents of the source stack's postgres database (generated using the `pg_dump` command",
)
parser.add_argument(
    "--source-s3-bucket-contents-dir",
    help="Directory containing the contents of the S3 bucket (generated using the `s3 sync` command)",
)

args = parser.parse_args()

TARGET_STACK_NAME = args.target_stack_name
SOURCE_COGNITO_USERS_FILE = args.source_cognito_users
SOURCE_DATABASE_DUMP_FILE = args.source_database_dump
SOURCE_S3_BUCKET_CONTENTS_DIR = args.source_s3_bucket_contents_dir

if not SOURCE_COGNITO_USERS_FILE.endswith(".csv"):
    raise Exception(
        f"Cognito users input file ({SOURCE_COGNITO_USERS_FILE}) should be a `.csv` file"
    )
if not SOURCE_DATABASE_DUMP_FILE.endswith(".sql"):
    raise Exception(
        f"Database input file ({SOURCE_DATABASE_DUMP_FILE}) should be a `.sql` file"
    )
if "." in SOURCE_S3_BUCKET_CONTENTS_DIR or not SOURCE_S3_BUCKET_CONTENTS_DIR.endswith(
    "-files"
):
    raise Exception(
        f"S3 input dir ({SOURCE_DATABASE_DUMP_FILE}) should contain no periods `.` and end with `-files`"
    )


cf_client = boto3.client("cloudformation")
cognito_client = boto3.client("cognito-idp")
secretsmanager_client = boto3.client("secretsmanager")


def import_cognito_users(target_user_pool_id: str) -> List[Dict]:
    """Launches a user import job using a local CSV file. Then queries
    the newley created users, adding them to the groups they were
    originally part of, and then returns a mapping containing the old and new
    user sub for each user. This mapping will be used to replace the user subs
    in the database file, to appropriately re-assign ATBD, Versions, Comments,
    etc to their original owners"""
    user_import_job = cognito_client.create_user_import_job(
        JobName=f"{TARGET_STACK_NAME}-user-import",
        UserPoolId=target_user_pool_id,
        # DevSeed: arn:aws:iam::552819999234:role/GrantCognitoAccessToCloudWatchLogs
        # GCC: arn:aws:iam::237694371684:role/CognitoAccessToCloudwatch
        CloudWatchLogsRoleArn="arn:aws:iam::237694371684:role/CognitoAccessToCloudwatch",
    )["UserImportJob"]

    # Upload users file
    with open(SOURCE_COGNITO_USERS_FILE, "r") as f:
        r = requests.put(
            user_import_job["PreSignedUrl"],
            data=f.read(),
            headers={
                "x-amz-server-side-encryption": "aws:kms",
                "Content-Disposition": "attachment;filename=filename.csv",
            },
        )
        if not r.status_code == 200:
            raise Exception(r.text)

    resp = cognito_client.describe_user_import_job(
        UserPoolId=target_user_pool_id, JobId=user_import_job["JobId"]
    )

    resp = cognito_client.start_user_import_job(
        UserPoolId=target_user_pool_id, JobId=user_import_job["JobId"]
    )["UserImportJob"]
    while resp["Status"] in ["Pending", "InProgress", "Stopping"]:
        time.sleep(5)
        resp = cognito_client.describe_user_import_job(
            UserPoolId=target_user_pool_id, JobId=user_import_job["JobId"]
        )["UserImportJob"]

    if not resp["Status"] == "Succeeded":
        raise Exception("User import job FAILED: ", resp)

    print(
        f"User import job finished. Imported users: {resp['ImportedUsers']}, skipped: {resp['SkippedUsers']}, failed: {resp['FailedUsers']}"
    )

    resp = cognito_client.list_users(UserPoolId=target_user_pool_id)
    target_users = resp["Users"]
    while "PaginationToken" in resp:
        resp = cognito_client.list_users(
            UserPoolId=target_user_pool_id, PaginationToken=resp["PaginationToken"]
        )
        target_users.extend(resp["Users"])

    target_users = [
        {a["Name"]: a["Value"] for a in u["Attributes"]} for u in target_users
    ]

    with open(SOURCE_COGNITO_USERS_FILE.replace(".csv", "-subs.json"), "r") as f:
        source_users = json.loads(f.read())

    user_mapping = [{"email": u["email"], "target_sub": u["sub"]} for u in target_users]

    for target_user in user_mapping:
        source_user = [
            source_user
            for source_user in source_users
            # cast email's to lower case since the User Pool has been updated
            # to be case insensitive
            if source_user["email"].lower() == target_user["email"].lower()
        ]
        if not len(source_user) == 1:
            raise Exception(
                "Unable to find source user for user: ",
                target_user,
                ". Source user: ",
                source_users,
            )
        [source_user] = source_user

        # ignore on the following lines because mypy beleives `source_user`
        # is still type List, as defined on line 125, even though
        # `source_user` has been converted to a dict in line 139
        target_user["source_sub"] = source_user["sub"]  # type: ignore

        # Add users to groups
        [group] = source_user["cognito:groups"]  # type: ignore

        cognito_client.admin_add_user_to_group(
            UserPoolId=target_user_pool_id,
            Username=target_user["target_sub"],
            GroupName=group,
        )

    if any([user.get("source_sub") is None for user in user_mapping]):
        raise Exception("Some target users missing source_subs", user_mapping)

    if not len(source_users) == len(target_users) == len(user_mapping):
        raise Exception(
            f"Some users missing. Source users count: {len(source_users)}, target users count: {len(target_users)}, user mapping count: {len(user_mapping)}"
        )

    return user_mapping


def upload_to_database(
    database_secrets_manager_arn: str, user_mapping: List[Dict]
) -> str:
    """Uploads data from disk to an RDS postgres instance. Uses the
    provided user_mapping to replace the user subs of data in the local
    file with the user subs of the newly created users in cognito."""
    with open(SOURCE_DATABASE_DUMP_FILE, "r") as f:
        database_dump = f.read()

    for user in user_mapping:
        database_dump = database_dump.replace(user["source_sub"], user["target_sub"])

    [CURATOR_SUB] = [
        target_user["target_sub"]
        for target_user in user_mapping
        if target_user["email"] == "leo+curator@developmentseed.org"
    ]

    def replace_missing_sub_with_curator_sub(match):

        if match.group(0) in [
            target_user["target_sub"] for target_user in user_mapping
        ]:
            return match.group(0)
        return CURATOR_SUB

    database_dump = re.sub(
        # matches cognito subs while ignoring filenames with a UUID
        r"([0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12})(?!\.(jpg|JPG|jpeg|JPEG|png|PNG))",
        replace_missing_sub_with_curator_sub,
        database_dump,
    )

    with open(SOURCE_DATABASE_DUMP_FILE, "w") as f:
        f.write(database_dump)

    secrets = json.loads(
        secretsmanager_client.get_secret_value(SecretId=database_secrets_manager_arn)[
            "SecretString"
        ]
    )

    dsn = f"postgres://{secrets['username']}:{secrets['password']}@{secrets['host']}/{secrets['dbname']}"

    subprocess.Popen(
        f"psql '{dsn}?options=--search_path%3dapt' -f {SOURCE_DATABASE_DUMP_FILE}",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read()
    return SOURCE_DATABASE_DUMP_FILE


def upload_s3_bucket_content(s3_bucket_name):
    """Sync from local file to S3 bucket"""
    subprocess.Popen(
        f"aws s3 sync ./{SOURCE_S3_BUCKET_CONTENTS_DIR} s3://{s3_bucket_name}",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read()

    return s3_bucket_name


if __name__ == "__main__":
    """Run migration --> upload"""

    stack_resources = cf_client.describe_stack_resources(StackName=TARGET_STACK_NAME)[
        "StackResources"
    ]
    [s3_bucket] = list(
        filter(lambda x: x["ResourceType"] == "AWS::S3::Bucket", stack_resources)
    )
    [cognito_user_pool] = list(
        filter(lambda x: x["ResourceType"] == "AWS::Cognito::UserPool", stack_resources)
    )
    [database_secrets_manager] = list(
        filter(
            lambda x: x["ResourceType"] == "AWS::SecretsManager::Secret",
            stack_resources,
        )
    )

    print("Importing users into cognito...")
    user_mapping = import_cognito_users(cognito_user_pool["PhysicalResourceId"])
    print("Done. Replacing user subs and uploading to target database...")
    upload_to_database(database_secrets_manager["PhysicalResourceId"], user_mapping)
    print("Done. Synchronizing S3 bucket to target...")
    upload_s3_bucket_content(s3_bucket["PhysicalResourceId"])
    print("Done. Data migration complete")
