"""Utility script for downloading all stateful data from an APT backend stack, in order to migrate it to a new backend."""
import argparse
import csv
import json
import subprocess
from typing import Dict, List, Union

import boto3

cf_client = boto3.client("cloudformation")
cognito_client = boto3.client("cognito-idp")
secretsmanager_client = boto3.client("secretsmanager")

parser = argparse.ArgumentParser()

parser.add_argument(
    "--source-stack-name", help="Name of the CDK stack to migrate data FROM"
)

args = parser.parse_args()

SOURCE_STACK_NAME = args.source_stack_name


def serialize_user_pool_users_to_csv(user_pool_id: str) -> str:
    """Generates 2 files:
    - a .csv file with user info (but no user subs) to be used in a Cognito user import job
    - a .json file that contains email, preferred_username and user sub for each user, to
    be used to replace cognito subs in the database file when uploading database content
    """

    users = []
    for group in ["curator", "contributor"]:
        paginator = cognito_client.get_paginator("list_users_in_group")
        response = paginator.paginate(UserPoolId=user_pool_id, GroupName=group)
        for page in response:
            users.extend(
                [
                    {
                        "cognito:groups": [group],
                        **{a["Name"]: a["Value"] for a in user["Attributes"]},
                    }
                    for user in page.get("Users", [])
                ]
            )

    # Store users with subs for mapping old user subs to new user subs
    with open(f"{user_pool_id}-users-subs.json", "w") as f:
        f.write(json.dumps(users))

    # store users without subs into the csv file that will be uploaded to start
    # the user import process
    # add email to the `cognito:username` field in order to allow users to sign
    # is using emails as a username attribute
    cognito_users: List[Dict[str, Union[str, List[str]]]] = [
        {
            "cognito:username": user["email"],
            "cognito:mfa_enabled": "false",
            "phone_number_verified": "false",
            "email_verified": "true",
            **{k: v for k, v in user.items() if k not in ["sub", "cognito:groups"]},
        }
        for user in users
    ]

    csv_header = cognito_client.get_csv_header(UserPoolId=user_pool_id)["CSVHeader"]

    with open(f"{user_pool_id}-users.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_header)
        writer.writeheader()
        writer.writerows(cognito_users)

    return f"{user_pool_id}-users.csv"


def serialize_postgres_data_to_file(database_secrets_manager_arn: str) -> str:
    """Download postgres data to disk"""
    secrets = json.loads(
        secretsmanager_client.get_secret_value(SecretId=database_secrets_manager_arn)[
            "SecretString"
        ]
    )

    dsn = f"postgres://{secrets['username']}:{secrets['password']}@{secrets['host']}/{secrets['dbname']}"
    filename = f"{secrets['dbInstanceIdentifier']}-data.sql"

    subprocess.Popen(
        f"pg_dump --data-only --column-inserts -d {dsn} > {filename}",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read()

    return filename


def serialize_s3_bucket_to_local_dir(s3_bucket_name: str) -> str:
    """Download S3 bucket content to disk"""

    subprocess.Popen(
        f"aws s3 sync s3://{s3_bucket_name} ./{s3_bucket_name}-files",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read()

    return s3_bucket_name


if __name__ == "__main__":
    """Run migration --> download"""
    stack_resources = cf_client.describe_stack_resources(StackName=SOURCE_STACK_NAME)[
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
    print("Downloading user data from Cognito...")
    users_file = serialize_user_pool_users_to_csv(
        cognito_user_pool["PhysicalResourceId"]
    )
    print(f"Done. Saved at: {users_file}")

    print("Downloading data from the Postgres Database...")
    database_file = serialize_postgres_data_to_file(
        database_secrets_manager["PhysicalResourceId"]
    )
    print(f"Done. Saved at: {database_file}")

    print("Downloading files from S3 Bucket...")
    s3_files_folder = serialize_s3_bucket_to_local_dir(s3_bucket["PhysicalResourceId"])
    print(f"Done. Saved at {s3_files_folder}")


"""
aws iam create-role --role-name GrantCognitoAccessToCloudWatchLogs --assume-role-policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "cognito-idp.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }'
aws iam create-policy --policy-name CloudWatchCognitoPolicy --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents"
            ],
            "Resource": [
                "arn:aws:logs:us-east-1:237694371684:log-group:/aws/cognito/*"
            ]
        }
    ]
}'

aws iam attach-role-policy --policy-arn ... --role-name GrantCognitoAccessToCloudWatchLogs
"""


# To transfer files from local to remote:
# scp /path/to/file username@a:/path/to/destination
# To transfer directory from local to remote:
# scp -r /path/to/dir username@a:~/dir
