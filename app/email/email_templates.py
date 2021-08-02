EMAIL_TEMPLATES = {
    "added_as_reviewer": {
        "subject": "Your review has been requested",
        "content": '<p>Hi $preferred_username,</p> <p>$app_user ($role) has requested your review on the following document: <a href="$atbd_version_link">$atbd_title, $atbd_version</a>.</p><p>Sincerely,</p><p>The APT Team</p>',
    },
    "added_as_author": {
        "subject": "You have been added as an author",
        "content": '<p>Hi $preferred_username,</p> <p>$app_user ($role) has added you as a collaborating author on the following document: <a href="$atbd_version_link">$atbd_title, $atbd_version</a>.</p><p>Sincerely,</p><p>The APT Team</p>',
    },
    "added_as_owner": {
        "subject": "You have been given ownership",
        "content": '<p>Hi $preferred_username,</p> <p>$app_user ($role) has transferred you ownership of the following document: <a href="$atbd_version_link">$atbd_title, $atbd_version</a>.</p><p>Sincerely,</p><p>The APT Team</p>',
    },
    "removed_as_owner": {
        "subject": "Your ownership has been removed",
        "content": '<p>Hi $preferred_username,</p> <p>$app_user ($role) has removed your ownership of the following document: <a href="$atbd_version_link">$atbd_title, $atbd_version</a>. You are now an author of this document.</p><p>Sincerely,</p><p>The APT Team</p>',
    },
}
