"""
    This module handles the processing of images and captions in generated PDFs
"""
from typing import Dict, List, Union

import botocore
import pydash
from pylatex import Figure, NoEscape, escape_latex

from app.api.utils import s3_client
from app.config import S3_BUCKET
from app.pdf import error_handler
from app.schemas import document

TEXT_WRAPPERS = {
    "superscript": lambda e: f"\\textsuperscript{{{e}}}",
    "subscript": lambda e: f"\\textsubscript{{{e}}}",
    # use the `\ul` command instead of the `\underline` as
    # `\underline` "wraps" the argument in a horizontal box
    # which doesn't allow for linebreaks
    "underline": lambda e: f"\\ul{{{e}}}",
    "italic": lambda e: f"\\textit{{{e}}}",
    "bold": lambda e: f"\\textbf{{{e}}}",
}


def wrap_caption_text(data: Dict) -> NoEscape:
    """
    Wraps text item with Latex commands corresponding to the sibbling elements
    of the text item. Allows for wrapping multiple formatting options.
    ----
    eg: if data looks like: {"bold": true, "italic": true, "text": "text to format" }
    then `wrap_caption_text(data)` will return: `\\bold{\\italic{text to format}}`

    """
    # pull caption text
    caption_text = data["text"]

    # escape caption text
    caption_text = escape_latex(caption_text)

    # process command for each option if found in caption textleaf (data)
    for option, command in TEXT_WRAPPERS.items():

        # TODO ensure this logic is applying correctly
        if (data[option] is True) and (caption_text.strip(" ") != ""):

            # run the command for the data attributes that are true
            caption_text = command(caption_text)

    return NoEscape(caption_text)


PLACEHOLDER_OBJECT_KEY = "No Image Found"
PLACEHOLDER_CAPTION = "No Caption Provided"


def process_image_caption(caption_text_leaf: Dict) -> List[NoEscape]:
    """
    Uses a modified text processing logic to process image captions
    """

    # pass to wraptext/caption format util
    processed_caption = NoEscape(wrap_caption_text(caption_text_leaf))

    return processed_caption


def process_image(
    data: Dict,
    atbd_id: int = None,
):
    """
    Top level processing of each of the possible section items: subsection, image,
    table, generic div-type node, ordered and unordered list, and equation.

    Returns Latex formatted object for each of these, to be appeneded to the
    Latex document.
    """

    # data is a Dict
    for _indx, element in enumerate(data["children"]):  # type: ignore
        # source for type ignore: https://github.com/python/mypy/issues/2220
        # data['children']: List
        # _indx: int
        # element: Dict

        # if content type is img
        if element["type"] == "img":

            # get the image block info: objectKey
            # maintain camelCase
            objectKey = pydash.get(
                obj=element, path="objectKey", default=PLACEHOLDER_OBJECT_KEY
            )

        # get the image block info: caption
        if element["type"] == "caption":

            # get the caption text leaf
            caption_text_leaf: Dict = pydash.get(
                obj=element, path="children.0", default=PLACEHOLDER_CAPTION
            )

        # handle errors and try to provide useful feedback during image load failure
        try:
            # lambda execution environment only allows for files to
            # written to `/tmp` directory
            # print(f"DOWNLOADING objectKey{objectKey} FROM S3....")

            s3_client().download_file(
                Bucket=S3_BUCKET,
                Key=f"{atbd_id}/images/{objectKey}",
                Filename=f"/tmp/{objectKey}",
            )

            figure = Figure(position="H")
            figure.add_image(f"/tmp/{objectKey}")

            # TODO debug captions
            figure.add_caption(NoEscape(process_image_caption(caption_text_leaf)))

        # if image is not found, return a placeholder text
        except botocore.exceptions.ClientError:
            return PLACEHOLDER_OBJECT_KEY

        except Exception as e:
            # TODO, DRY out and reference these correct values
            error_handler.generate_html_content_for_error(
                error=e,
                return_link="",
                atbd_id="",
                atbd_title="",
                atbd_version="",
                pdf_type="",
            )
        else:
            return figure
