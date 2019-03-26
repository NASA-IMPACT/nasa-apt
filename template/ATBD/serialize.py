import requests
import json
from shutil import copyfile
import os
import pandas as pd

# from https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase
def toCamelCase(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)

def processWYSIWYG(element):
    print('element 2 is ' + str(element))
    to_return = ''
    for sub in element['document']['nodes']:
        print('sub is ' + str(sub))
        if sub['type'] != 'image':
            text = sub['nodes'][0]['leaves'][0]['text']
            if sub['type'] == 'equation':
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

mapVars = {
    'scientific_theory': processWYSIWYG,
    'scientific_theory_assumptions': processWYSIWYG,
    'mathematical_theory': processWYSIWYG,
    'mathematical_theory_assumptions': processWYSIWYG,
    'algorithm_input_variables': processVarList,
    'algorithm_output_variables': processVarList
}

def macroWrap(name, value):
    return '\\newcommand{{\\{fn}}}{{{val}}}'.format(fn=name, val=value)


def helperTwo (name, element):
    print('name: {} || element: {}'.format(name, element))
    if name in mapVars.keys() and element is not None:
        return macroWrap(toCamelCase(name), mapVars[name](element))
    elif element is None:
        return macroWrap(toCamelCase(name), 'Lorem Ipsum Filler text')
    else:
        return name

def helper ():
    res = requests.get('http://localhost:3000/atbd_versions?atbd_id=eq.1&atbd_version=eq.1&select=*,algorithm_input_variables(*),publication_references(*),atbd(*),data_access_input_data(*)')
    myJson = json.loads(res.text)
    for item, value in myJson[0].items():
        print('item: {}, value: {}'.format(item, value))
    commands = [helperTwo(x, y) for x,y in myJson[0].items() if x in mapVars.keys()]
    return commands

def filewrite():
    add = helper()
    with open(os.path.join(os.getcwd(), 'template', 'ATBD', 'ATBD.tex'),  'r') as original:
        data = original.read()
    with open(os.path.join(os.getcwd(), 'template', 'ATBD', 'ATBD2.tex'), 'w') as modified:
        modified.write(
            '\n'.join(add) + " \n" + data)

filewrite()
