"""Email notifications module"""
import json
import os
from string import Template
from typing import Any, Dict, List, Mapping, Optional

from app import config
from app.api.utils import ses_client
from app.db.models import AtbdVersions
from app.schemas.users import CognitoUser
from app.users import cognito

dir_path = os.path.dirname(os.path.realpath(__file__))
EMAIL_TEMPLATES = json.load(open(os.path.join(dir_path, "email_templates.json"), "r"))


class UserNotification(Dict):
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

    mentioned_users = data.get("notify") or []
    recipient_user_ids = []
    # If users are mentioned
    if len(mentioned_users) > 0:
        recipient_user_ids.extend(
            [
                user_sub
                for user_sub in mentioned_users
                # Skip curators
                if user_sub != "curators"
            ]
        )

        # If curator exists
        if "curators" in mentioned_users:
            recipient_user_ids.extend(
                [
                    user_id
                    for (user_id, user) in app_users.items()
                    if "curator" in user.cognito_groups
                ]
            )
    else:
        recipient_user_ids.append(atbd_version.owner)
        recipient_user_ids.extend(atbd_version.authors)
        recipient_user_ids.extend(atbd_version.reviewers)
    recipient_user_ids_set = set(recipient_user_ids)
    del recipient_user_ids
    # Remove current user from the list
    if user.sub in recipient_user_ids_set:
        recipient_user_ids_set.remove(user.sub)
    return notify_users(
        user_notifications=[
            UserNotification(
                **app_users[user_id].dict(),
                notification=notification,
                data=data,
            )
            for user_id in recipient_user_ids_set
        ],
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

        subject_t = Template(message["subject"])
        body_t = Template(message["content"])

        template_kwargs = dict(
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
        subject_content = subject_t.substitute(**template_kwargs)
        body_content = body_t.substitute(**template_kwargs)

        ses_client().send_email(
            Source=config.NOTIFICATIONS_FROM,
            Destination={"ToAddresses": [user_to_notify["email"]]},
            Message={
                "Subject": {"Data": subject_content},
                "Body": {"Html": {"Data": body_content}},
            },
        )
