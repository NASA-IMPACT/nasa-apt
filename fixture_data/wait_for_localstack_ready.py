"""Localstack startup script
"""
import os
import time
from datetime import datetime

import boto3
import botocore

start_time = datetime.now()
count = 0


def aws_resources_ready():
    """
    Returs true if all necessary startup resources are present in Localstack
    """
    s3 = boto3.client("s3", endpoint_url=os.environ["AWS_RESOURCES_ENDPOINT"])
    if not (
        {b["Name"] for b in s3.list_buckets()["Buckets"]} == {os.environ["S3_BUCKET"]}
    ):
        return False
    sm = boto3.client(
        "secretsmanager", endpoint_url=os.environ["AWS_RESOURCES_ENDPOINT"]
    )
    if not (
        {s["Name"] for s in sm.list_secrets()["SecretList"]}
        == {"mocked_credentials_arn"}
    ):
        return False

    sqs = boto3.resource("sqs", endpoint_url=os.environ["AWS_RESOURCES_ENDPOINT"])
    if not ({q.url.split("/")[-1] for q in sqs.queues.all()} == {"dev-tasks"}):
        return False

    cognito = boto3.client(
        "cognito-idp", endpoint_url=os.environ["AWS_RESOURCES_ENDPOINT"]
    )
    if not (
        {u["Name"] for u in cognito.list_user_pools(MaxResults=1)["UserPools"]}
        == {"dev-users"}
    ):
        print(
            "User pools: ",
            {u for u in cognito.list_user_pools(MaxResults=1)["UserPools"]},
        )
        return False
    else:
        print(
            "User pools: ",
            [u["Id"] for u in cognito.list_user_pools(MaxResults=1)["UserPools"]],
        )
        [user_pool_id] = [
            x["Id"] for x in cognito.list_user_pools(MaxResults=1)["UserPools"]
        ]

        if not (
            {
                u["ClientName"]
                for u in cognito.list_user_pool_clients(
                    MaxResults=1, UserPoolId=user_pool_id
                )["UserPoolClients"]
            }
            == {"dev-client"}
        ):
            print(
                "User pool clients: ",
                {
                    u["ClientId"]
                    for u in cognito.list_user_pool_clients(
                        MaxResults=1, UserPoolId=user_pool_id
                    )["UserPoolClients"]
                },
            )
            return False

    print("All resources ready!")
    return True


if __name__ == "__main__":
    count = 0

    while (datetime.now() - start_time).total_seconds() <= int(
        os.environ.get("LOCALSTACK_READY_TIMEOUT", "360")
    ):
        print("Checking for S3 and SecretsManager resources")
        try:
            if aws_resources_ready():
                exit()
        except botocore.exceptions.EndpointConnectionError:
            pass
        print(f"Not all resources ready, sleeping {2 ** count} seconds")
        time.sleep(2**count)
        count += 1
