""" Utility function that gets sections user input info """
import pydash
from pylatex import NoEscape

# def get_section_user_text(document_content):
#     """
#     Utility function used in generator.py to get text input by user
#     """

#     # for each paragraph of user input in document content
#     for indx, item in enumerate(document_content):
#         # get user input
#         section_user_text = pydash.get(obj=item, path=f"children.{indx}.children.text")

#     return section_user_text


def bib_reference_name(reference_id: str) -> str:
    """
    Generates an identifier that can be used in the Latex document
    to generate a reference object
    """
    return f"ref{reference_id}"


def reference(reference_id: str) -> NoEscape:
    """
    Returns a Latex formatted refrerence object, wrapped with a
    NoEscape command to ensure the string gets processed as a
    command and not plain text.
    """

    return NoEscape(f"\\cite{{{bib_reference_name(reference_id)}}}")


def yield_text(paragraph):
    """
    WIP: Generator type that may be used to handle paragraph text logic
    """
    section_p_text = pydash.get(obj=paragraph, path="text")
    yield section_p_text


def get_paragraph_text(section_element):
    """
    Utility function used in generator.py to get text input by user
    """
    for indx, paragraph in enumerate(section_element["children"]):
        # TODO DRY this logic

        # check if the paragraph has the path text
        # if so get text

        section_p_text = pydash.get(obj=paragraph, path="text")

        # TODO get line breaks i.e. type='p', children.0.text = ''

        # check if the paragraph has type 'ref'
        paragraph_type = pydash.get(obj=paragraph, path="type")

        # if we have type 'ref', get the reference id and process reference
        if paragraph_type == "ref":

            refId = pydash.get(obj=paragraph, path="refId")

            # we will return the reference content if encountered
            return reference(refId)

    return section_p_text
