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
    "ownership_revoked": {
        "subject": "Your ownership has been revoked",
        "content": '<p>Hi $preferred_username,</p> <p>$app_user ($role) has transferred your ownership of the following document: <a href="$atbd_version_link">$atbd_title, $atbd_version</a> to $transferred_to. You have been added as an author of the document.</p><p>Sincerely,</p><p>The APT Team</p>',
    },
    "new_thread_created": {
        "subject": "A new thread has been created",
        "content": '<p>Hi $preferred_username,</p> <p>$created_by has transferred your ownership of the following document: <a href="$atbd_version_link">$atbd_title, $atbd_version</a> to $transferred_to. You have been added as an author of the document.</p><p>Sincerely,</p><p>The APT Team</p>',
    },
}
