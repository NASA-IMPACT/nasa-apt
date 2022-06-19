"""Access Control Lists (ACLs) for accessing/updating AtbdVersions and Contacts"""
from typing import Dict, List, Tuple

import fastapi_permissions

ATBD_VERSION_ACLS: Dict = {
    "owner": [
        {"action": "view"},
        {"action": "delete", "conditions": {"status": ["DRAFT"]}},
        {"action": "request_closed_review", "conditions": {"status": ["DRAFT"]}},
        {
            "action": "cancel_closed_review_request",
            "conditions": {
                "status": ["CLOSED_REVIEW_REQUESTED"],
            },
        },
        {"action": "request_publication", "conditions": {"status": ["OPEN_REVIEW"]}},
        {
            "action": "cancel_publication_request",
            "conditions": {"status": ["PUBLICATION_REQUESTED"]},
        },
        {"action": "create_new_version", "conditions": {"status": ["PUBLISHED"]}},
        {"action": "bump_minor_version", "conditions": {"status": ["PUBLISHED"]}},
        {
            "action": "update_journal_publication_status",
            "conditions": {
                "status": ["PUBLICATION", "PUBLISHED"],
            },
        },
        {"action": "update_journal_status"},
        {"action": "join_reviewers", "deny": True},
        {"action": "join_authors", "deny": True},
        {"action": "edit"},
        {"action": "offer_ownership"},
        # {
        #     "action": "update",
        #     "conditions": {
        #         "locked_by": [None],
        #         "status": [
        #             "DRAFT",
        #             "CLOSED_REVIEW_REQUESTED",
        #             "OPEN_REVIEW",
        #             "PUBLICATION_REQUESTED",
        #             "PUBLICATION",
        #             "PUBLISHED",
        #         ],
        #     },
        # },
        {
            "action": "secure_lock",
            "conditions": {
                "locked_by": [None],
                "status": [
                    "DRAFT",
                    "CLOSED_REVIEW_REQUESTED",
                    "OPEN_REVIEW",
                    "PUBLICATION_REQUESTED",
                    "PUBLICATION",
                    "PUBLISHED",
                ],
            },
        },
        {"action": "override_release_lock"},
        {"action": "invite_authors"},
        {"action": "view_owner"},
        {"action": "view_authors"},
        {"action": "view_curators"},
        {"action": "view_comments"},
        {"action": "comment"},
    ],
    "authors": [
        {"action": "join_reviewers", "deny": True},
        {"action": "view"},
        {"action": "comment"},
        {"action": "edit"},
        # {
        #     "action": "update",
        #     "conditions": {
        #         "locked_by": [None],
        #         "status": [
        #             "DRAFT",
        #             "CLOSED_REVIEW_REQUESTED",
        #             "OPEN_REVIEW",
        #             "PUBLICATION_REQUESTED",
        #             "PUBLICATION",
        #             "PUBLISHED",
        #         ],
        #     },
        # },
        {
            "action": "secure_lock",
            "conditions": {
                "locked_by": [None],
                "status": [
                    "DRAFT",
                    "CLOSED_REVIEW_REQUESTED",
                    "OPEN_REVIEW",
                    "PUBLICATION_REQUESTED",
                    "PUBLICATION",
                    "PUBLISHED",
                ],
            },
        },
        {"action": "override_release_lock"},
        {"action": "create_new_version", "conditions": {"status": ["PUBLISHED"]}},
        {"action": "bump_minor_version", "conditions": {"status": ["PUBLISHED"]}},
        {
            "action": "update_journal_publication_status",
            "conditions": {
                "status": ["PUBLICATION", "PUBLISHED"],
            },
        },
        {"action": "update_journal_status"},
        {"action": "view_owner"},
        {"action": "view_authors"},
        {"action": "view_curators"},
        {"action": "view_comments"},
        {"action": "comment"},
    ],
    "lock_owner": [
        # grant `secure_lock` to the lock owner to ensure idempotency of the
        # PUT /lock operation (lock owner should be able to request secure the
        # lock on an ATBD version lock they already own withour raising an
        # exception). The permissions will be granted sequentially, so
        # the lock_owner, who is also part of the "authors" or "owners" group
        # fill first be granted `secure_lock` only if the locked_by field is
        # None (which it isn't, since they've locked it), and then will be
        # granted `secure_lock`, as the lock owner
        {"action": "secure_lock"},
        {"action": "release_lock"},
        {
            "action": "update",
            "conditions": {
                "status": [
                    "DRAFT",
                    "CLOSED_REVIEW_REQUESTED",
                    "OPEN_REVIEW",
                    "PUBLICATION_REQUESTED",
                    "PUBLICATION",
                    "PUBLISHED",
                ],
            },
        },
    ],
    "reviewers": [
        {"action": "view"},
        {"action": "recieve_ownership", "deny": True},
        {"action": "join_authors", "deny": True},
        {"action": "comment"},
        {"action": "update_review_status", "conditions": {"status": ["CLOSED_REVIEW"]}},
        {"action": "view_owner"},
        {"action": "view_authors"},
        {"action": "view_reviewers"},
        {"action": "view_comments"},
        {"action": "view_curators"},
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
        {"action": "view_comments"},
        {"action": "comment"},
        {"action": "view"},
        {"action": "view_reviewers"},
        {"action": "view_authors"},
        {"action": "view_owner"},
        {"action": "view_curators"},
        {"action": "update"},
        {
            "action": "invite_reviewers",
            "conditions": {
                "status": [
                    "CLOSED_REVIEW_REQUESTED",
                    "CLOSED_REVIEW",
                    "OPEN_REVIEW",
                    "PUBLICATION_REQUESTED",
                    "PUBLICATION",
                    "PUBLISHED",
                ],
            },
        },
        {"action": "invite_authors"},
        {"action": "offer_ownership"},
        {"action": "delete"},
        {"action": "delete_thread"},
        {
            "action": "deny_closed_review_request",
            "conditions": {"status": ["CLOSED_REVIEW_REQUESTED"]},
        },
        {
            "action": "accept_closed_review_request",
            "conditions": {
                "status": ["CLOSED_REVIEW_REQUESTED"],
            },
        },
        {"action": "open_review", "conditions": {"status": ["CLOSED_REVIEW"]}},
        {
            "action": "deny_publication_request",
            "conditions": {"status": ["PUBLICATION_REQUESTED"]},
        },
        {
            "action": "accept_publication_request",
            "conditions": {"status": ["PUBLICATION_REQUESTED"]},
        },
        {"action": "publish", "conditions": {"status": ["PUBLICATION"]}},
    ],
    fastapi_permissions.Everyone: [
        {"action": "view", "conditions": {"status": ["PUBLISHED"]}}
    ],
}

CONTACT_ACLS: List[Tuple] = [
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "create_contact"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "list_contacts"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "get_contact"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "update_contact"),
    (fastapi_permissions.Allow, fastapi_permissions.Authenticated, "delete_contact"),
]

COMMENT_ACLS: Dict[str, List[Dict[str, str]]] = {
    "owner": [{"action": "update"}, {"action": "delete"}],
    "role:curator": [{"action": "update"}, {"action": "delete"}],
}

THREAD_ACLS: Dict[str, List[Dict[str, str]]] = {
    "owner": [{"action": "update"}, {"action": "delete"}],
    "role:curator": [{"action": "update"}, {"action": "delete"}],
}
