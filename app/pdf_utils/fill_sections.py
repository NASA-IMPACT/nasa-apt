""" Utility function that gets sections user input info """
import pydash

def get_section_user_text(document_content):
    """
    Utility function used in generator.py to get text input by user
    """
    # for each paragraph of user input in document content
    for indx,item in enumerate(document_content):
        # get user input
        section_user_text = pydash.get(
            obj=item, path=f"children.0.text"
        )

    return section_user_text