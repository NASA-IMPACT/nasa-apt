from string import Template
from typing import List, Mapping, Optional, TypedDict, Dict, Any

from app import config
from app.api.utils import ses_client
from app.db.models import AtbdVersions
from app.email.email_templates import EMAIL_TEMPLATES
from app.schemas.users import CognitoUser
from app.users import cognito


class UserToNotify(TypedDict):
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

    app_users, _ = cognito.list_cognito_users()

    users_to_notify = [
        UserToNotify(
            **app_users[atbd_version.owner].dict(), notification=notification, data=data
        )  # type: ignore
    ]

    users_to_notify.extend(
        [
            UserToNotify(**app_users[author].dict(), notification=notification, data=data)  # type: ignore
            for author in atbd_version.authors
        ]
    )
    users_to_notify.extend(
        [
            UserToNotify(
                **app_users[reviewer["sub"]].dict(),
                notification=notification,
                data=data,
            )  # type: ignore
            for reviewer in atbd_version.reviewers
        ]
    )
    return notify_users(
        users_to_notify=users_to_notify,
        atbd_title=atbd_title,
        atbd_id=atbd_id,
        atbd_version=f"v{atbd_version.major}.{atbd_version.minor}",
        user=user,
    )


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
