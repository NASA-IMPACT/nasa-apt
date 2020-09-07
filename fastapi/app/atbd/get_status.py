from typing import Dict
from . import Status


def get_status(atbd_doc: Dict) -> Status:
    """
    Extract the Status from atbd json doc
    :param atbd_doc: json atbd doc
    :type atbd_doc: dict
    :return: status
    :rtype: Status enum
    """
    atbd_metadata = atbd_doc['atbd']
    [version] = atbd_metadata['atbd_versions']
    status: Status = version['status']
    return status
