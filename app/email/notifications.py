from string import Template
from typing import List, Mapping, TypedDict

from moto.ses import ses_backend

from app import config
from app.api.utils import ses_client
from app.email.email_templates import EMAIL_TEMPLATES
from app.schemas.users import CognitoUser


class UserToNotify(TypedDict):
    email: str
    preferred_username: str
    notification: str
    data: Mapping[str, object]


def notify_users(
    users_to_notify: List[UserToNotify],
    atbd_title: str,
    atbd_id: int,
    atbd_version: str,
    user: CognitoUser,
):
    for app_user in users_to_notify:

        message = EMAIL_TEMPLATES[app_user["notification"]]

        t = Template(message["content"])

        message_content = t.substitute(
            # User performing the action:
            app_user=user.preferred_username,
            role=f"{' '.join(user.cognito_groups)}",
            # User being notified:
            preferred_username=app_user["preferred_username"],
            atbd_title=atbd_title,
            atbd_version=atbd_version,
            atbd_version_link=f"{config.FRONTEND_URL}/documents/{atbd_id}/{atbd_version}",
            **app_user.get("data", {}),
        )

        ses_client().send_email(
            Source="no-reply@ds.io",
            Destination={"ToAddresses": [app_user["email"]]},
            Message={
                "Subject": {"Data": message["subject"]},
                "Body": {"Html": {"Data": message_content}},
            },
        )

    print("MESSAGES: ", ses_backend.sent_messages)
