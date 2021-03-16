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
r = re.post(
    f"{endpoint}/atbds/{atbd_alias}/versions/v1.0",
    headers={"Authorization": f"Bearer {create_token()}"},
    data=json.dumps(
        {
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
                                        "leaves": [
                                            {"text": "A line of text in a paragraph."}
                                        ],
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
                                        "leaves": [
                                            {"object": "leaf", "text": "", "marks": []}
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
                                        "leaves": [
                                            {"object": "leaf", "text": "", "marks": []}
                                        ],
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
                                        "leaves": [
                                            {"object": "leaf", "text": "", "marks": []}
                                        ],
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
                                        "leaves": [
                                            {"object": "leaf", "text": "", "marks": []}
                                        ],
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
                        "publication_reference_id": 1,
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
    ),
)
# r = re.post(
#     f"{endpoint}/atbds/{atbd_alias}",
#     data=json.dumps({"title": "A new title 2"}),
#     headers={"Authorization": f"Bearer {create_token()}"},
# )
print(r.content)
r = re.get(
    f"{endpoint}/atbds/{atbd_alias}/versions/v1.0",
    headers={"Authorization": f"Bearer {create_token()}"},
)
print(r.content)

