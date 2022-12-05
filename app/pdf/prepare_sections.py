"""
Module prepares content for each PDF section. See function doc string below
"""
from typing import List

import pydash
from pylatex import Command

from app.pdf_utils import fill_contents


def prepare_sections(document_data, sections, atbd):
    """
    This module is used to prepare the SECTIONS dictionary with commands, title, and contents for the given section using document_data
    Expected output allows separation of formatting for each allowed type of content (paragraphs, lists, images, etc)
    Module's output pre-formats content, separating most formatting from PDf generation logic
    """
    # print(document_data,"THE DOCUMENT DATA")
    for section_name, info in sections.items():

        # get the entire List of Dicts from document data as section_content, default to empty dict
        document_content: List = pydash.get(
            obj=document_data, path=f"{section_name}.children", default={}
        )

        # update the sections info with contents
        info.update(
            {
                "contents": fill_contents.fill_contents(
                    document_content=document_content, atbd=atbd
                )
            }
        )

    return sections

    # expected output >>
    # return  {
    #     "abstract": {"contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "plain_summary": {"title": "Plain Language Summary", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "keywords": {"title": "Keywords", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "version_description": {"title": "Description", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "introduction": {"title": "Introduction", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "context_background": {
    #         "title": "Context / Background",
    #         "section_header": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "historical_perspective": {
    #         "title": "Historical Perspective",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "additional_information": {
    #         "title": "Additional Data",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "algorithm_description": {
    #         "title": "Algorithm Description",
    #         "section_header": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "scientific_theory": {
    #         "title": "Scientific Theory",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "scientific_theory_assumptions": {
    #         "title": "Scientific Theory Assumptions",
    #         "subsubsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "mathematical_theory": {
    #         "title": "Mathematical Theory",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "mathematical_theory_assumptions": {
    #         "title": "Mathematical Theory Assumptions",
    #         "subsubsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "algorithm_input_variables": {
    #         "title": "Algorithm Input Variables",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "algorithm_output_variables": {
    #         "title": "Algorithm Output Variables",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "algorithm_implementations": {"title": "Algorithm Availability", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "algorithm_usage_constraints": {
    #         "title": "Algorithm Usage Constraints",
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "performace_assessment_validations": {
    #         "title": "Performance Assessment Validation Methods",
    #         "section_header": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "performance_assessment_validation_methods": {
    #         "title": "Performance Assessment Validation Methods",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "performance_assessment_validation_uncertainties": {
    #         "title": "Performance Assessment Validation Uncertainties",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "performance_assessment_validation_errors": {
    #         "title": "Performance Assessment Validation Errors",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "data_access": {"title": "Data Access", "section_header": True, "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "data_access_input_data": {
    #         "title": "Input Data Access",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "data_access_output_data": {
    #         "title": "Output Data Access",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "data_access_related_urls": {
    #         "title": "Important Related URLs",
    #         "subsection": True,
    #         "contents": fill_contents(document_content=document_content,section_name=section_name),
    #     },
    #     "journal_discussion": {"title": "Discussion", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "journal_acknowledgements": {"title": "Acknowledgements", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    #     "data_availability": {"title": "Open Research", "contents": fill_contents(document_content=document_content,section_name=section_name)},
    # }
