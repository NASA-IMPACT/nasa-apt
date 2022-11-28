"""
    Module to process ul, ol, and li items
"""
from pylatex import Itemize, Enumerate

def list_items(data):
    
    if data.get("type") == "li":
        # TODO: confirm whether formatting of list items is allowed
        # if so, a document.TextLeaf type should be used
        # this list is be enumerated so that if multiple paragraph lines, lines can be appended to a single list item
        return [ d['text'] for _indx,d in enumerate(data["children"][0]['children']) ]
        # return process(data["children"][0])

def ul_ol_lists(data):
    
    if data.get("type") in ["ul", "ol"]:
        latex_list = Itemize() if data["type"] == "ul" else Enumerate()
        for child in data["children"]:
            # latex_list.add_item(process(child))
            for item in list_items(child):
                latex_list.add_item(item)
        return latex_list

