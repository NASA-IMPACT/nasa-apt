"""Access Control Lists (ACLs) for accessing/updating AtbdVersions and Contacts"""
from typing import Dict, List, Tuple

import fastapi_permissions

ATBD_VERSION_ACLS: Dict = {
    fastapi_permissions.Everyone: [
        {"action": "view", "status": "PUBLISHED"},
        {"action": "send_email"},
    ],
    "owner": [
        {"action": "view"},
        {"action": "delete", "status": ["DRAFT"]},
        {"action": "request_closed_review", "status": ["DRAFT"]},
        {
            "action": "cancel_closed_review_request",
            "status": ["CLOSED_REVIEW_REQUESTED"],
        },
        {"action": "request_publication", "status": ["OPEN_REVIEW"]},
        {"action": "cancel_publication_request", "status": ["PUBLICATION_REQUESTED"]},
        {"action": "create_new_version", "status": ["PUBLISHED"]},
        {"action": "bump_minor_version", "status": ["PUBLISHED"]},
        {"action": "update_journal_status", "status": ["PUBLISHED"]},
        {"action": "join_reviewers", "deny": True},
        {"action": "join_authors", "deny": True},
        {"action": "comment"},
        {"action": "edit"},
        {"action": "invite_authors"},
        {"action": "offer_ownership"},
        {
            "action": "update",
            "status": [
                "DRAFT",
                "CLOSED_REVIEW_REQUESTED",
                "OPEN_REVIEW",
                "PUBLICATION_REQUESTED",
                "PUBLICATION",
                "PUBLISHED",
            ],
        },
        {"action": "invite_authors"},
        {"action": "view_owner"},
        {"action": "view_authors"},
    ],
    "authors": [
        {"action": "join_reviewers", "deny": True},
        {"action": "view"},
        {"action": "comment"},
        {"action": "edit"},
        {
            "action": "update",
            "status": [
                "DRAFT",
                "CLOSED_REVIEW_REQUESTED",
                "OPEN_REVIEW",
                "PUBLICATION_REQUESTED",
                "PUBLICATION",
                "PUBLISHED",
            ],
        },
        {"action": "create_new_version", "status": ["PUBLISHED"]},
        {"action": "bump_minor_version", "status": ["PUBLISHED"]},
        {"action": "update_journal_status", "status": ["PUBLISHED"]},
        {"action": "view_owner"},
        {"action": "view_authors"},
    ],
    "reviewers": [
        {"action": "view"},
        {"action": "recieve_ownership", "deny": True},
        {"action": "join_authors", "deny": True},
        {"action": "comment"},
        {"action": "update_review_status", "status": ["CLOSED_REVIEW"]},
        {"action": "view_owner"},
        {"action": "view_authors"},
        {"action": "view_reviewers"},
    ],
    "role:contributor": [
        {"action": "receive_ownership"},
        {"action": "join_authors"},
        {"action": "join_reviewers"},
    ],
    "role:curator": [
        {"action": "receive_ownership", "deny": True},
        {"action": "join_authors", "deny": True},
        {"action": "join_reviewers", "deny": True},
        {"action": "comment"},
        {"action": "view"},
        {"action": "view_reviewers"},
        {"action": "view_authors"},
        {"action": "view_owner"},
        {"action": "update"},
        {
            "action": "invite_reviewers",
            "status": [
                "CLOSED_REVIEW_REQUESTED",
                "CLOSED_REVIEW",
                "OPEN_REVIEW",
                "PUBLICATION_REQUESTED",
                "PUBLICATION",
                "PUBLISHED",
            ],
        },
        {"action": "invite_authors"},
        {"action": "offer_ownership"},
        {"action": "delete"},
        {"action": "deny_closed_review_request", "status": ["CLOSED_REVIEW_REQUESTED"]},
        {
            "action": "accept_closed_review_request",
            "status": ["CLOSED_REVIEW_REQUESTED"],
        },
        {"action": "open_review", "status": ["CLOSED_REVIEW"]},
        {"action": "deny_publication_request", "status": ["PUBLICATION_REQUESTED"]},
        {"action": "accept_publication_request", "status": ["PUBLICATION_REQUESTED"]},
        {"action": "publish", "status": ["PUBLICATION"]},
    ],
}

CONTACT_ACLS: List[Tuple] = [
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "create_contact"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "list_contacts"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "get_contact"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "update_contact"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "delete_contact"),
]