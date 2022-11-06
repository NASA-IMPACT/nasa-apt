""" Utility function that gets sections user input info """
import pydash


def get_section_info(document_section):

    
    # get user input
    section_info = pydash.get(obj=document_section,path='children.0.children.0.text')
    

    return section_info

def handle_lists(document_section):
    
    

    return