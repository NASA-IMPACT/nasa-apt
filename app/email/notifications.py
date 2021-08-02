from string import Template
from typing import List, TypedDict

from app import config
from app.api.utils import ses_client
from app.email.email_templates import EMAIL_TEMPLATES
from app.schemas.users import User


class UserToNotify(TypedDict):
    email: str
    preferred_username: str
    notification: str


def notify_users(
    users_to_notify: List[UserToNotify],
    app_user: User,
    atbd_title: str,
    atbd_id: int,
    atbd_version: str,
):
    for user in users_to_notify:

        message = EMAIL_TEMPLATES[user["notification"]]

        t = Template(message["content"])

        print("APP USER: ", app_user)

        message_content = t.substitute(
            # User performing the action:
            app_user=app_user["preferred_username"],
            role=app_user["cognito:groups"][0],
            # User being notified:
            preferred_username=user["preferred_username"],
            atbd_title=atbd_title,
            atbd_version=atbd_version,
            atbd_version_link=f"{config.FRONTEND_URL}/documents/{atbd_id}/{atbd_version}",
        )

        ses_client().send_email(
            Source="no-reply@ds.io",
            Destination={"ToAddresses": [user["email"]]},
            Message={
                "Subject": {"Data": message["subject"]},
                "Body": {"Html": {"Data": message_content}},
            },
        )
