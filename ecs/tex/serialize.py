import json
import sys
from shutil import copyfile
import os
import pandas as pd
from latex import build_pdf
from num2words import num2words
from functools import reduce

debug = False
pdfImgs = []
htmlImgs = []
references = []
refIDs = {}

# from https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase
def toCamelCase(snake_str):
    components = snake_str.split('_')
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return ''.join(x.title() for x in components)

def toSpaceCase(snake_str):
    components = snake_str.split('_')
    return ' '.join(x.title() for x in components)

def processTable(nodeRows):
    tableList = []
    for rows in nodeRows:
        tableList.append([])
        for row in rows['nodes']:
            for cell in row['nodes']:
                for subcell in cell['nodes']:
                    for cellnode in subcell['leaves']:
                        tableList[-1].append(cellnode['text'])
    columnNames = tableList.pop(0)
    df = pd.DataFrame(tableList, columns=columnNames)
    col_width = int(12/len(df.columns))
    col_format = 'p{' + str(col_width) + 'cm}'
    col_format *= len(df.columns)
    latexTable = df.to_latex(index=False, column_format=col_format)
    return latexTable

def addMarkup(text, marks):
    for mark in marks:
        markupType = mark['type']
        if markupType == 'italic':
            text= f'\\textit{{{text}}}'
        elif markupType == 'bold':
            text= f'\\textbf{{{text}}}'
        elif markupType == 'underline':
            text= f'\\underline{{{text}}}'
    return text

def preserveStyle(text):
    text = text.encode("unicode_escape").decode(
        "utf-8").replace('\\n', '\\\\')
    while (text[:2].strip() == '\\\\'):
        text=text[2:]
    while (text[-2:].strip() == '\\\\'):
        text=text[:-2]
    return text

def processText(nodes):
    to_return = ''
    for node in nodes:
        if node['object'] == 'text':
            for leaf in node['leaves']:
                if 'marks' in leaf and leaf['marks']:
                    to_return += addMarkup(preserveStyle(leaf['text']), leaf['marks'])
                else:
                    to_return += preserveStyle(leaf['text'])
        elif node['object'] == 'inline' and node['type'] == 'link':
            url = node['data']['url']
            url_nodes = node['nodes']
            to_return += f'\\href{{{url}}}{{{processText(url_nodes)}}}'
        elif node['object'] == 'inline' and node['type'] == 'reference':
            try:
                refID = refIDs[node['data']['id']]
                to_return += f'\\cite{{{refID}}}'
            except KeyError:
                to_return += ''
    return to_return

def saveImage(imgUrl, img):
    imgLink = num2words(len(pdfImgs))
    pdfImgs.append(r'\immediate\write18{wget "' + imgUrl + f'"}} \n \\newcommand{{\\{imgLink}}}{{{img}}}')
    htmlImgs.append(f'\\newcommand{{\\{imgLink}}}{{{imgUrl}}}')
    return imgLink

def wrapImage(img, cap=''):
    if cap:
        cap = f'\\caption{{{cap}}}'
    wrapper = f''' \\begin{{figure}}
        \\includegraphics[width=\\maxwidth{{\\linewidth}}]{{\\{img}}}
        {cap}
        \\end{{figure}}
    '''
    return wrapper

def processWYSIWYGElement(node, text_prepend=''):
    if node['type'] == 'table':
        return processTable(node['nodes'])
    elif node['type'] == 'table_cell':
        return processWYSIWYGElement(node['nodes'])
    elif node['type'] == 'image':
        imgUrl = node['data']['src']
        filename = imgUrl.rsplit('/', 1)[1]
        imgCommand = saveImage(imgUrl, filename)
        try:
            caption = node['data']['caption']
            return wrapImage(imgCommand, caption)
        except:
            return wrapImage(imgCommand)
    elif node['type'] == 'equation':
        return ' \\begin{equation} ' + \
            node['nodes'][0]['leaves'][0]['text'] + ' \\end{equation} '
    elif node['type'] == 'paragraph':
        return text_prepend + processText(node['nodes'])
    else:
        print('oops! here with {}'.format(node))

def processWYSIWYG(element, text_prepend=''):
    if debug:
        print('element in WYSIWYG is ' + str(element))
    to_return = ''
    for node in element['document']['nodes']:
        returned = processWYSIWYGElement(node, text_prepend)
        if returned: #ignore newlines at the beginning
            to_return += returned
            text_prepend = '\\\\\\\\'
    return to_return

def accessURL(url):
    return f'\\textbf{{Access URL: }} {{{url}}} \\\\'

def simpleList(name, item):
    return f'\\textbf{{{toSpaceCase(name)}: }} {item} \\\\'

def processImplementations(collection):
    return reduce((lambda x, y: x + y),
                  list(map(lambda x: '\\subsection {}' + processWYSIWYG(x['execution_description']) + '\\\\' + simpleList('access_url', x['access_url']), collection)), '')
                  # accessURL(x['access_url']) + f'\\textbf{{Description: }}' + processWYSIWYG(x['execution_description']) + '\\\\', collection)), '')

def processContacts(collection):
    allContacts = ''
    for contact in collection:
        if contact['middle_name'] is not None:
            contactString = contact['first_name'] + ' ' + \
                contact['middle_name'] + ' ' + contact['last_name']
        else:
            contactString = contact['first_name'] + ' ' + contact['last_name']
        contactString += ' \\\\ '
        contactString += simpleList('uuid', contact['uuid']) if contact['uuid'] is not None else ''
        for attribute in ["contact_mechanism_type", "contact_mechanism_value"]:
            contactString += simpleList(attribute, contact[attribute]) if contact[attribute] is not None else ''
        allContacts += '\\subsection{} ' + contactString
    return allContacts

def processVarList(element):
    varDF = pd.DataFrame.from_dict(element, orient='columns')
    latexDF = varDF.to_latex(index=False, bold_rows=True, escape=False, column_format='p{9cm} p{3cm}',
        columns=['long_name', 'unit'], header = ['\\textbf{{Name}}', '\\textbf{{Unit}}'])
    return latexDF

def processATBD(element):
    title = macroWrap('ATBDTitle', element['title'])
    try:
        contacts = macroWrap('Contacts', processContacts(element['contacts']))
    except KeyError:
        return [title]
    return [title, contacts]

mapVars = {
    'scientific_theory': processWYSIWYG,
    'scientific_theory_assumptions': processWYSIWYG,
    'mathematical_theory': processWYSIWYG,
    'mathematical_theory_assumptions': processWYSIWYG,
    'algorithm_input_variables': processVarList,
    'algorithm_output_variables': processVarList,
    'atbd': processATBD,
    'introduction': processWYSIWYG,
    'historical_perspective': processWYSIWYG,
    'algorithm_usage_constraints': processWYSIWYG,
    'performance_assessment_validation_methods': processWYSIWYG,
    'performance_assessment_validation_uncertainties': processWYSIWYG,
    'performance_assessment_validation_errors': processWYSIWYG,
    'algorithm_implementations': processImplementations,
    'contacts': processContacts
}

def processReferences(refs):
    # create BibTeX
    counter = 1
    for ref in refs:
        identifier = 'REF'+ num2words(counter)
        if debug:
            print('ref is {}'.format(ref))
        this_ref = '\n'
        # currently just for Article
        for element in ['title', 'pages', 'volume']:
            if ref[element] is not None:
                this_ref += element.upper() + '="{}", \n'.format(ref[element])
        if ref['authors'] is not None:
            this_ref += 'AUTHOR' + '="{}", \n'.format(ref['authors'])
        else:
            this_ref += 'key' + '="{}", \n'.format(ref['title'])
        if ref['publisher'] is not None :
            this_ref += 'JOURNAL' + '="{}", \n'.format(ref['publisher'])
        if ref['issue'] is not None:
            this_ref += 'NUMBER' + '="{}", \n'.format(ref['issue'])
        if ref['publication_date'] is not None:
            this_ref += 'YEAR' + '="{}", \n'.format(ref['publication_date'])
        bibtexRef = f'@ARTICLE{{{identifier},{this_ref}}}'
        references.append(bibtexRef)
        refIDs[ref['publication_reference_id']] = identifier
        counter +=1

def macroWrap(name, value):
    return '\\newcommand{{\\{fn}}}{{{val}}}'.format(fn=name, val=value)

def texify (name, element):
    if debug:
        print('name: {} || element: {}'.format(name, element))
    elif name in mapVars.keys() and element is not None:
        return macroWrap(toCamelCase(name), mapVars[name](element))
    elif element is None:
        return macroWrap(toCamelCase(name), '')
    else:
        return name

def filetypeSpecific(filetype):
    functionList = []
    if filetype == 'HTML':
        functionList.append('\\def\\maxwidth#1{#1}')
        functionList += htmlImgs
    elif filetype == 'PDF':
        functionList.append(
        '''
        \\makeatletter
        \\def\\maxwidth#1{\\ifdim\\Gin@nat@width>#1 #1\\else\\Gin@nat@width\\fi}
        \\makeatother
        ''')
        functionList += pdfImgs
    return functionList

class ATBD:
    def __init__(self, path):
        #TODO: Handle paths locally and pulling from s3
        self.filepath = path

    def texVariables (self):
        myJson = json.loads(open(self.filepath).read())
        processReferences(myJson.pop('publication_references'))
        commands = processATBD(myJson.pop('atbd'))
        if debug:
            for item, value in myJson.items():
                print('item: {}, value: {}'.format(item, value))
        commands += [texify(x, y) for x,y in myJson.items() if x in mapVars.keys()]
        if debug:
            print(commands)
        self.texVars = commands

    def nameFile(self, ext):
        atbd_name = self.filepath.rsplit('.json', 1)[0]
        if debug:
            print(atbd_name)
        return f'{atbd_name}.{ext}'

    def filewrite(self):
        with open('ATBD.tex',  'r') as original:
            data = original.read()
        with open(self.nameFile('tex'), 'w') as modified:
            modified.write('\\ifx \\convertType \\undefined \n')
            modified.write('\n'.join(filetypeSpecific('HTML')))
            modified.write('\n \\else \n')
            modified.write('\n'.join(filetypeSpecific('PDF')))
            modified.write('\n \\fi \n')
            modified.write('\n'.join(self.texVars) + ' \n' + data)
            fileName = modified.name
        with open(os.path.join(os.path.dirname(fileName), 'main.bib'), 'w') as bibFile:
            bibFile.write('\n'.join(references))
        return fileName

def createLatex(args):
    atbd_path = args
    newTex = ATBD(atbd_path)
    newTex.texVariables()
    texFile = newTex.filewrite()
    print(texFile)

createLatex(sys.argv[1])
