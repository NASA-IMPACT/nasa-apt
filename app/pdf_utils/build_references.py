"""
    This function helps handle references within generated PDFs
"""
from pylatex import NoEscape

from app.schemas import document


def bib_reference_name(reference_id: str) -> str:
    """
    Generates an identifier that can be used in the Latex document
    to generate a reference object
    """
    return f"ref{reference_id}"


def create_reference(reference_id: str) -> NoEscape:
    """
    Returns a Latex formatted refrerence object, wrapped with a
    NoEscape command to ensure the string gets processed as a
    command and not plain text.
    """

    return NoEscape(f"\\cite{{{bib_reference_name(reference_id)}}}")


def build_references(reference_dict: document.PublicationReference):
    """
    Processes a reference/citation item. Returns a text string
    """

    # print(reference_dict, "reference_dict used to generate bib reference")
    reference_id = bib_reference_name(reference_dict["id"])
    reference_id = reference_dict["id"]
    print(reference_id)  # TODO remove this. Only to resolve precommit errors

    # remove the id
    del reference_dict["id"]
    reference = ""

    for key, value in reference_dict.items():
        if not key:
            continue
        #  `series` gets changed to `journal` since `series` isn't a field used in
        # the `@article` citation type of `apacite`
        if key == "series":
            reference += f"journal={{{value}}},\n"
            continue
        if key == "authors":
            reference += f"author={{{value}}},\n"
            continue
        reference += f"{key}={{{value}}},\n"

    return f"@article{{\n{reference}}}"

    # Uncomment for debugging only
    # return NoEscape(create_reference(reference_id))
    # return NoEscape(f"@article{{{reference_id},\n{create_reference(reference_id)}}}")
