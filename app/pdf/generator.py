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
from app.schemas.versions_contacts import (
    ContactMechanismEnum,
    ContactsLinkOutput,
    RolesEnum,
)

SECTIONS = {
    "abstract": {},
    "plain_summary": {"title": "Plain Language Summary"},
    "keywords": {"title": "Keywords"},
    "version_description": {"title": "Description"},
    "introduction": {"title": "Introduction"},
    "context_background": {"title": "Context / Background", "section_header": True},
    "historical_perspective": {"title": "Historical Perspective", "subsection": True},
    "additional_information": {"title": "Additional Data", "subsection": True},
    "algorithm_description": {"title": "Algorithm Description", "section_header": True},
    "scientific_theory": {"title": "Scientific Theory", "subsection": True},
    "scientific_theory_assumptions": {
        "title": "Scientific Theory Assumptions",
        "subsubsection": True,
    },
    "mathematical_theory": {"title": "Mathematical Theory", "subsection": True},
    "mathematical_theory_assumptions": {
        "title": "Mathematical Theory Assumptions",
        "subsubsection": True,
    },
    "algorithm_input_variables": {
        "title": "Algorithm Input Variables",
        "subsection": True,
    },
    "algorithm_output_variables": {
        "title": "Algorithm Output Variables",
        "subsection": True,
    },
    "algorithm_implementations": {"title": "Algorithm Availability"},
    "algorithm_usage_constraints": {"title": "Algorithm Usage Constraints"},
    "performace_assessment_validations": {
        "title": "Performance Assessment Validation Methods",
        "section_header": True,
    },
    "performance_assessment_validation_methods": {
        "title": "Performance Assessment Validation Methods",
        "subsection": True,
    },
    "performance_assessment_validation_uncertainties": {
        "title": "Performance Assessment Validation Uncertainties",
        "subsection": True,
    },
    "performance_assessment_validation_errors": {
        "title": "Performance Assessment Validation Errors",
        "subsection": True,
    },
    "data_access": {"title": "Data Access", "section_header": True},
    "data_access_input_data": {"title": "Input Data Access", "subsection": True},
    "data_access_output_data": {"title": "Output Data Access", "subsection": True},
    "data_access_related_urls": {"title": "Important Related URLs", "subsection": True},
    "journal_discussion": {"title": "Discussion"},
    "journal_acknowledgements": {"title": "Acknowledgements"},
    "data_availability": {"title": "Open Research"},
    # "contacts": {"title": "Contacts"},
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
            paragraph = section.Paragraph(f"{k.title()}:", numbering=False)
            paragraph.append(NoEscape(contact[k]))
            latex_contact.append(paragraph)

    if contact.get("mechanisms"):
        for mechanism in contact["mechanisms"]:
            paragraph = section.Paragraph(
                f"{mechanism['mechanism_type']}:", numbering=False
            )
            paragraph.append(mechanism["mechanism_value"])
            latex_contact.append(paragraph)

    if contact_link.roles:
        paragraph = section.Paragraph("Roles:", numbering=False)
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
    return NoEscape(f"\\href{{{url}}}{{\\nolinkurl{{{text}}}}}")


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
    e = utils.escape_latex(data["text"])
    # e = data["text"]

    for option, command in TEXT_WRAPPERS.items():
        if data.get(option) and e.strip(" ") != "":
            e = command(e)

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
    p1 = section.Paragraph(wrap_text({"text": "Access url:", "bold": True}), numbering=False)  # type: ignore
    p1.append(hyperlink(access_url["url"], access_url["url"]))

    p2 = section.Paragraph(wrap_text({"text": "Description:", "bold": True}), numbering=False)  # type: ignore
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
        s = Subsubsection(NoEscape(f"\\normalfont{{Entry \\#{str(i+1)}}}"))
        for command in process_data_access_url(access_url):
            s.append(command)
        urls.append(s)
    return urls


def process_algorithm_variables(
    data: List[document.AlgorithmVariable], caption
) -> NoEscape:
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

    latex_table = algorithm_variables_dataframe.to_latex(
        index=False,
        escape=False,
        column_format="p{0.75\\linewidth}p{0.25\\linewidth}",
        na_rep=" ",
        columns=["long_name", "unit"],
        header=["\\textbf{{Name}}", "\\textbf{{Unit}}"],
        caption=caption,
        position="H",
        longtable=True,
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
    del data["id"]
    reference = ""

    for k, v in data.items():
        if not v:
            continue
        #  `series` gets changed to `journal` since `series` isn't a field used in
        # the `@article` citation type of `apacite`
        if k == "series":
            reference += f"journal={{{v}}},\n"
            continue
        if k == "authors":
            reference += f"author={{{v}}},\n"
            continue
        reference += f"{k}={{{v}}},\n"

    return f"@article{{{reference_id},\n{reference}}}"


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
        section_title = " ".join(d for d in process_text_content(data["children"]))

        return Subsubsection(
            NoEscape(f"\\normalfont{{\\itshape{{{section_title}}}}}"), numbering=False
        )

    if data.get("type") == "equation":
        eq = data["children"][0]["text"].replace("\\\\", "\\")
        return NoEscape(f"\\begin{{equation}}{eq}\\end{{equation}}")

        # return Math(data=NoEscape(data["children"][0]["text"].replace("\\\\", "\\")))

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


def generate_latex(atbd: Atbds, filepath: str, journal=False):  # noqa: C901
    """
    Generates a Latex document with associated Bibtex file
    """
    [atbd_version] = atbd.versions

    # parse as Pydantic model and return to dict to enforce data integrity
    document_data = document.Document.parse_obj(atbd_version.document).dict()

    contacts_data = atbd_version.contacts_link

    document_class = "agujournal2019" if journal else "article"
    doc = Document(
        default_filepath=filepath,
        documentclass=Command("documentclass", arguments=document_class),
        # disable inputenc and fontenc because we are compiling using
        # xelatex which accepts unicode chars by defaults
        inputenc=None,
        fontenc=None,
        # use textcomp for additional character support
        textcomp=True,
        # use Latin-Math Modern package for char suppor
        lmodern=True,
    )

    for p in [
        "float",
        "booktabs",
        "soul",
        "longtable",
        "amsmath",
        "fontspec",
        "fancyhdr",
        "xcolor",
    ]:
        doc.packages.append(Package(p))

    doc.preamble.append(Command("setmainfont", arguments=NoEscape("Latin Modern Math")))
    doc.preamble.append(
        Command("definecolor", arguments=["ltgray", "cmyk", ".12,0,0,.3"])
    )

    if not journal:

        doc.preamble.append(
            NoEscape(
                "\\PassOptionsToPackage{obeyspaces,hyphens}{url}\\usepackage{hyperref}"
            )
        )

        doc.preamble.append(
            Command(
                "hypersetup",
                arguments="breaklinks=true,colorlinks=true,linkcolor=blue,filecolor=magenta,urlcolor=blue,citecolor=black",
            )
        )
        doc.preamble.append(Command("urlstyle", arguments="same"))
        # The apacite package is added using the `usepackage` command
        # instead of the `Package()` function to ensure that apacite
        # will be loaded after `hyperref` - with breaks things if the
        # two packages are loaded in the reverse order:
        # https://tex.stackexchange.com/a/316288
        doc.preamble.append(Command("usepackage", arguments="apacite"))

    if journal:

        doc.packages.append(Package("lineno"))
        doc.preamble.append(Command("linenumbers"))

    # TODO: re-implement the following functionality using pylatex's `UnsafeCommand` class.
    # eg:
    # new_comm = UnsafeCommand('newcommand', '\exampleCommand', options=3,
    #                         extra_arguments=r'\color{#1} #2 #3 \color{black}')
    # doc.append(new_comm)
    # # Use our newly created command with different arguments
    # doc.append(ExampleCommand(arguments=Arguments('blue', 'Hello', 'World!')))

    header_content = ""
    if journal:
        header_content += "\\vss\\centerline{\\color{ltgray}\\small Manuscript submitted to {\\it Earth and Space Science}}"
        header_content += " \\vss\\centerline{ }"  # ensures line break
    header_content += "\\vss\\centerline{\\color{ltgray}\\small This ATBD was downloaded from the NASA Algorithm Publication Tool (APT)}"

    header_def = f"""\\makeatletter
        \\let\\@mkboth\\@gobbletwo
        \\let\\chaptermark\\@gobble
        \\let\\sectionmark\\@gobble


        \\def\\ps@headings{{
            \\def\\@oddfoot{{
                \\centerline{{
                    \\small --\\the\\c@page--
                }}
            }}
            \\let\\@evenfoot\\@oddfoot
            \\def\\@oddhead{{\\vbox to 0pt{{{header_content}\\vskip12pt}}}}
            \\let\\@evenhead\\@oddhead
        }}
        \\ps@headings

        \\def\\@maketitle{{
            \\newpage
            \\vskip 2em
            \\begin{{center}}
                \\let \\footnote \\thanks
                {{\\LARGE \\@title \\par}}
                \\vskip 1.5em
                {{
                    \\large\\lineskip .5em
                    \\begin{{tabular}}[t]{{c}}
                        \\@author
                    \\end{{tabular}}\\par
                }}
                \\vskip 1em
                {{\\large \\@date}}
            \\end{{center}}
            \\par
            \\vskip 1.5em
        }}

        \\makeatother
        """
    doc.preamble.append(NoEscape(header_def))

    doc.append(Command("title", arguments=atbd.title))

    affiliations = []
    authors = []

    contacts_data = sorted(contacts_data, key=lambda x: x.contact.last_name)

    for contact_link in contacts_data:

        initials = "".join(
            [f"{n[0].upper()}." for n in contact_link.contact.first_name.split(" ")]
        )

        author = f"{initials} {contact_link.contact.last_name}"

        if not journal or not contact_link.affiliations:
            authors.append(author)
            continue

        affiliation_indices = []
        for affiliation in contact_link.affiliations:
            if affiliation not in affiliations:
                affiliations.append(affiliation)
            affiliation_indices.append(str(affiliations.index(affiliation) + 1))

        author += f'\\affil{{{",".join(affiliation_indices)}}}'

        authors.append(author)

    if journal:

        doc.append(
            Command(
                "authors",
                arguments=NoEscape(", ".join(authors)),
            )
        )
        for i, affiliation in enumerate(affiliations):
            doc.append(Command("affiliation", arguments=[str(i + 1), affiliation]))

        corresponding_author = [
            contact_link.contact
            for contact_link in contacts_data
            if RolesEnum.CORRESPONDING_AUTHOR in contact_link.roles
        ]
        if not corresponding_author:
            corresponding_author_fullname = "No corresponding author found"
            corresponding_author_email = "No email found"
        else:
            corresponding_author = corresponding_author[0]
            corresponding_author_fullname = f"{corresponding_author.first_name} {corresponding_author.last_name}"  # type: ignore

            corresponding_author_email = [
                mechanism.mechanism_value  # type: ignore
                for mechanism in corresponding_author.mechanisms  # type: ignore
                if mechanism.mechanism_type == ContactMechanismEnum.EMAIL
            ]
            if corresponding_author_email:
                corresponding_author_email = corresponding_author_email[0]

        doc.append(
            Command(
                "correspondingauthor",
                arguments=[corresponding_author_fullname, corresponding_author_email],
            )
        )

    else:
        doc.append(Command("author", arguments=NoEscape("\\and ".join(authors))))
        doc.append(
            Command(
                "date",
                arguments=NoEscape(
                    atbd_version.published_at.strftime("%B %d, %Y")
                    if atbd_version.published_at
                    else "{}"
                ),
            )
        )
        doc.append(Command("makeatletter"))
        doc.append(Command("@maketitle"))
        doc.append(Command("makeatother"))

    if not journal:
        doc.append(Command("tableofcontents"))
        doc.append(Command("newpage"))

    if journal:
        doc.append(Command("begin", arguments="keypoints"))
        for keypoint in document_data["key_points"].split("\n"):
            doc.append(Command("item", arguments=keypoint.strip("-") or " "))
        doc.append(Command("end", arguments="keypoints"))

    generate_bib_file(
        document_data["publication_references"],
        filepath=f"{filepath}.bib",
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

        if section_name == "abstract":
            doc.append(Command("begin", "abstract"))
            if not document_data.get(section_name):
                doc.append("Abstract Unavailable")
            else:
                doc.append(document_data[section_name])
            doc.append(Command("end", "abstract"))
            continue

        # Version Description is the only field that doesn't get rendered at all
        # if it's not found in the database data (as opposed to other field which)
        # get displayed as "Content Unavailable"
        if section_name == "version_description" and (
            not document_data.get("version_description")
            or not process(document_data.get("version_description"))
        ):
            continue

        s = Section(
            info["title"],
            numbering=False if section_name in ["plain_summary", "keywords"] else True,
        )

        if info.get("subsection"):
            title = info["title"]
            if journal:
                title = NoEscape(f"\\normalfont{{{title}}}")
            s = Subsection(title)

        if info.get("subsubsection"):
            title = info["title"]
            if journal:
                title = NoEscape(f"\\normalfont{{{title}}}")
            s = Subsubsection(title)

        doc.append(s)

        if info.get("section_header"):
            # section header means that no content is needed
            continue

        if section_name == "plain_summary":
            doc.append(document_data[section_name])
            continue

        if section_name == "keywords" and atbd_version.keywords:
            doc.append(Command("begin", arguments="itemize"))
            for keyword in atbd_version.keywords:
                doc.append(Command("item", arguments=keyword["label"]))
            doc.append(Command("end", arguments="itemize"))
            continue

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

            doc.append(
                process_algorithm_variables(
                    data=document_data[section_name],
                    caption=document_data[f"{section_name}_caption"],
                )
            )
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

    if not journal:
        doc.append(Command("bibliographystyle", arguments="apacite"))

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
        # XeTeX generates multiple intermediate files (`.aux`, `.log`, etc)
        # that we want to remove
        clean=True,
        # Keep the generated `.tex` file
        clean_tex=False,
        # latexmk automatically performs the multiple runs necessary
        # to include the bibliography, table of contents, etc
        compiler="latexmk",
        # the `--pdfxe` flag loads the Xelatex pacakge necessary for
        # the compiler to manage image positioning within the pdf document
        # and native unicode character handling
        compiler_args=["-pdfxe", "-interaction=batchmode", "-e", "$max_repeat=10"],
        # Hides compiler output, except in case of error
        silent=True,
    )

    return f"{filepath}.pdf"
