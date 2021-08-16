"""Email notifications module"""
import json
import os
from string import Template
from typing import Any, Dict, List, Mapping, Optional, TypedDict

from app import config
from app.api.utils import ses_client
from app.db.models import AtbdVersions
from app.schemas.users import CognitoUser
from app.users import cognito

dir_path = os.path.dirname(os.path.realpath(__file__))
EMAIL_TEMPLATES = json.load(open(os.path.join(dir_path, "email_templates.json"), "r"))


# TODO: use an enum for notification
class UserNotification(TypedDict):
    """Object representing a notification to be sent to an app user"""

    email: str
    preferred_username: str
    notification: str
    data: Optional[Mapping[str, object]]


def notify_atbd_version_contributors(
    atbd_version: AtbdVersions,
    notification: str,
    atbd_title: str,
    atbd_id: int,
    user: CognitoUser,
    data: Dict[str, Any] = {},
):
    """
    Sends the same notifications to all users (owner, author, reviewers) of an atbd
    """
    app_users, _ = cognito.list_cognito_users()

    user_notifications = [
        UserNotification(
            **app_users[atbd_version.owner].dict(),
            notification=notification,
            data=data,
        )  # type: ignore
    ]

    user_notifications.extend(
        [
            UserNotification(
                **app_users[author].dict(), notification=notification, data=data  # type: ignore
            )
            for author in atbd_version.authors
        ]
    )
    user_notifications.extend(
        [
            UserNotification(
                **app_users[reviewer["sub"]].dict(),
                notification=notification,
                data=data,
            )  # type: ignore
            for reviewer in atbd_version.reviewers
        ]
    )
    return notify_users(
        user_notifications=user_notifications,
        atbd_title=atbd_title,
        atbd_id=atbd_id,
        atbd_version=f"v{atbd_version.major}.{atbd_version.minor}",
        user=user,
    )


def notify_users(
    user_notifications: List[UserNotification],
    atbd_title: str,
    atbd_id: int,
    atbd_version: str,
    user: CognitoUser,
):
    """
    Executes a series of notifications. Each notification in the `user_notifications`
    object can have a different notifications as some events generate different notifications
    for different users (Eg: when transfering ownership the owner is notified that their
    ownership of the document has been removed and the new owner is notified that they have
    been granted ownership)
    """
    for user_to_notify in user_notifications:

        message = EMAIL_TEMPLATES[user_to_notify["notification"]]

        t = Template(message["content"])

        message_content = t.substitute(
            # User performing the action:
            app_user=user.preferred_username,
            role=" ".join(user.cognito_groups),
            # User being notified:
            preferred_username=user_to_notify["preferred_username"],
            atbd_title=atbd_title,
            atbd_version=atbd_version,
            atbd_version_link=f"{config.FRONTEND_URL}/documents/{atbd_id}/{atbd_version}",
            **user_to_notify.get("data", {}),
        )

        ses_client().send_email(
            Source=config.NOTIFICATIONS_FROM,
            Destination={"ToAddresses": [user_to_notify["email"]]},
            Message={
                "Subject": {"Data": message["subject"]},
                "Body": {"Html": {"Data": message_content}},
            },
        )
