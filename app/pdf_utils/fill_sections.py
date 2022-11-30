""" Utility function that gets sections user input info """
import pydash


def get_section_user_text(document_content):
    """
    Utility function used in generator.py to get text input by user
    """

    # for each paragraph of user input in document content
    for indx, item in enumerate(document_content):
        # get user input
        section_user_text = pydash.get(obj=item, path=f"children.{indx}.children.text")

    return section_user_text


def get_paragraph_text(section_element):
    """
    Utility function used in generator.py to get text input by user
    """

    for _indx, paragraph in enumerate(section_element["children"]):

        section_p_text = pydash.get(obj=paragraph, path="text")

    return section_p_text
