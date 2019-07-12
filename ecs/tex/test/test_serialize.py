
import os
import sys
import json 

sys.path.append(os.getcwd())

from serialize import processTable, processWYSIWYGElement, processWYSIWYG, mapVars

from table2import import tablejson
from text import textjson

#TODO: Decide if it's useful to add tests for more elements which do not use ProcessWYSIWYG
uncodedVars = ["atbd_version", "atbd_id", "status", "publication_references"]
excludedVars = ["atbd"]

#TODO: Add tests for algorithm input/output variables
def test_table():
    tableInfo = processWYSIWYGElement(tablejson)
    print(tableInfo[0], tableInfo[1])
    assert tableInfo[0] == '\n \n\\begin{tabular}{ll}\n\\toprule\n                      A &                       B \\\\\n\\midrule\n \\underline{\\textit{C}} &  \\underline{\\textit{D}} \\\\\n\\bottomrule\n\\end{tabular}\n\n \n'
    assert tableInfo[1] == 'table'

#TODO: Add tests for super/subscript, hyperlink, and B/I/U
def test_text():
    textInfo = processWYSIWYGElement(textjson)
    print(textInfo[0], textInfo[1])
    assert textInfo[0] == 'A line of text in a paragraph.'
    assert textInfo[1] == 'text'

def test_full():
    myJson = json.loads(open('test/full.json').read())
    for name, element in myJson.items():
        print(name, element)
        if name not in mapVars.keys():
            assert name in uncodedVars
        elif name not in excludedVars and element is not None:
            assert isinstance(mapVars[name](element), str)

if __name__ == '__main__':
    test_table()
    test_text()
    test_full()

