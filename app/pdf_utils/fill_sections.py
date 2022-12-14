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
    "italic": lambda e: utils.italic(e, escape=True),
    "bold": lambda e: utils.bold(e, escape=True),
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


def yield_text(paragraph):
    """
    Work in Progress: Generator type that may be used to handle paragraph text logic
    """
    section_p_text = pydash.get(obj=paragraph, path="text")
    yield section_p_text

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


def get_paragraph_text(section_element):
    """
    Utility function used in generator.py to get text input by user
    """
    for _indx, paragraph in enumerate(section_element["children"]):


        # check if the paragraph has the path text
        # if so get text
        section_p_text = pydash.get(obj=paragraph, path="text")

        # TODO get line breaks i.e. type='p', children.0.text = ''

        # check if the paragraph has type 'ref'
        paragraph_type = pydash.get(obj=paragraph, path="type")

        # if we have type 'ref', get the reference id and process reference
        if paragraph_type == "ref":

            refId = pydash.get(obj=paragraph, path="refId")

            # we will return the reference content if encountered
            return reference(refId)

        # TODO allow inline text formatting
        # isolate full text leaf element
        text_leaf = paragraph
        # use functions in TEXT_WRAPPERS to format text
        for option, command in TEXT_WRAPPERS.items():

            # if the option in text_leaf is true
            if text_leaf[option]:
                # if text_leaf.get(option) and e.strip(" ") != "":
                # section_p_text = section_p_text.strip(" ") if section_p_text.strip(" ") != "" else section_p_text

                # run functions in text_wrappers
                section_p_text = command(section_p_text)

                # # escape latex
                # section_p_text = utils.escape_latex(section_p_text)
                # section_p_text = NoEscape(section_p_text)
                section_p_text = wrap_text(text_leaf)

        return section_p_text
