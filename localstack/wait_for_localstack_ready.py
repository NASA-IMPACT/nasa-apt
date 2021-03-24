import boto3
import botocore
from datetime import datetime
import os
import time


start_time = datetime.now()
count = 0


def aws_resources_ready():
    s3 = boto3.client("s3", endpoint_url=os.environ["AWS_RESOURCES_ENDPOINT"])
    if not (
        {b["Name"] for b in s3.list_buckets()["Buckets"]}
        == {"nasa-apt-dev-figures", "nasa-apt-dev-pdfs"}
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
        time.sleep(2 ** count)
        count += 1
