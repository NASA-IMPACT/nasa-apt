""" Utility function that gets sections user input info """
import pydash
from pylatex import NoEscape, basic, utils

from app.schemas import document

TEXT_WRAPPERS = {
    # "superscript": lambda e: f"\\textsuperscript{{{e}}}",
    # "subscript": lambda e: f"\\textsubscript{{{e}}}",
    # # use the `\ul` command instead of the `\underline` as
    # # `\underline` "wraps" the argument in a horizontal box
    # # which doesn't allow for linebreaks
    # "underline": lambda e: f"\\ul{{{e}}}",
    # "italic": lambda e: f"\\textit{{{e}}}",
    # "bold": lambda e: f"\\textbf{{{e}}}",
    "superscript": lambda e: f"\\textsuperscript{{{e}}}",
    "subscript": lambda e: f"\\textsubscript{{{e}}}",
    # use the `\ul` command instead of the `\underline` as
    # `\underline` "wraps" the argument in a horizontal box
    # which doesn't allow for linebreaks
    "underline": lambda e: f"\\ul{{{e}}}",
    "italic": lambda e: utils.italic(e, escape=False),
    "bold": lambda e: utils.bold(e, escape=False),
}


def bib_reference_name(reference_id: str) -> str:
    """
    Generates an identifier that can be used in the Latex document
    to generate a reference object
    """
    return f"ref{reference_id}"


def reference(reference_id: str) -> NoEscape:
    """
    Returns a Latex formatted refrerence object, wrapped with a
    NoEscape command to ensure the string gets processed as a
    command and not plain text.
    """

    return NoEscape(f"\\cite{{{bib_reference_name(reference_id)}}}")


def wrap_text(data: document.TextLeaf) -> NoEscape:
    """
    Wraps text item with Latex commands corresponding to the sibbling elements
    of the text item. Allows for wrapping multiple formatting options.
    ----
    eg: if data looks like: {"bold": true, "italic": true, "text": "text to format" }
    then `wrap_text(data)` will return: `\\bold{\\italic{text to format}}`

    """
    e = utils.escape_latex(data["text"])
    # e = data["text"]

    for option, command in TEXT_WRAPPERS.items():
        if data.get(option) and e.strip(" ") != "":
            e = command(e)

    return NoEscape(e)


def get_reference_ids(text_element: list):
    """
    Checks for the "type" key with a value of "ref",
    Appends the corresponding "refId" value to a new list or variable.
    Formats the reference items with helper functions
    """

    ref_ids = [item["refId"] for item in text_element if item.get("type") == "ref"]

    x = []
    for item in ref_ids:
        x.append(reference(item))

    return x


def get_paragraph_text(section_element):
    """
    Utility function used in generator.py to get text input by user
    """
    for _indx, text_leaf in enumerate(section_element["children"]):

        # check if the text_leaf has the path text
        section_p_text = pydash.get(obj=text_leaf, path="text")

        if len(section_element["children"]) > 1:

            # use child as a "counter"
            for child in section_element["children"]:

                # if we have type 'ref', get the reference id and process reference
                child_type = pydash.get(obj=child, path="type")

                # get reference text from text_leaf
                ref_text = pydash.get(obj=text_leaf, path="text")

                # if we have type 'ref', get the reference id and process reference(s), checking for multiple references
                if child_type == "ref":

                    ref_ids: list = get_reference_ids(section_element["children"])

                    # join the formatted references as a single string
                    ids_ = " ".join(str(i) for i in ref_ids)

                    # return reference text and bibliography refs
                    return NoEscape(f"{ref_text} {ids_}")

        # use functions in TEXT_WRAPPERS to format text
        for option, _command in TEXT_WRAPPERS.items():

            # if the option in text_leaf is true
            if text_leaf.get(option):
                # run functions in text_wrappers
                section_p_text = wrap_text(text_leaf)

        return section_p_text
