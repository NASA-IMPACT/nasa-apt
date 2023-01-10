"""
    Module to process ul, ol, and li items
"""
import pydash
from pylatex import Enumerate, Itemize


def list_items(data):
    """
    Helper function to process unordered and ordered lists
    """
    if data.get("type") == "li":
        # TODO: confirm whether formatting of list items is allowed
        # if so, a document.TextLeaf type should be used
        # this list is be enumerated so that if multiple paragraph lines, lines can be appended to a single list item
        items = pydash.get(obj=data, path="children.0.children")

        return [d.get("text", "") for _indx, d in enumerate(items)]


def ul_ol_lists(data):
    """
    Function to process unordered and ordered lists
    """
    if data.get("type") in ["ul", "ol"]:
        latex_list = Itemize() if data["type"] == "ul" else Enumerate()
        for child in data["children"]:
            # latex_list.add_item(process(child))
            for item in list_items(child):
                latex_list.add_item(item)
        return latex_list
