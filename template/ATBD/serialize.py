import requests
import json
from shutil import copyfile
import os
import pandas as pd
import subprocess
from latex import build_pdf

debug = True

# from https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase
def toCamelCase(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)

def processWYSIWYG(element):
    if debug:
        print('element in WYSIWYG is ' + str(element))
    to_return = ''
    for node in element['document']['nodes']:
        if node['type'] != 'image':
            text = node['nodes'][0]['leaves'][0]['text']
            if node['type'] == 'equation':
                text = ' \\begin{equation} ' + text + ' \\end{equation} '
            to_return += text
        else:
            to_return
    return to_return

def processVarList(element):
    varDF = pd.DataFrame.from_dict(element, orient='columns')
    varDF = varDF[['name', 'long_name', 'unit']].rename(
        columns={'name': '\\textbf{{Name}}', 'long_name': '\\textbf{{Long Name}}', 'unit': '\\textbf{{Unit}}'})
    latexDF = varDF.to_latex(index=False, bold_rows=True, escape = False)
    return latexDF

def processATBD(element):
    return element['title']

def processText(element):
    return element

mapVars = {
    'scientific_theory': processWYSIWYG,
    'scientific_theory_assumptions': processWYSIWYG,
    'mathematical_theory': processWYSIWYG,
    'mathematical_theory_assumptions': processWYSIWYG,
    'algorithm_input_variables': processVarList,
    'algorithm_output_variables': processVarList,
    'atbd': processATBD,
    'introduction': processText,
    'historical_perspective': processText
}

def macroWrap(name, value):
    return '\\newcommand{{\\{fn}}}{{{val}}}'.format(fn=name, val=value)

def texify (name, element):
    if debug:
        print('name: {} || element: {}'.format(name, element))
    if name == 'atbd':
        return macroWrap('ATBDTitle', processATBD(element))
    elif name in mapVars.keys() and element is not None:
        return macroWrap(toCamelCase(name), mapVars[name](element))
    elif element is None:
        return macroWrap(toCamelCase(name), 'Lorem Ipsum Filler text')
    else:
        return name

def texVariables (ID, version):
    url = f'http://localhost:3000/atbd_versions?atbd_id=eq.{ID}&atbd_version=eq.{version}&select=*,algorithm_input_variables(*),publication_references(*),atbd(*),data_access_input_data(*)'
    res = requests.get(url)
    myJson = json.loads(res.text)
    if debug:
        for item, value in myJson[0].items():
            print('item: {}, value: {}'.format(item, value))
    commands = [texify(x, y) for x,y in myJson[0].items() if x in mapVars.keys()]
    if debug:
        print(commands)
    return commands

def nameFile(ID, version, ext):
    return f'ATBD_{ID}v{version}.{ext}'

def filewrite(prepend, ID, version):
    with open(os.path.join(os.getcwd(), 'template', 'ATBD', 'ATBD.tex'),  'r') as original:
        data = original.read()
    with open(os.path.join(os.getcwd(), 'template', 'ATBD', nameFile(ID, version, 'tex')), 'w') as modified:
        modified.write('\n'.join(prepend) + ' \n' + data)
        fileName = modified.name
    return fileName

def writeLatex(srcFile, ID, version):
    # temporary: change directory to create pdf
    curDir = os.getcwd()
    outputDir = os.path.join(os.getcwd(), 'template', nameFile(ID, version, 'pdf'))
    os.chdir(outputDir)
    subprocess.check_call(['pdflatex', srcFile])
    # run a second time for table of contents
    subprocess.check_call(['pdflatex', srcFile])
    os.chdir(curDir)

def createLatex(atbd_id, atbd_version):
    to_prepend = texVariables(atbd_id, atbd_version)
    texFile = filewrite(to_prepend, atbd_id, atbd_version)
    writeLatex(texFile, atbd_id, atbd_version)

createLatex(1, 1)
