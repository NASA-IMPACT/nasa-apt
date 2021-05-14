import requests as re
from datetime import datetime, timedelta
import json
from jose import jwt
import os
import boto3
from requests_aws4auth import AWS4Auth
import time

token_life = 60 * 60 * 24
secrets_manager = boto3.Session(profile_name="dev-seed").client("secretsmanager")
cloudformation = boto3.Session(profile_name="dev-seed").client("cloudformation")
credentials = boto3.Session(profile_name="dev-seed").get_credentials()


def aws_auth():
    region = "us-east-1"
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        "es",
        session_token=credentials.token,
    )
    return awsauth


def create_token():
    return jwt.encode(create_token_data(), os.environ["JWT_SECRET"])


def auth_headers():
    return {"Authorization": f"Bearer {create_token()}"}


def create_token_data():
    exp = datetime.utcnow() + timedelta(seconds=token_life)
    data = {
        "userdata": {"user": "mocked-auth-user"},
        "name_id": "nameid",
        "nq": "np",
        "spnq": "spnq",
        "name_id_format": "formate",
        "session_index": "index",
        "exp": exp,
        "role": "app_user",
    }
    return data


def get_secrets_arn():

    return [
        o["OutputValue"]
        for o in cloudformation.describe_stacks(StackName="nasa-apt-lambda-dev")[
            "Stacks"
        ][0]["Outputs"]
        if o["OutputKey"] == "nasaaptlambdadevdatabasesecretarn"
    ][0]


def create_pg_connection_string():
    values = json.loads(
        secrets_manager.get_secret_value(
            SecretId=get_secrets_arn(),
        )["SecretString"]
    )
    return f"postgres://{values['username']}:{values['password']}@{values['host']}:{values['port']}/{values['dbname']}"


def pprint(data):
    print(json.dumps(json.loads(data), indent=4, sort_keys=True))
    print("\n")


# endpoint = "https://nuo783m1th.execute-api.us-east-1.amazonaws.com"
# es_endpoint = "http://search-nasa-apt-lambda-dev-elastic-ze76i6s5yajg4kqzkanr2orzvy.us-east-1.es.amazonaws.com"
endpoint = "http://localhost:8000"
es_endpoint = "http://localhost:9200"


# r = re.get(
#     f"{endpoint}/search",
#     #    auth=aws_auth(),
#     headers={
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {create_token()}",
#     },
#     data=json.dumps(
#         {"query": {"bool": {"must": [{"multi_match": {"query": "kelvins"}}]}}}
#     ),
# )
# print("Search result: ")
# print(r.content)

print(create_pg_connection_string())
print(create_token())
