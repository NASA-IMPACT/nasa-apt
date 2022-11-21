""" Utility function that gets sections user input info """
import pydash


def get_section_user_text(document_section):
    """
    Utility function used in generator.py to get text input by user
    """
    # get user input
    section_user_text = pydash.get(
        obj=document_section, path="children.0.children.0.text"
    )

    return section_user_text


def handle_lists(document_section):
    """
    Utility function in process for refactor
    """
    return
