import argparse
import csv
import json
import subprocess

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
    resp = cognito_client.list_users(UserPoolId=user_pool_id)
    users = resp["Users"]
    while "PaginationToken" in resp:
        resp = cognito_client.list_users(
            UserPoolId=user_pool_id, PaginationToken=resp["PaginationToken"]
        )
        users.extend(resp["Users"])

    users = [{a["Name"]: a["Value"] for a in u["Attributes"]} for u in users]

    with open(f"{user_pool_id}-users.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=users[0].keys())
        writer.writeheader()
        writer.writerows(users)

    return f"{user_pool_id}-users.csv"


def serialize_postgres_data_to_file(database_secrets_manager_arn: str) -> str:
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

    subprocess.Popen(
        f"aws s3 sync s3://{s3_bucket_name} ./{s3_bucket_name}-files",
        shell=True,
        stdout=subprocess.PIPE,
    ).stdout.read()

    return s3_bucket_name


if __name__ == "__main__":

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
