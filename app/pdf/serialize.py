#!/usr/bin/env python3

"""
copied from  https://github.com/developmentseed/nasa-apt/blob/eb0b6bc897efa29284dd11b4e46b085f388d9743/ecs/tex/serialize.py

TODO: refactor to be a python package instead of cli tool
TODO: unit tests
TODO: use a templating package instead of string formatting
TODO: rename functions and classes to be pythonic

Using ATBD.tex as a template, this file adds variable definitions and others at the beginning to correctly fill out the template with the data held in the JSON file used as input.
The driver code and main class are at the end of this file. In general, the functions are more straightforward at the beginning and more complex at the end, and are commented accordingly.
Turn debug to True in order to see output as print statements instead of attempting to build the new TeX file.
"""

import json
import sys
from shutil import copyfile
import os
import pandas as pd
from latex import build_pdf
from num2words import num2words
from functools import reduce
from app.api.utils import s3_client
from app import config

debug = False
pdfImgs = []
htmlImgs = []
references = []
refIDs = {}


# from https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase
def toCamelCase(snake_str):
    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return "".join(x.title() for x in components)


def toSpaceCase(snake_str):
    components = snake_str.split("_")
    return " ".join(x.title() for x in components)


def processTable(nodeRows, caption=None):
    tableList = []
    for rows in nodeRows:
        tableList.append([])
        for row in rows["nodes"]:
            if "nodes" not in row:
                tableList.pop(-1)
                continue
            for cell in row["nodes"]:
                # Since we kept each cell in the table as a flexible type, they must be processed as generic WYSIWYG elements
                tableList[-1].append(processWYSIWYGElement(cell)[0])

    columnNames = [" " if not x else x for x in tableList.pop(0)]
    pd.set_option("display.max_colwidth", 1000)
    df = pd.DataFrame(tableList, columns=columnNames)
    # latex default text width = 426 pts
    column_format = "|".join(
        f" m{{{int(375/len(columnNames))}pt}} " for _ in columnNames
    )

    to_latex_params = dict(
        index=False, escape=False, header=True, column_format=f"{column_format}"
    )

    if caption:
        to_latex_params["caption"] = caption

    latexTable = df.to_latex(**to_latex_params)
    # insert [h] for block latex from "floating" the table to the top of the page
    latexTable = latexTable.replace("\\begin{table}", "\\begin{table}[h]")

    return latexTable


def addMarkup(text, marks):
    for mark in marks:
        markupType = mark["type"]
        if markupType == "italic":
            text = f"\\textit{{{text}}}"
        elif markupType == "bold":
            text = f"\\textbf{{{text}}}"
        elif markupType == "underline":
            text = f"\\underline{{{text}}}"
        elif markupType == "subscript":
            text = f"\\textsubscript{{{text}}}"
        elif markupType == "superscript":
            text = f"\\textsuperscript{{{text}}}"
    return text


def whiteSpaceStrip(text):
    text = text.replace("\n", "\\\\")
    while text[:2].strip() == "\\\\":
        text = text[2:]
    while text[-2:].strip() == "\\\\":
        text = text[:-2]
    # The below line should perhaps be moved to the escapeSpecialChars function
    text = text.replace("/", "\/")
    return text


def preserveStyle(text):
    text = whiteSpaceStrip(text)
    text = escapeSpecialChars(text)
    return text


# TODO: This is an incomplete list of special characters which cause errors when not escaped in LaTeX code - more will need to be added, or a different method is needed to escape them
def escapeSpecialChars(text):
    return text.replace("%", "\%").replace("&", "\&").replace("_", "\_")


def processText(nodes):
    to_return = ""
    for node in nodes:

        if node["object"] == "text":
            for leaf in node["leaves"]:
                if "marks" in leaf and leaf["marks"]:
                    to_return += addMarkup(preserveStyle(leaf["text"]), leaf["marks"])
                else:
                    to_return += preserveStyle(leaf["text"])
        elif node["object"] == "inline" and node["type"] == "link":
            url = node["data"]["url"]
            url_nodes = node["nodes"]
            to_return += f"\\href{{{url}}}{{{processText(url_nodes)}}}"
        elif node["object"] == "inline" and node["type"] == "reference":
            try:
                refID = refIDs[node["data"]["id"]]
                to_return += f"\\cite{{{refID}}}"
            except KeyError:
                to_return += ""
    return to_return


def saveImage(imgUrl, img):
    print(
        "BUCKET CONTENTS: ",
        [k["Key"] for k in s3_client().list_objects(Bucket=config.BUCKET)["Contents"]],
    )
    print("DOWNLOADING FILE: ", imgUrl)
    s3_client().download_file(Bucket=config.BUCKET, Key=imgUrl, Filename=img)
    print("DOWNLOADED FILE")
    imgLink = num2words(len(pdfImgs))
    pdfImgs.append(f" \n \\newcommand{{\\{imgLink}}}{{{img}}}")
    htmlImgs.append(f"\\newcommand{{\\{imgLink}}}{{{img}}}")
    return imgLink


def wrapImage(img, cap=""):
    if cap:
        cap = f"\\caption{{{cap}}}"
    wrapper = f""" \\begin{{figure}}[H]
        \\includegraphics[width=\\maxwidth{{\\linewidth}}]{{\\{img}}}
        {cap}
        \\end{{figure}}
    """
    return wrapper


def processList(nodeRows, listType):
    itemList = ""
    for item in nodeRows:
        itemList += "\\item " + processText(item["nodes"]) + "\n"
    if listType == "unordered":
        return f"\\begin{{itemize}} {itemList} \\end{{itemize}}"
    elif listType == "ordered":
        return f"\\begin{{enumerate}} {itemList} \\end{{enumerate}}"


# Depending on the type of the node, call the corresponding function to correctly format and return
def processWYSIWYGElement(node):
    if node["type"] == "table":
        return (
            "\n \n"
            + processTable(node["nodes"], caption=node.get("data", {}).get("caption"))
            + "\n \n",
            "table",
        )
    elif node["type"] == "table_cell":
        return processWYSIWYGElement(node["nodes"]), "table_cell"
    elif node["type"][-4:] == "list":
        return processList(node["nodes"], node["type"][:-5]), "list"
    elif node["type"] == "image":
        imgUrl = node["data"]["src"]
        filename = imgUrl.rsplit("/", 1)[-1]
        imgCommand = saveImage(imgUrl, filename)
        try:
            caption = node["data"]["caption"]
            cmd = "\n \n" + wrapImage(imgCommand, caption) + "\n \n"
        except:
            cmd = "\n \n" + wrapImage(imgCommand) + "\n \n"
        return cmd, "image"
    elif node["type"] == "equation":
        return (
            " \\begin{equation} "
            + " \\begin{split} "
            + node["nodes"][0]["leaves"][0]["text"]
            + " \\end{split} "
            + " \\end{equation} ",
            "equation",
        )
    elif node["type"] == "paragraph":
        text = processText(node["nodes"])
        if text:
            return text, "text"
        else:
            return None, None
    else:
        print("oops! here with {}".format(node))
        return None, None


# Catch-all function which will handle each element (returnedElement) in the body of the ATBD in accordance with its type (elementType)
def processWYSIWYG(element):
    if debug:
        print("element in WYSIWYG is " + str(element))
    to_return = []
    ctr = 0

    for node in element["document"]["nodes"]:
        prepend = ""
        returnedElement, elementType = processWYSIWYGElement(node)

        if returnedElement:  # ignore newlines at the beginning
            # Only need to worry about adding newline characters around text elements
            if elementType == "text":
                # Only prepend text with newlines if not the first item or preceded by image, table, or list
                if (
                    ctr != 0
                    and to_return[ctr - 1][1] != "image"
                    and to_return[ctr - 1][1] != "table"
                    and to_return[ctr - 1][1] != "list"
                ):
                    prepend = "\\\\\\\\"
                # Convert element to string, and add newlines following and before (if needed)
                returnedElement = prepend + str(returnedElement) + "\\\\\\\\"
            to_return.append([returnedElement, elementType])
            ctr += 1
    return reduce((lambda x, y: x + y), list(map(lambda x: x[0], to_return)), "")


def accessURL(url):
    return f"\\textbf{{Access URL: }} {{{url}}} \\\\"


def simpleList(name, item):
    return f"\\textbf{{{toSpaceCase(name)}: }} {item} \\\\"


def simpleListURLs(name, item):
    return f"\\textbf{{{toSpaceCase(name)}: }} \\url{{{escapeSpecialChars(item)}}} \\\\"


def processImplementations(collection):
    return reduce(
        (lambda x, y: x + y),
        list(
            map(
                lambda x: "\\subsection {}"
                + processWYSIWYG(x["execution_description"])
                + "\\\\"
                + simpleListURLs("access_url", x["access_url"]),
                collection,
            )
        ),
        "",
    )


def processDataAccess(collection):
    return reduce(
        (lambda x, y: x + y),
        list(
            map(
                lambda x: "\\subsection {}"
                + processWYSIWYG(x["description"])
                + "\\\\"
                + simpleListURLs("access_url", x["access_url"]),
                collection,
            )
        ),
        "",
    )


def processDataAccessURL(collection):
    return reduce(
        (lambda x, y: x + y),
        list(
            map(
                lambda x: "\\subsection {}"
                + processWYSIWYG(x["description"])
                + "\\\\"
                + simpleListURLs("URL", x["url"]),
                collection,
            )
        ),
        "",
    )


def processContacts(collection):
    allContacts = ""
    for contact in collection:
        if contact["middle_name"] is not None:
            contactString = (
                contact["first_name"]
                + " "
                + contact["middle_name"]
                + " "
                + contact["last_name"]
            )
        else:
            contactString = contact["first_name"] + " " + contact["last_name"]
        contactString += " \\\\ "
        contactString += simpleList("uuid", contact["uuid"]) if contact["uuid"] else ""
        contactString += simpleListURLs("url", contact["url"]) if contact["url"] else ""
        if "mechanisms" in contact:
            contactString += "\\subsubsection{Contact Mechanisms}"
            for mechanism in contact["mechanisms"]:
                contactString += (
                    mechanism["mechanism_value"] + "\\\\"
                    if mechanism is not None
                    else ""
                )
        allContacts += "\\subsection{} " + contactString
    return allContacts


def processVarList(element):

    for var in element:

        # var["long_name"] = processWYSIWYG(json.loads(var["long_name"])).strip("\\")
        var["long_name"] = processWYSIWYG(var["long_name"]).strip("\\")

        if not var.get("unit"):
            continue
        # var["unit"] = processWYSIWYG(json.loads(var["unit"])).strip("\\")
        var["unit"] = processWYSIWYG(var["unit"]).strip("\\")

    pd.set_option("display.max_colwidth", 1000)
    varDF = pd.DataFrame.from_dict(element, orient="columns")

    # varDF["long_name"] = varDF["long_name"].apply(axis=1, func=processWYSIWYG)
    # varDF["unit"] = varDF["unit"].apply(axis=1, func=processWYSIWYG)
    # page width is 426 pts - divide into 3/4 and 1/4 sections for algorithm name and units
    column_format = f"p{{{int(426/4)*3}pt}} p{{{int(426/4)}pt}}"
    if not varDF.empty:
        latexDF = varDF.to_latex(
            index=False,
            bold_rows=True,
            escape=False,
            column_format=column_format,
            na_rep=" ",
            columns=["long_name", "unit"],
            header=["\\textbf{{Name}}", "\\textbf{{Unit}}"],
        )
        return latexDF
    else:
        return ""


def processATBD(element):
    title = macroWrap("ATBDTitle", element["title"])
    try:
        contacts = macroWrap("Contacts", processContacts(element["contacts"]))
    except KeyError:
        return [title]
    return [title, contacts]


# Map variables to be found in JSON to the functions which will correctly format them into their TeX counterparts
mapVars = {
    "scientific_theory": processWYSIWYG,
    "scientific_theory_assumptions": processWYSIWYG,
    "mathematical_theory": processWYSIWYG,
    "mathematical_theory_assumptions": processWYSIWYG,
    "algorithm_input_variables": processVarList,
    "algorithm_output_variables": processVarList,
    "atbd": processATBD,
    "introduction": processWYSIWYG,
    "historical_perspective": processWYSIWYG,
    "algorithm_usage_constraints": processWYSIWYG,
    "performance_assessment_validation_methods": processWYSIWYG,
    "performance_assessment_validation_uncertainties": processWYSIWYG,
    "performance_assessment_validation_errors": processWYSIWYG,
    "algorithm_implementations": processImplementations,
    "data_access_input_data": processDataAccess,
    "data_access_output_data": processDataAccess,
    "data_access_related_urls": processDataAccessURL,
    "journal_discussion": processWYSIWYG,
    "journal_acknowledgements": processWYSIWYG,
}


# Formats each reference in {refs} and appends to the references list which will comprise the BibTex file
def processReferences(refs):
    # create BibTeX
    counter = 1
    for ref in refs:
        identifier = "REF" + num2words(counter)
        if debug:
            print("ref is {}".format(ref))
        this_ref = "\n"
        # currently just for Article
        for element in ["title", "pages", "volume"]:
            if ref[element] is not None:
                this_ref += element.upper() + '="{}", \n'.format(ref[element])
        if ref["authors"] is not None:
            this_ref += "AUTHOR" + '="{}", \n'.format(ref["authors"])
        else:
            this_ref += "key" + '="{}", \n'.format(ref["title"])
        if ref["publisher"] is not None:
            this_ref += "JOURNAL" + '="{}", \n'.format(ref["publisher"])
        if ref["issue"] is not None:
            this_ref += "NUMBER" + '="{}", \n'.format(ref["issue"])
        if ref["year"] is not None:
            this_ref += "YEAR" + '="{}", \n'.format(ref["year"])
        bibtexRef = f"@ARTICLE{{{identifier},{this_ref}}}"
        references.append(bibtexRef)
        refIDs[ref["publication_reference_id"]] = identifier
        counter += 1


# Creates a new TeX variable called {name} and defines it as {value} in the TeX file
def macroWrap(name, value):
    return "\\newcommand{{\\{fn}}}{{{val}}}".format(fn=name, val=value)


def texify(name, element):
    if debug:
        print("name: {} || element: {}".format(name, element))
    elif name in mapVars.keys() and element is not None:
        return macroWrap(toCamelCase(name), mapVars[name](element))
    elif element is None:
        return macroWrap(toCamelCase(name), "Placeholder text")
    else:
        return name


# Include a section at the top of the ATBD which has filetype specific instructions so that images will render correctly in both HTML and PDF
def filetypeSpecific(filetype):
    functionList = []
    if filetype == "HTML":
        functionList.append("\\def\\maxwidth#1{#1}")
        functionList += htmlImgs
    elif filetype == "PDF":
        functionList.append(
            """
        \\makeatletter
        \\def\\maxwidth#1{\\ifdim\\Gin@nat@width>#1 #1\\else\\Gin@nat@width\\fi}
        \\makeatother
        """
        )
        functionList += pdfImgs
    return functionList


class ATBD:
    def __init__(self, path: str, journal: str):
        self.journal = journal
        self.filepath = path

    # Parse the JSON file into the corresponding sections (variables) enumerated in the ATBD
    def texVariables(self):
        myJson = json.loads(open(self.filepath).read())
        processReferences(myJson.pop("publication_references"))
        commands = processATBD(myJson)
        if debug:
            for item, value in myJson.items():
                print("item: {}, value: {}".format(item, value))

        if not self.journal and myJson.get("journal_discussion"):
            del myJson["journal_discussion"]
        if not self.journal and myJson.get("journal_acknowledgements"):
            del myJson["journal_acknowledgements"]

        for k in mapVars.keys():
            commands += [texify(k, myJson.get(k))]
        # commands += [texify(x, y) for x, y in myJson.items() if x in mapVars.keys()]

        if debug:
            print(commands)
        self.texVars = commands

    def nameFile(self, ext):
        atbd_name = self.filepath.rsplit(".json", 1)[0]
        if debug:
            print(atbd_name)
        return f"{atbd_name}.{ext}"

    def filewrite(self):
        atbd_template_file = "ATBD.tex"

        if self.journal:
            atbd_template_file = "ATBD_JOURNAL.tex"

        with open(atbd_template_file, "r") as original:
            data = original.read()

        with open(self.nameFile("tex"), "w") as modified:
            modified.write("\\ifx \\convertType \\undefined \n")
            modified.write("\n".join(filetypeSpecific("HTML")))
            modified.write("\n \\else \n")
            modified.write("\n".join(filetypeSpecific("PDF")))
            modified.write("\n \\fi \n")
            modified.write("\n".join(self.texVars) + " \n" + data)
            fileName = modified.name

        with open(os.path.join(os.path.dirname(fileName), "main.bib"), "w") as bibFile:
            bibFile.write("\n".join(references))
        return fileName

    def placeholder(self, text):
        return [{"object": "text", "leaves": [{"text": text}],}]


def createLatex(atbd_path, journal):

    newTex = ATBD(atbd_path, journal == "True")
    newTex.texVariables()
    texFile = newTex.filewrite()
    print(texFile)


createLatex(sys.argv[1], sys.argv[2])