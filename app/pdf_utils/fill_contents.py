"""
    Module fills contents of document for each section of PDF generation
"""
import types
from typing import List

import pydash
from pylatex import LineBreak, NewLine, NoEscape, Subsubsection, basic, utils

from app.pdf_utils import (  # process_reference,
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

            if text_element != "":

                contents.append(text_element)

            else:
                continue

            # if d.get("type") == "a":
            #     result.append(hyperlink(d["url"], d["children"][0]["text"]))

        # Sub Sections
        if content_type == "sub-section":

            sub_section_title = pydash.get(obj=element, path="children.0.text")

            sub_section = Subsubsection(
                NoEscape(f"\\normalfont{{\\itshape{{{sub_section_title}}}}}"),
                numbering=False,
            )

            contents.append(sub_section)

        # Image Blocks
        if content_type == "image-block":

            contents.append(image_handler.process_image(data=element, atbd_id=atbd.id))

        # Lists
        if content_type in ["ul", "ol"]:

            contents.append(process_lists.ul_ol_lists(element))

        # Equations
        if content_type == "equation":

            contents.append(format_equation.format(element))

        # Table Blocks
        if content_type == "table-block":

            contents.append(process_table.process_table(element))

    # returns the contents for the section
    return contents
