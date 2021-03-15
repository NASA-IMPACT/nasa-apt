import requests as re
from datetime import datetime, timedelta
import json
from jose import jwt
import os
import boto3

# endpoint = "https://7rofk8zck6.execute-api.us-east-1.amazonaws.com"
endpoint = "http://localhost:8000"
token_life = 60 * 60
secrets_manager = boto3.Session(profile_name="dev-seed").client("secretsmanager")
cloudformation = boto3.Session(profile_name="dev-seed").client("cloudformation")


def create_token():
    return jwt.encode(create_token_data(), os.environ["JWT_SECRET"])


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
        secrets_manager.get_secret_value(SecretId=get_secrets_arn(),)["SecretString"]
    )
    return f"postgres://{values['username']}:{values['password']}@{values['host']}:{values['port']}/{values['dbname']}"


def pprint(data):
    print(json.dumps(json.loads(data), indent=4, sort_keys=True))
    print("\n")


atbd_alias = "test-atbd-3"

# r = re.post(
#     f"{endpoint}/atbds",
#     headers={"Authorization": f"Bearer {create_token()}"},
#     data=json.dumps({"title": "This is a title", "alias": f"{atbd_alias}"}),
# )
# r = re.post(
#     f"{endpoint}/atbds/{atbd_alias}/versions/v1.0",
#     headers={"Authorization": f"Bearer {create_token()}"},
#     data=json.dumps({"document": {"new_key": "new_val3"}}),
# )
r = re.post(
    f"{endpoint}/atbds/{atbd_alias}",
    data=json.dumps({"title": "A new title 2"}),
    headers={"Authorization": f"Bearer {create_token()}"},
)
print(r.content)
r = re.get(
    f"{endpoint}/atbds/{atbd_alias}/versions/v1.0",
    headers={"Authorization": f"Bearer {create_token()}"},
)
print(r.content)

