import os
import pathlib
import pandas as pd
from pylatex import (
    Document,
    Command,
    Package,
    NoEscape,
    Section,
    Subsection,
    Subsubsection,
    section,
    Itemize,
    Enumerate,
    Math,
    Figure,
    utils,
)
from collections import OrderedDict
from typing import List
from app.db.models import Atbds
from app.schemas.versions import ContactLink
from app.schemas.contacts import Output as Contact
from app.api.utils import s3_client
from app.config import BUCKET


def process_contacts(contacts: List[ContactLink], doc):
    contacts = [ContactLink.from_orm(contact) for contact in contacts]
    for contact_link in contacts:
        contact = contact_link.contact.dict(exclude_none=True)
        print(contact_link.contact)
        # contact = Contact.from_orm(contact_link.contact).dict(exclude_none=True)
        # print("CONTACT: ", contact)
        doc.append(
            NoEscape(
                " ".join(
                    contact.get(k, "")
                    for k in ["first_name", "middle_name", "last_name"]
                )
            )
        )

        for k in ["uuid", "url"]:
            if contact.get(k):
                with doc.create(section.Paragraph(f"{k.title()}:")) as paragraph:
                    paragraph.append(NoEscape(contact[k]))

        if contact.get("mechanisms"):
            for mechanism in contact["mechanisms"]:
                with doc.create(
                    section.Paragraph(f"{mechanism['mechanism_type']}:")
                ) as paragraph:
                    paragraph.append(mechanism["mechanism_value"])

        if contact_link.roles:
            with doc.create(section.Paragraph("Roles:")) as paragraph:
                paragraph.append(", ".join(r for r in contact_link.roles))


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


def process_reference(data):
    reference_id = f"ref{data['id']}"
    reference = ""
    for e in ["title", "pages", "publisher", "year", "volume"]:
        if data.get(e):
            reference += f'{e}="{data[e]}",\n'
    if data.get("authors"):
        reference += f"author=\"{data['authors']}\",\n"
    # Can't use both VOLUME and NUMBER fields in bibtex

    return f"@BOOK{{{reference_id},\n{reference}}}"


def generate_bibliography(references, filepath):
    with open(filepath, "w") as bib_file:
        bib_file.write("\n".join(process_reference(r) for r in references))


def hyperlink(url, text):
    text = utils.escape_latex(text)
    return NoEscape(f"\\href{{{url}}}{{{text}}}")


def reference(reference_id):
    return NoEscape(f"\\cite{{ref{reference_id}}}")


TEXT_WRAPPERS = {
    "superscript": lambda e: f"\\textsuperscript{{{e}}}",
    "subscript": lambda e: f"\\textsubscript{{{e}}}",
    "underline": lambda e: f"\\underline{{{e}}}",
    "italic": lambda e: utils.italic(e),
    "bold": lambda e: utils.bold(e),
}


def process_text(data):
    # Allows for wrapping text with multiple formatting options
    # ie:  process_text({"bold": true, "italic": true, "text": ... })
    # will return latex like `\bold{\italic{text}}`
    e = data["text"]
    for option, command in TEXT_WRAPPERS.items():
        if data.get(option):
            e = command(e)
    return e


def process_content(data):
    res = []
    for d in data:
        if d.get("type") == "a":
            res.append(hyperlink(d["url"], d["children"][0]["text"]))
        elif d.get("type") == "ref":
            res.append(reference(d["refId"]))
        else:
            res.append(process_text(d))
    return res


def process_data_access_url(access_url, doc):
    with doc.create(
        section.Paragraph(process_text({"text": "Access url:", "bold": True}))
    ) as s:
        s.append(hyperlink(access_url["url"], access_url["url"]))

        with doc.create(
            section.Paragraph(process_text({"text": "Description:", "bold": True}))
        ) as s:
            s.append(access_url["description"])


def process_data_access_urls(data, doc):
    for i, access_url in enumerate(data):
        with doc.create(Subsection(f"Entry #{str(i+1)}")):
            process_data_access_url(access_url, doc)


def process_algorithm_variables(data, doc):
    parsed_data = [
        {
            # process_text applies any subscript, superscript, bold, etc to the data
            # before transforming it into a table using latex
            # TODO: Figure out how to do this without having to fetch children[0][children]
            k: " ".join(process_text(c) for c in v["children"][0]["children"])
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
    latex_dataframe = algorithm_variables_dataframe.to_latex(
        index=False,
        bold_rows=True,
        escape=False,
        column_format=column_format,
        na_rep=" ",
        columns=["long_name", "unit"],
        header=["\\textbf{{Name}}", "\\textbf{{Unit}}"],
    )
    doc.append(NoEscape(latex_dataframe))


def parse(data, doc=None):
    if isinstance(data, list):
        for e in data:
            parse(e, doc)

    if isinstance(data, dict):
        # When a `p` element is encountered at the root/section level,
        # it must be appended directly to the document. However, `p` elements
        # also appear within other elements (eg: list items). In those
        # cases the contents of the processed `p` element, should be returned
        # as a string, for the parent element to handle it (eg:
        #     list.append(process_p_item)
        # )
        # To ensure the `p` item is returned and not appended to the doc,
        # pass `None` as the `doc` parameter value when calling `parse()`
        # The output is wrapped in a NoEscape command, to ensure that when the
        # output text is appended to the latex document, latex does not interpret
        # commands as full-text and escape them: (eg: ensure that `\bold{sometext}`
        # does not become printed as `\textbackslashbol\{sometext\}` in the rendered
        # pdf)
        if data.get("type") == "p":

            if doc is None:
                return NoEscape(" ".join(d for d in process_content(data["children"])))

            for c in process_content(data["children"]):
                doc.append(NoEscape(c))

            doc.append("\n")

        # ordered list
        if data.get("type") == "ol":
            with doc.create(Enumerate()) as doc:
                parse(data["children"], doc)

        # un-ordered list
        if data.get("type") == "ul":
            with doc.create(Itemize()) as doc:
                parse(data["children"], doc)
        # list item
        if data.get("type") == "li":
            doc.add_item(parse(data["children"][0], doc=None))

        if data.get("type") == "sub-section":
            with doc.create(Subsubsection(data["children"][0]["text"])) as doc:
                doc.append("")

        if data.get("type") == "equation":
            doc.append(
                Math(data=NoEscape(data["children"][0]["text"].replace("\\\\", "\\")))
            )

        if data.get("type") == "img":
            # lambda execution environment only allows for files to
            # written to `/tmp` directory
            s3_client().download_file(
                Bucket=BUCKET,
                Key=data["objectKey"],
                Filename=f"/tmp/{data['objectKey']}",
            )

            with doc.create(Figure(position="H")) as doc:
                doc.add_image(f"/tmp/{data['objectKey']}",)
                doc.add_caption(data["children"][0]["text"])


def setup_document(atbd: Atbds, filepath: str, journal: bool = False):
    doc = Document(
        default_filepath=filepath,
        documentclass=Command("documentclass", options=["12pt"], arguments="article",),
        # font-encoding
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
        "booktabs",
        "graphicx",
        "float",
        "amsmath",
        "array",
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
    # document_data = atbd.versions[0].document
    # atbd_version_contacts = atbds
    [atbd_version] = atbd.versions
    document_data = atbd_version.document
    contacts_data = atbd_version.contacts_link
    doc = setup_document(atbd, filepath, journal=journal)

    generate_bibliography(
        document_data.get("publication_references", []), filepath=f"{filepath}.bib",
    )

    for section_name, info in SECTIONS.items():
        s = Section(info["title"])

        if info.get("subsection"):
            s = Subsection(info["title"])

        if info.get("subsubsection"):
            s = Subsubsection(info["title"])

        with doc.create(s):

            if not document_data.get(section_name) and section_name != "contacts":
                parse(CONTENT_UNAVAILABLE, s)
                continue

            if section_name in [
                "algorithm_input_variables",
                "algorithm_output_variables",
            ]:

                process_algorithm_variables(document_data[section_name], doc)
                continue

            if section_name in [
                "algorithm_implementations",
                "data_access_input_data",
                "data_access_output_data",
                "data_access_related_urls",
            ]:
                process_data_access_urls(document_data[section_name], doc)
                continue

            if section_name == "contacts":
                process_contacts(contacts_data, doc)
                continue

            # Journal Acknowledgements and Journal Discussion are only included in
            # Journal type pdfs
            if (
                section_name in ["journal_acknowledgements", "journal_dicsussion"]
                and not journal
            ):
                continue

            if isinstance(document_data[section_name], dict):
                parse(
                    document_data[section_name].get("children", CONTENT_UNAVAILABLE), s,
                )
                continue

            parse(document_data[section_name], s)

    doc.append(Command("bibliographystyle", arguments="abbrv"))
    doc.append(Command("bibliography", arguments=NoEscape(filepath)))
    return doc


def generate_pdf(atbd: Atbds, filepath: str, journal: bool = False):
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
        clean=True,
        clean_tex=False,
        # automatically performs the multiple runs necessary
        # to include the bibliography, table of contents, etc
        compiler="latexmk",
        # loads a pacakge necessary for the compiler to manage
        # image positioning within the pdf document
        compiler_args=["--pdf"],
    )

    return f"{filepath}.pdf"

