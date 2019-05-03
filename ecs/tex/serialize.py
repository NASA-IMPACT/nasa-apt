import json
import sys
from shutil import copyfile
import os
import pandas as pd
import subprocess
from latex import build_pdf
from num2words import num2words

debug = False
pdfImgs = []
htmlImgs = []

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

def saveImage(imgUrl, img):
    imgLink = num2words(len(pdfImgs))
    pdfImgs.append(r'\immediate\write18{wget "' + imgUrl + f'"}} \n \\newcommand{{\\{imgLink}}}{{{img}}}')
    htmlImgs.append(f'\\newcommand{{\\{imgLink}}}{{{imgUrl}}}')
    return imgLink

def wrapImage(img):
    wrapper = f''' \\begin{{center}}
        \\includegraphics[width=\\linewidth]{{\\{img}}}
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
        imgUrl = node['data']['src']
        filename = imgUrl.rsplit('/', 1)[1]
        imgCommand = saveImage(imgUrl, filename)
        return wrapImage(imgCommand)

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
    def __init__(self, path):
        #TODO: Handle paths locally and pulling from s3
        self.filepath = path

    def texVariables (self):
        myJson = json.loads(open(self.filepath).read())
        if debug:
            for item, value in myJson[0].items():
                print('item: {}, value: {}'.format(item, value))
        commands = [texify(x, y) for x,y in myJson[0].items() if x in mapVars.keys()]
        if debug:
            print(commands)
        self.texVars = commands

    def nameFile(self, ext):
        atbd_name = self.filepath.rsplit('.json', 1)[0]
        if debug:
            print(atbd_name)
        return f'{atbd_name}.{ext}'

    def filewrite(self):
        with open(os.path.join('ATBD.tex'),  'r') as original:
            data = original.read()
        with open(os.path.join(self.nameFile('tex')), 'w') as modified:
            modified.write('\\ifx \\convertType \\undefined \n')
            modified.write('\n'.join(pdfImgs))
            modified.write('\n \\else \n')
            modified.write('\n'.join(htmlImgs))
            modified.write('\n \\fi \n')
            modified.write('\n'.join(self.texVars) + ' \n' + data)
            fileName = modified.name
        if debug:
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
    # print(args)
    atbd_path = args
    newTex = ATBD(atbd_path)
    newTex.texVariables()
    texFile = newTex.filewrite()
    print(texFile)
    # newTex.writeLatex(texFile)

createLatex(sys.argv[1])
