"""
Function to format equations within PDF document
"""
from pylatex import NoEscape


def format(data):
    """
    Formats equations with NoEscape
    """
    eq = data["children"][0]["text"].replace("\\\\", "\\")
    return NoEscape(f"\\begin{{equation}}{eq}\\end{{equation}}")


# Sample of data
# {
#     "type": "equation",
#     "id": None,
#     "children": [
#         {
#             "text": "sum_(k=1)^n k = 1+2+ cdots +n=(n(n+1))",
#             "underline": None,
#             "italic": None,
#             "bold": None,
#             "subscript": None,
#             "superscript": None,
#         }
#     ],
# }
