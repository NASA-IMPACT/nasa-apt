"""
PDF generation code for ATBD Documents
"""
import os
import pathlib
from typing import Any, List, Union

import pandas as pd
from pylatex import (
    Command,
    Document,
    Enumerate,
    Figure,
    Itemize,
    Math,
    NoEscape,
    Package,
    Section,
    Subsection,
    Subsubsection,
    section,
    utils,
)

from app.api.utils import s3_client
from app.config import S3_BUCKET
from app.db.models import Atbds
from app.schemas import document
from app.schemas.versions_contacts import ContactsLinkOutput

SECTIONS = {
    "introduction": {"title": "Introduction"},
    "historical_perspective": {"title": "Historical Perspective"},
    "algorithm_description": {"title": "Algorithm Description"},
    "scientific_theory": {"title": "Scientific Theory", "subsection": True},
    "scientific_theory_assumptions": {
        "title": "Scientific Theory Assumptions",
        "subsection": True,
    },
    "mathematical_theory": {"title": "Mathematical Theory", "subsection": True},
    "mathematical_theory_assumptions": {
        "title": "Mathematical Theory Assumptions",
        "subsection": True,
    },
    "algorithm_input_variables": {
        "title": "Algorithm Input Variables",
        "subsection": True,
    },
    "algorithm_output_variables": {
        "title": "Algorithm Output Variables",
        "subsection": True,
    },
    "algorithm_implementations": {"title": "Algorithm Implementations"},
    "algorithm_usage_constraints": {"title": "Algorithm Usage Constraints"},
    "performance_assessment_validation_methods": {
        "title": "Performance Assessment Validation Methods"
    },
    "performance_assessment_validation_uncertainties": {
        "title": "Performance Assessment Validation Uncertainties"
    },
    "performance_assessment_validation_errors": {
        "title": "Performance Assessment Validation Errors"
    },
    "data_access_input_data": {"title": "Data Access Input Data"},
    "data_access_output_data": {"title": "Data Access Output Data"},
    "data_access_related_urls": {"title": "Data Access Related URLs"},
    "journal_dicsussion": {"title": "Discussion"},
    "journal_acknowledgements": {"title": "Acknowledgements"},
    "contacts": {"title": "Contacts"},
}


CONTENT_UNAVAILABLE = {"type": "p", "children": [{"text": "Content Unavailable"}]}


def generate_contact(contact_link: ContactsLinkOutput) -> List:
    """
    Returns a list of Latex formated objects representing the parts of a
    contact (name, email, uuid, etc), to be appended, in order, to the
    Latex document.
    """
    contact = contact_link.contact.dict(exclude_none=True)

    latex_contact = [
        Subsubsection(
            " ".join(
                contact.get(k, "") for k in ["first_name", "middle_name", "last_name"]
            )
        )
    ]

    for k in ["uuid", "url"]:
        if contact.get(k):
            paragraph = section.Paragraph(f"{k.title()}:")
            paragraph.append(NoEscape(contact[k]))
            latex_contact.append(paragraph)

    if contact.get("mechanisms"):
        for mechanism in contact["mechanisms"]:
            paragraph = section.Paragraph(f"{mechanism['mechanism_type']}:")
            paragraph.append(mechanism["mechanism_value"])
            latex_contact.append(paragraph)

    if contact_link.roles:
        paragraph = section.Paragraph("Roles:")
        paragraph.append(", ".join(r for r in contact_link.roles))
        latex_contact.append(paragraph)

    return latex_contact


def process_contacts(contacts: List[ContactsLinkOutput]) -> List:
    """
    Returns a flattened list of the all the Latex objects representing
    all of the document contacts, to be appended, in order to the Latex document.
    """
    contact_links = [ContactsLinkOutput.from_orm(contact) for contact in contacts]

    return [
        item
        for contact_link in contact_links
        for item in generate_contact(contact_link)
    ]


def hyperlink(url: str, text: str) -> NoEscape:
    """
    Returns a Latex formatted hyperlink object, wrapped with a
    NoEscape command to ensure the string gets processed as a
    command, and not plain text.
    """
    text = utils.escape_latex(text)
    return NoEscape(f"\\href{{{url}}}{{{text}}}")


def reference(reference_id: str) -> NoEscape:
    """
    Returns a Latex formatted refrerence object, wrapped with a
    NoEscape command to ensure the string gets processed as a
    command and not plain text.
    """

    return NoEscape(f"\\cite{{{bib_reference_name(reference_id)}}}")


# TODO: wrape the first 3 with NoEscape?
TEXT_WRAPPERS = {
    "superscript": lambda e: f"\\textsuperscript{{{e}}}",
    "subscript": lambda e: f"\\textsubscript{{{e}}}",
    "underline": lambda e: f"\\underline{{{e}}}",
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
    e = utils.escape_latex(data["text"])

    for option, command in TEXT_WRAPPERS.items():
        if data.get(option) and e.strip(" ") != "":
            e = command(e)

    # TODO: should this be wrapped with NoEscape?
    return NoEscape(e)


def process_text_content(
    data: Union[document.TextLeaf, document.ReferenceNode, document.LinkNode]
) -> List[NoEscape]:
    """
    Returns a list of text base elements (text, reference or hyperlink)
    wrapped with the appropriate Latex formatting commands
    """
    result = []
    for d in data:
        if d.get("type") == "a":
            result.append(hyperlink(d["url"], d["children"][0]["text"]))
        elif d.get("type") == "ref":
            result.append(reference(d["refId"]))
        else:
            result.append(wrap_text(d))
    return result


def process_data_access_url(access_url: document.DataAccessUrl) -> List[NoEscape]:
    """
    Returns a list of Latex formatted commands, to be appended in order
    to the Latex document, to display a single data acccess url
    """
    p1 = section.Paragraph(wrap_text({"text": "Access url:", "bold": True}))  # type: ignore
    p1.append(hyperlink(access_url["url"], access_url["url"]))

    p2 = section.Paragraph(wrap_text({"text": "Description:", "bold": True}))  # type: ignore
    p2.append(access_url["description"])
    return [p1, p2]


# TODO: figure out typing anotations for the child elements of the returned List
def process_data_access_urls(data: List[document.DataAccessUrl]) -> List:
    """
    Returns a list of Latex `Subsection` items with formatted elements to
    display access url fields.
    """
    urls = []
    for i, access_url in enumerate(data):
        s = Subsection(f"Entry #{str(i+1)}")
        for command in process_data_access_url(access_url):
            s.append(command)
        urls.append(s)
    return urls


def process_algorithm_variables(data: List[document.AlgorithmVariable]) -> NoEscape:
    """
    Returns a Latex formatted table representing algorithm input or output variables,
    wrapped with a NoEscape command. The text processing commands are applied to each
    of the algorithm variable child items before generating the table.
    """
    parsed_data = [
        {
            # process applies any subscript, superscript, bold, etc to the data
            # before transforming it into a table using latex
            k: " ".join(process(c) for c in v["children"])
            for k, v in d.items()
            if k in ["long_name", "unit"]
        }
        for d in data
    ]

    algorithm_variables_dataframe = pd.DataFrame.from_dict(
        parsed_data, orient="columns"
    )

    # TODO: make this dynamic, instead of based on the number of pixels in a page
    # page width is 426 pts - divide into 3/4 and 1/4 sections for algorithm name and units
    column_format = f"p{{{int(426/4)*3}pt}} p{{{int(426/4)}pt}}"
    latex_table = algorithm_variables_dataframe.to_latex(
        index=False,
        escape=False,
        column_format=column_format,
        na_rep=" ",
        columns=["long_name", "unit"],
        header=["\\textbf{{Name}}", "\\textbf{{Unit}}"],
    )
    return NoEscape(latex_table)


def process_table(data: document.TableNode, caption: str) -> NoEscape:
    """
    Returns a Latex formatted Table Item, wrapped with a NoEscape Command
    """
    rows = [
        tuple(
            " ".join(process(c) for c in table_cell["children"])
            for table_cell in table_row["children"]
        )
        for table_row in data["children"]
    ]

    dataframe = pd.DataFrame(rows[1:], columns=rows[0])

    column_formats = [f"p{{{1/len(rows[0])}\\linewidth}}" for _ in rows[0]]
    column_format = "".join(column_formats)

    pd.set_option("max_colwidth", None)
    latex_table = dataframe.to_latex(
        index=False,
        escape=False,
        na_rep=" ",
        column_format=column_format,
        caption=caption,
        position="H",
    )

    return NoEscape(latex_table)


def bib_reference_name(reference_id: str) -> str:
    """
    Generates an identifier that can be used in the Latex document
    to generate a reference object
    """
    return f"ref{reference_id}"


def generate_bib_reference(data: document.PublicationReference) -> str:
    """
    Returns a bibtex-formatted string representing a `@BOOK` type
    reference to be saved to a `.bib` file
    """
    reference_id = bib_reference_name(data["id"])
    reference = ""
    for e in ["title", "pages", "publisher", "year", "volume"]:
        if data.get(e):
            reference += f'{e}="{data[e]}",\n'
    if data.get("authors"):
        reference += f"author=\"{data['authors']}\",\n"
    # Can't use both VOLUME and NUMBER fields in bibtex

    return f"@BOOK{{{reference_id},\n{reference}}}"


def generate_bib_file(references: List[document.PublicationReference], filepath: str):
    """
    Saves the provided references, each as a new line, in a `.bib` file. Raises an exception
    if the provided filepath does not use a `.bib` extension
    """
    if not filepath.split(".")[-1] == "bib":
        raise ValueError("BibTex file should have a `.bib` extension")
    with open(filepath, "w") as bib_file:
        bib_file.write("\n".join(generate_bib_reference(r) for r in references))


def process(
    data: Union[
        document.BaseNode,
        document.SubsectionNode,
        document.ImageBlockNode,
        document.TableBlockNode,
        document.DivNode,
        document.OrderedListNode,
        document.UnorderedListNode,
        document.EquationNode,
    ],
    atbd_id: int = None,
):
    """
    Top level processing of each of the possible section items: subsection, image,
    table, generic div-type node, ordered and unordered list, and equation.

    Returns Latex formatted object for each of these, to be appeneded to the
    Latex document.
    """
    if data.get("type") in ["p", "caption"]:
        # p = section.Paragraph("")
        # p.append(NoEscape(" ".join(d for d in process_text_content(data["children"]))))
        # return p
        return NoEscape(" ".join(d for d in process_text_content(data["children"])))

    if data.get("type") in ["ul", "ol"]:
        latex_list = Itemize() if data["type"] == "ul" else Enumerate()
        for child in data["children"]:
            # latex_list.add_item(process(child))
            for item in process(child):
                latex_list.add_item(item)
        return latex_list

    if data.get("type") == "li":
        # TODO: confirm the `li` elements can only have 1 child element
        # If not, figure out how to handle a list item with different
        # kinds of children elements (paragraph / other list types)
        return [process(d) for d in data["children"]]
        # return process(data["children"][0])

    if data.get("type") == "sub-section":
        section_title = NoEscape(
            " ".join(d for d in process_text_content(data["children"]))
        )
        return Subsubsection(section_title)

    if data.get("type") == "equation":
        return Math(data=NoEscape(data["children"][0]["text"].replace("\\\\", "\\")))

    if data.get("type") == "image-block":
        [img] = filter(lambda d: d["type"] == "img", data["children"])
        [caption] = filter(lambda d: d["type"] == "caption", data["children"])

        # lambda execution environment only allows for files to
        # written to `/tmp` directory
        s3_client().download_file(
            Bucket=S3_BUCKET,
            Key=f"{atbd_id}/images/{img['objectKey']}",
            Filename=f"/tmp/{img['objectKey']}",
        )

        figure = Figure(position="H")
        figure.add_image(f"/tmp/{img['objectKey']}")

        figure.add_caption(
            NoEscape(" ".join(d for d in process_text_content(caption["children"])))
        )
        return figure

    if data.get("type") == "table-block":
        [table] = filter(lambda d: d["type"] == "table", data["children"])
        [caption] = filter(lambda d: d["type"] == "caption", data["children"])
        caption = NoEscape(
            " ".join(d for d in process_text_content(caption["children"]))
        )
        return process_table(table, caption=caption)


def setup_document(atbd: Atbds, filepath: str, journal: bool = False) -> Document:
    """
    Creates a new Latex document instance and adds packages/metadata commands
    necessary for the document style (eg: line numbering and spacing, math
    char support, table of contents generation)
    """
    doc = Document(
        default_filepath=filepath,
        documentclass=Command(
            "documentclass",
            options=["12pt"],
            # arguments="article",
            arguments="agujournal2019",
        ),
        fontenc="T1",
        inputenc="utf8",
        # use Latin-Math Modern pacakge for char support
        lmodern=True,
        textcomp=True,
        page_numbers=True,
        indent=True,
    )
    for p in [
        "color",
        "url",
        "graphicx",
        "float",
        "amsmath",
        "array",
        "booktabs",
        "soul",
    ]:
        doc.packages.append(Package(p))

    if journal:
        doc.packages.append(Package("setspace"))
        doc.preamble.append(Command("doublespacing"))

        doc.packages.append(Package("lineno"))
        doc.preamble.append(Command("linenumbers"))

    doc.packages.append(Package("hyperref"))
    doc.preamble.append(
        Command(
            "hypersetup",
            arguments=f"colorlinks={str(journal).lower()},linkcolor=blue,filecolor=magenta,urlcolor=blue",
        )
    )

    doc.preamble.append(Command("title", arguments=atbd.title))
    doc.preamble.append(Command("date", arguments=NoEscape("\\today")))

    doc.append(Command("maketitle"))

    if not journal:
        doc.append(Command("tableofcontents"))
    return doc


def generate_latex(atbd: Atbds, filepath: str, journal=False):
    """
    Generates a Latex document with associated Bibtex file
    """

    [atbd_version] = atbd.versions
    document_data = atbd_version.document
    contacts_data = atbd_version.contacts_link
    doc = setup_document(atbd, filepath, journal=journal)

    generate_bib_file(
        document_data.get("publication_references", []), filepath=f"{filepath}.bib",
    )
    section_name: str
    info: Any

    for section_name, info in SECTIONS.items():
        # Journal Acknowledgements and Journal Discussion are only included in
        # Journal type pdfs
        if not journal and section_name in [
            "journal_acknowledgements",
            "journal_discussion",
        ]:
            continue

        s = Section(info["title"])

        if info.get("subsection"):
            s = Subsection(info["title"])

        if info.get("subsubsection"):
            s = Subsubsection(info["title"])

        doc.append(s)

        if section_name == "contacts":
            for contact in process_contacts(contacts_data):
                doc.append(contact)
            continue

        if not document_data.get(section_name):
            doc.append(process(CONTENT_UNAVAILABLE))  # type: ignore
            continue

        if section_name in [
            "algorithm_input_variables",
            "algorithm_output_variables",
        ]:

            doc.append(process_algorithm_variables(document_data[section_name]))
            continue

        if section_name in [
            "algorithm_implementations",
            "data_access_input_data",
            "data_access_output_data",
            "data_access_related_urls",
        ]:
            for url in process_data_access_urls(document_data[section_name]):
                doc.append(url)
            continue

        for item in document_data[section_name].get("children", [CONTENT_UNAVAILABLE]):
            doc.append(NoEscape("\n"))
            doc.append(process(item, atbd_id=atbd.id))
            continue

    # doc.append(Command("bibliographystyle", arguments="apalike"))
    doc.append(Command("bibliography", arguments=NoEscape(filepath)))

    return doc


def generate_pdf(atbd: Atbds, filepath: str, journal: bool = False):
    """
    Generates and saves a Latex document as a PDF to `/tmp`, along with
    the necessary bib file
    """
    # The extension is removed because the latex compiler uses this filepath
    # to generate a bunch of temporary files (<filepath>.tex, <filepath>.log,
    # <filepath>.aux, etc), before generating the pdf. Once it generates the
    # pdf file, it adds the `.pdf` extension.
    filepath = os.path.join("/tmp", filepath.replace(".pdf", ""))

    # create a folder for the pdf/latex files to be stored in
    pathlib.Path(filepath).mkdir(parents=True, exist_ok=True)

    latex_document = generate_latex(atbd, filepath, journal=journal)

    latex_document.generate_pdf(
        filepath=filepath,
        clean=False,
        clean_tex=False,
        # latexmk automatically performs the multiple runs necessary
        # to include the bibliography, table of contents, etc
        compiler="latexmk",
        # the `--pdfxe` flag loads the Xelatex pacakge necessary for
        # the compiler to manage image positioning within the pdf document
        # and native unicode character handling
        compiler_args=["--pdfxe"],
    )

    return f"{filepath}.pdf"
