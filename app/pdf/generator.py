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
from app.db.models import Atbds
from app.api.utils import s3_client
from app.config import BUCKET


def process_reference(data):
    reference_id = f"ref{data['publication_reference_id']}"
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
    return NoEscape(f"\href{{{url}}}{{{text}}} ")


def reference(reference_id):
    return NoEscape(f"\\cite{{ref{reference_id}}}")


def process_text(data):
    e = data["text"]
    if data.get("superscript"):
        # e = NoEscape(f"\\textsuperscript{{{e}}}")
        e = f"\\textsuperscript{{{e}}}"
    if data.get("subscript"):
        print("SUBSCRIPTING NOW>>>")
        # e = NoEscape(f"\\textsubscript{{{e}}}")
        e = f"\\textsubscript{{{e}}}"
    if data.get("underline"):
        print("UNDERLINING>>>")
        # e = NoEscape(f"\\underline{{{e}}}")
        e = f"\\underline{{{e}}}"
    if data.get("italic"):
        e = utils.italic(e)
    if data.get("bold"):
        e = utils.bold(e)

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


def process_data_access_url(data, doc):
    for access_url in data:

        with doc.create(Subsection("")):

            with doc.create(
                section.Paragraph(process_text({"text": "Access url:", "bold": True}))
            ) as s:
                s.append(hyperlink(access_url["url"], access_url["url"]))

            with doc.create(
                section.Paragraph(process_text({"text": "Description:", "bold": True}))
            ) as s:
                s.append(
                    " ".join(
                        process_text(c)
                        for c in access_url["description"]["children"][0]["children"]
                    )
                )


def process_algorithm_variables(data, doc):
    #
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

    # TODO: figure out how to apply the WYSIWYG parsing to the algorithm variable list
    # algorithm_variables_dataframe["long_name"] = algorithm_variables_dataframe[
    #     "long_name"
    # ].apply(process_content)
    # algorithm_variables_dataframe["unit"] = algorithm_variables_dataframe["unit"].apply(
    #     process_content
    # )
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
        if data.get("type") == "p":

            if doc is None:
                return NoEscape(" ".join(d for d in process_content(data["children"])))
            for c in process_content(data["children"]):
                doc.append(NoEscape(c))
            doc.append("\n")

        if data.get("type") == "ol":
            with doc.create(Enumerate()) as doc:
                parse(data["children"], doc)

        if data.get("type") == "ul":
            with doc.create(Itemize()) as doc:
                parse(data["children"], doc)

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
        fontenc="T1",
        inputenc="utf8",
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


def generate_latex(atbd: Atbds, filepath: str, journal: bool = False):
    atbd_version_data = atbd.versions[0].document
    doc = setup_document(atbd, filepath, journal=journal)

    generate_bibliography(
        atbd_version_data.get("publication_references", []), filepath=f"{filepath}.bib"
    )
    for section_name, info in SECTIONS.items():
        s = Section(info["title"])
        if info.get("subsection"):
            s = Subsection(info["title"])
        with doc.create(s):

            if not atbd_version_data.get(section_name):
                parse(CONTENT_UNAVAILABLE, s)
                continue

            if section_name in [
                "algorithm_input_variables",
                "algorithm_output_variables",
            ]:

                process_algorithm_variables(atbd_version_data[section_name], doc)
                continue

            if section_name in [
                "algorithm_implementations",
                "data_access_input_data",
                "data_access_output_data",
                "data_access_related_urls",
            ]:
                process_data_access_url(atbd_version_data[section_name], doc)
                continue

            if (
                section_name in ["journal_acknowledgements", "journal_dicsussion"]
                and not journal
            ):
                continue

            if isinstance(atbd_version_data[section_name], dict):
                parse(
                    atbd_version_data[section_name].get(
                        "children", CONTENT_UNAVAILABLE
                    ),
                    s,
                )
                continue

            parse(atbd_version_data[section_name], s)

            # TODO: process contacts

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

