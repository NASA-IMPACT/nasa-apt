import requests as re
from datetime import datetime, timedelta
import json
from jose import jwt
import os
import boto3
from requests_aws4auth import AWS4Auth
import time

token_life = 60 * 60
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


atbd_data = {
    "document": {
        "scientific_theory": {
            "document": {
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [{"text": "A line of text in a paragraph."}],
                            }
                        ],
                    },
                    {
                        "object": "block",
                        "type": "equation",
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [{"text": "\\int_0^\\infty x^2 dx"}],
                            }
                        ],
                    },
                    {
                        "object": "block",
                        "type": "image",
                        "data": {
                            "src": "http://localstack:4566/nasa-apt-dev-figures/fullmoon.jpg",
                            "caption": "Image of the full moon - 2019",
                        },
                    },
                ]
            }
        },
        "introduction": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "An introduction.",
                                        "marks": [],
                                    }
                                ],
                            }
                        ],
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [{"object": "leaf", "text": "", "marks": []}],
                            }
                        ],
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [{"object": "leaf", "text": "", "marks": []}],
                            }
                        ],
                    },
                    {
                        "object": "block",
                        "type": "table",
                        "caption": "A Table containing important data",
                        "data": {"headless": True},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "table_row",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Table Column 1",
                                                                "marks": [
                                                                    {
                                                                        "object": "mark",
                                                                        "type": "bold",
                                                                        "data": {},
                                                                    }
                                                                ],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Table Column 2",
                                                                "marks": [
                                                                    {
                                                                        "object": "mark",
                                                                        "type": "bold",
                                                                        "data": {},
                                                                    }
                                                                ],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Table Column 3",
                                                                "marks": [
                                                                    {
                                                                        "object": "mark",
                                                                        "type": "bold",
                                                                        "data": {},
                                                                    }
                                                                ],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                ],
                            },
                            {
                                "object": "block",
                                "type": "table_row",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Cell value (short)",
                                                                "marks": [],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Cell value (long) - This is a super long cell value. It should be wrapped several times, perhaps 2 but although at this point maybe even 3. ",
                                                                "marks": [],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Cell value (short)",
                                                                "marks": [],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                ],
                            },
                            {
                                "object": "block",
                                "type": "table_row",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Cell value (short)",
                                                                "marks": [],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Cell value (short)",
                                                                "marks": [],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                    {
                                        "object": "block",
                                        "type": "table_cell",
                                        "data": {},
                                        "nodes": [
                                            {
                                                "object": "block",
                                                "type": "paragraph",
                                                "data": {},
                                                "nodes": [
                                                    {
                                                        "object": "text",
                                                        "leaves": [
                                                            {
                                                                "object": "leaf",
                                                                "text": "Cell value (short)",
                                                                "marks": [],
                                                            }
                                                        ],
                                                    }
                                                ],
                                            }
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [{"object": "leaf", "text": "", "marks": []}],
                            }
                        ],
                    },
                ],
            },
        },
        "historical_perspective": {
            "object": "value",
            "document": {
                "object": "document",
                "data": {},
                "nodes": [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "data": {},
                        "nodes": [
                            {
                                "object": "text",
                                "leaves": [
                                    {
                                        "object": "leaf",
                                        "text": "A historical perspective. We are now referencing ",
                                        "marks": [],
                                    }
                                ],
                            },
                            {
                                "object": "inline",
                                "type": "reference",
                                "data": {"id": 1, "name": "Example Reference"},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "ref",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            },
                            {
                                "object": "text",
                                "leaves": [{"object": "leaf", "text": "", "marks": []}],
                            },
                        ],
                    }
                ],
            },
        },
        "algorithm_input_variables": [
            {
                "name": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Input Var 1",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
                "long_name": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Input Variable 1",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
            },
            {
                "name": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Input Var 2",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
                "long_name": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Input variable that is quite long and should be wrapped over at least two lines but possible also three",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
                "unit": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Kelvins",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
            },
        ],
        "algorithm_output_variables": [
            {
                "name": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Output Var 1",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
                "long_name": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Output Variable 1",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
                "unit": {
                    "object": "value",
                    "document": {
                        "object": "document",
                        "data": {},
                        "nodes": [
                            {
                                "object": "block",
                                "type": "paragraph",
                                "data": {},
                                "nodes": [
                                    {
                                        "object": "text",
                                        "leaves": [
                                            {
                                                "object": "leaf",
                                                "text": "Kelvins",
                                                "marks": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    },
                },
            }
        ],
        "publication_references": [
            {
                "id": 1,
                "authors": "Charles Dickens,  John Steinbeck",
                "title": "Example Reference",
                "series": "A",
                "edition": "3rd",
                "volume": "42ml",
                "publication_place": "Boston",
                "issue": "ticket",
                "publisher": "PenguinBooks",
                "pages": "189-198",
                "isbn": 123456789,
                "year": 1995,
            }
        ],
    }
}
# endpoint = "https://nuo783m1th.execute-api.us-east-1.amazonaws.com"
# es_endpoint = "http://search-nasa-apt-lambda-dev-elastic-ze76i6s5yajg4kqzkanr2orzvy.us-east-1.es.amazonaws.com"
endpoint = "http://localhost:8000"
es_endpoint = "http://localhost:9200"


# atbd_alias = "test-atbd-2"

# r = re.post(
#     f"{endpoint}/atbds",
#     headers={"Authorization": f"Bearer {create_token()}"},
#     data=json.dumps({"title": "This is a title", "alias": f"{atbd_alias}"}),
# )
# r = re.post(
#     f"{endpoint}/atbds/{atbd_alias}/versions/v1.0",
#     headers={"Authorization": f"Bearer {create_token()}"},
#     data=json.dumps(atbd_data),
# )


# r = re.get(
#     f"{endpoint}/atbds/{atbd_alias}",
#     headers={"Authorization": f"Bearer {create_token()}"},
# )
# print("Updated version v1.0 with ATBD data")
# print(
#     f"Last Updated AT: {r.json()['last_updated_at']}, Last Updated BY: {r.json()['last_updated_by']}"
# )
# r = re.post(
#     f"{endpoint}/atbds/{atbd_alias}/versions/v1.0",
#     headers={"Authorization": f"Bearer {create_token()}"},
#     data=json.dumps({"doi": "http://updated_doi"}),
# )
# time.sleep(5)

# r = re.post(
#     f"{endpoint}/atbds/{atbd_alias}",
#     headers={"Authorization": f"Bearer {create_token()}"},
#     data=json.dumps({"title": "Updated Title"}),
# )

# r = re.get(
#     f"{endpoint}/atbds/{atbd_alias}",
#     headers={"Authorization": f"Bearer {create_token()}"},
# )

# print("Updated version v1.0 with")

# print(
#     f"Last Updated AT: {r.json()['last_updated_at']}, Last Updated BY: {r.json()['last_updated_by']}"
# )


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

# print(create_pg_connection_string())
print(create_token())
# r = re.get(
#     f"{endpoint}/atbds/1/versions/2/pdf?token={create_token()}",
#     # headers={"Authorization": f"Bearer {create_token()}"},
# )
# print(r.content)
# for chunk in r.iter_content()

