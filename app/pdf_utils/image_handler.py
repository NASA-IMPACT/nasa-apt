"""
    This module handles the processing of images and captions in generated PDFs
"""
from typing import List, Union

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


def wrap_text(data: document.TextLeaf) -> NoEscape:
    """
    Wraps text item with Latex commands corresponding to the sibbling elements
    of the text item. Allows for wrapping multiple formatting options.
    ----
    eg: if data looks like: {"bold": true, "italic": true, "text": "text to format" }
    then `wrap_text(data)` will return: `\\bold{\\italic{text to format}}`

    """
    e = escape_latex(data["text"])
    # e = data["text"]

    for option, command in TEXT_WRAPPERS.items():
        if data.get(option) and e.strip(" ") != "":
            e = command(e)

    return NoEscape(e)


PLACEHOLDER_OBJECT_KEY = "PLACEHOLDER_OBJECT_KEY"
PLACEHOLDER_CAPTION = "PLACEHOLDER_CAPTION"


def process_image_caption(
    caption_text: Union[
        document.TextLeaf,
        document.ReferenceNode,
        document.LinkNode,
        document.EquationInlineNode,
    ]
) -> List[NoEscape]:
    """
    Uses a standard text processing logic to process image captions
    """

    # TODO revisit typing and text formatting
    caption_text_leaf = {
        "text": caption_text,
        "underline": False,
        "italic": False,
        "bold": False,
        "subscript": False,
        "superscript": False,
    }
    # generate and validate textleaf type
    caption_text_leaf = document.TextLeaf(**caption_text_leaf)

    # pass to wraptext/caption format util
    processed_caption = NoEscape(wrap_text(caption_text_leaf))

    return processed_caption


def process_image(
    data: List,
    atbd_id: int = None,
):
    """
    Top level processing of each of the possible section items: subsection, image,
    table, generic div-type node, ordered and unordered list, and equation.

    Returns Latex formatted object for each of these, to be appeneded to the
    Latex document.
    """
    print(data, "THIS DATA IS PASSED TO PROCESS IMAGE")
    # data is a list
    for _indx, element in enumerate(data["children"]):  # type: ignore
        # source for type ignore: https://github.com/python/mypy/issues/2220
        # _indx: int
        # element: Dict

        # if content type is img
        if element["type"] == "img":
            print("Processing the image in image handler")
            # get the image block info: objectKey
            # maintain camelCase
            objectKey = pydash.get(
                obj=element, path="objectKey", default=f"{PLACEHOLDER_OBJECT_KEY}"
            )

            # TODO, debug captions
            # get the image block info: caption
            # caption_text = pydash.get(
            #     obj=element, path="children.0.text", default=f"{PLACEHOLDER_CAPTION}"
            # )

            # handle errors and try to provide useful feedback during image load failure
            try:
                # lambda execution environment only allows for files to
                # written to `/tmp` directory
                print(f"DOWNLOADING objectKey{objectKey} FROM S3....")
                try:
                    s3_client().download_file(
                        Bucket=S3_BUCKET,
                        Key=f"{atbd_id}/images/{objectKey}",
                        Filename=f"/tmp/{objectKey}",
                    )

                    figure = Figure(position="H")
                    figure.add_image(f"/tmp/{objectKey}")
                    print(figure, "THE FIGURE AFTER DOWNLOAD FROM S3 ")
                    # TODO debug captions
                    # figure.add_caption(
                    #     NoEscape(
                    #         process_image_caption(caption_text))
                    #     )
                except Exception as e:
                    raise e

                return figure

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
