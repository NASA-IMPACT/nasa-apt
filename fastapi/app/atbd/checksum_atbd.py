from struct import pack
from hashlib import sha3_224 as hasher
from typing import Dict


def checksum_atbd(atbd_doc: Dict) -> str:
    """
    Checksum an atbd document for the purposes of the pdf cache index key. For simplicity, only checksum the alias,
    atbd_id and version_id. For published docs this is sufficient to identify a unique instance of an atbd doc
    across a series of edits (according to the business logic of the app).

    *** Note: do not use this for detecting errors or data integrity of the atbd doc itself! ***

    :param atbd_doc: atbd document
    :type atbd_doc: Dict
    :return: hex digest
    :rtype: str
    """
    atbd_id = atbd_doc['atbd_id']
    version_id = atbd_doc['atbd_version']
    alias = atbd_doc['atbd']['alias'] or ''
    checksum = hasher()
    checksum.update(pack('L', atbd_id))
    checksum.update(pack('L', version_id))
    checksum.update(alias.encode('utf8'))
    return checksum.hexdigest()
