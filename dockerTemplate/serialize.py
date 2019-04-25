import json
import sys
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

def processTable(nodeRows):
    tableList = []
    for row in nodeRows['nodes']:
        tableList.append([])
        for cell in row['nodes']:
            for subcell in cell['nodes']:
                text = processWYSIWYGElement(subcell)
                tableList[-1].append(text)
    columnNames = tableList.pop(0)
    df = pd.DataFrame(tableList, columns=columnNames)
    col_width = int(12/len(df.columns))
    col_format = 'p{' + str(col_width) + 'cm}'
    col_format *= len(df.columns)
    latexTable = '\\\\ \\\\' + \
        df.to_latex(index=False, column_format=col_format) + '\\\\ \\\\'
    return latexTable

def saveImage(imgUrl):
    import requests
    r = requests.get(imgUrl, allow_redirects=True)
    filename = os.path.join(os.getcwd(), 'template/ATBD/imgs', imgUrl.rsplit('/', 1)[1])
    open(filename, 'wb').write(r.content)
    print('IMAGE: ', filename)
    return filename

def wrapImage(img):
    wrapper = f''' \\begin{{center}}
        \\includegraphics[width=\\linewidth]{{{img}}}
        \\end{{center}}
    '''
    return wrapper

def processWYSIWYGElement(node):
    if node['type'] == 'table':
        processTable(node['nodes'])
    elif node['type'] == 'table_cell':
        return processWYSIWYGElement(node['nodes'])
    elif node['type'] != 'image' and node['type'] != 'table':
        text = node['nodes'][0]['leaves'][0]['text']
        if node['type'] == 'equation':
            text = ' \\begin{equation} ' + text + ' \\end{equation} '
        return text
    elif node['type'] == 'image':
        filename = node['data']['src']
        # filename = saveImage(imgUrl)
        return wrapImage(filename)

def processWYSIWYG(element):
    if debug:
        print('element in WYSIWYG is ' + str(element))
    to_return = ''
    for node in element['document']['nodes']:
        to_return += processWYSIWYGElement(node)
    return to_return

def processVarList(element):
    varDF = pd.DataFrame.from_dict(element, orient='columns')
    latexDF = varDF.to_latex(index=False, bold_rows=True, escape=False, column_format='p{9cm} p{3cm}',
        columns=['long_name', 'unit'], header = ['\\textbf{{Name}}', '\\textbf{{Unit}}'])
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

class ATBD:
    def __init__(self, atbd_id, atbd_version, path):
        self.identifier = atbd_id
        self.version = atbd_version
        #TODO: Handle paths locally and pulling from s3
        self.path = path

    def texVariables (self):
        # url = f'http://localhost:3000/atbd_versions?atbd_id=eq.{self.identifier}&atbd_version=eq.{self.version}&select=*,algorithm_input_variables(*),algorithm_output_variables(*),publication_references(*),atbd(*),data_access_input_data(*)'
        # res = requests.get(url)
        # myJson = json.loads(res.text)
        myJson = json.loads(open(self.path).read())
        if debug:
            for item, value in myJson[0].items():
                print('item: {}, value: {}'.format(item, value))
        commands = [texify(x, y) for x,y in myJson[0].items() if x in mapVars.keys()]
        if debug:
            print(commands)
        self.texVars = commands

    def nameFile(self, ext):
        return f'ATBD_{self.identifier}v{self.version}.{ext}'

    def filewrite(self):
        with open(os.path.join(os.getcwd(), 'ATBD.tex'),  'r') as original:
            data = original.read()
        with open(os.path.join(os.getcwd(), self.nameFile('tex')), 'w') as modified:
            modified.write('\n'.join(self.texVars) + ' \n' + data)
            fileName = modified.name
        print(fileName)
        return fileName

    def writeLatex(self, srcFile):
        # temporary: change directory to create pdf in template/ATBD
        # curDir = os.getcwd()
        # outputDir = os.path.join(os.getcwd(), 'template', 'ATBD')
        # os.chdir(outputDir)
        subprocess.check_call(['pdflatex', srcFile])
        # run a second time for table of contents
        subprocess.check_call(['pdflatex', srcFile])
        # os.chdir(curDir)

def createLatex(args):
    print(args)
    atbd_id, atbd_version, atbd_path = args
    newTex = ATBD(atbd_id, atbd_version, atbd_path)
    newTex.texVariables()
    texFile = newTex.filewrite()
    newTex.writeLatex(texFile)

createLatex(sys.argv[1:])
