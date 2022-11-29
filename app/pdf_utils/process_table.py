"""
    Module to handle processing of table elements
"""
import pandas as pd
from pylatex import NoEscape, utils

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


def wrap_caption(caption_text):
    """
    Uses a standard text processing logic to process table captions
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
    processed_caption = NoEscape(wrap_text(caption_text))

    return processed_caption


def wrap_text(data: document.TextLeaf) -> NoEscape:
    """
    Wraps text item with Latex commands corresponding to the sibbling elements
    of the text item. Allows for wrapping multiple formatting options.
    ----
    eg: if data looks like: {"bold": true, "italic": true, "text": "text to format" }
    then `wrap_text(data)` will return: `\\bold{\\italic{text to format}}`

    """
    # e = utils.escape_latex(data["text"])
    print(data, "DATA IN WRAP TEXT")
    e = utils.escape_latex(data)
    # e = data["text"]

    for option, command in TEXT_WRAPPERS.items():
        if data.get(option) and e.strip(" ") != "":
            e = command(e)

    return NoEscape(e)


def build_table(data: document.TableNode, caption: str) -> NoEscape:
    """
    Returns a Latex formatted Table Item, wrapped with a NoEscape Command
    """
    print(data, "TABLE IN BUILD TABLE")
    rows = [
        tuple(
            " ".join(wrap_text(c) for c in table_cell["children"])
            # " ".join(c for c in table_cell["children"])
            for table_cell in table_row["children"]
        )
        for table_row in data["children"]
    ]

    dataframe = pd.DataFrame(rows[1:], columns=rows[0])

    pd.set_option("max_colwidth", None)
    latex_table = dataframe.to_latex(
        index=False,
        escape=False,
        na_rep=" ",
        column_format="".join([f"p{{{1/len(rows[0])}\\linewidth}}" for _ in rows[0]]),
        caption=caption,
        position="H",
        longtable=True,
    )

    return NoEscape(latex_table)


def process_table(data):
    """
    Function to handle processing of table elements
    """
    [table] = filter(lambda d: d["type"] == "table", data["children"])
    [caption] = filter(lambda d: d["type"] == "caption", data["children"])
    print(data, "DATA COMING INTO PROCESS TABLE")
    # caption = NoEscape(
    #     " ".join(d for d in wrap_text(caption["children"]))
    # )
    caption = NoEscape(wrap_caption(item for item in caption["children"]))
    return build_table(table, caption=caption)
