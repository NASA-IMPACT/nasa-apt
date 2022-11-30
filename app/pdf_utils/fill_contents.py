"""
    Module fills contents of document for each section of PDF generation
"""
from typing import List

import pydash
from pylatex import NoEscape, Subsubsection

from app.pdf_utils import (
    fill_sections,
    format_equation,
    image_handler,
    process_lists,
    process_table,
)


def fill_contents(document_content: List, atbd):
    """
    This function returns a list of formatted contents for a section of the PDF document to be generated
    Contents are then added in order to the PDF during generation
    """
    # list will be appended with ordered contents
    contents = []

    # check the content type, of each item in document_content List
    for indx, element in enumerate(document_content):

        # check for the contents' type
        content_type: str = pydash.get(obj=document_content, path=f"{indx}.type")

        # apply logic for each content type, append to document in order
        if content_type == "p":

            text_element = fill_sections.get_paragraph_text(element)

            contents.append(text_element)
            # check for references in paragraph
            # reference = TODO

            # check for equations in paragraph
            # equation = TODO

        # check for sub-section
        if content_type == "sub-section":

            sub_section_title = pydash.get(obj=element, path="children.0.text")

            sub_section = Subsubsection(
                NoEscape(f"\\normalfont{{\\itshape{{{sub_section_title}}}}}"),
                numbering=False,
            )

            contents.append(sub_section)

        # process image type content
        if content_type == "image-block":

            # append image
            contents.append(image_handler.process_image(data=element, atbd_id=atbd.id))

        if content_type in ["ul", "ol"]:

            contents.append(process_lists.ul_ol_lists(element))

        if content_type == "equation":

            contents.append(format_equation.format(element))

        # TODO process table blocks
        # if content_type == "table-block":
        #     print(f"""CONTENT_TYPE: table-block
        #         \n
        #         {element}
        #     """)
        #     doc.append(
        #         process_table.process_table(element)
        #     )
        #     pass

        # append to list

        # return the contents for that section

    return contents
