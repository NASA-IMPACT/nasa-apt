"""
Function to format equations within PDF document
"""
import pydash
from pylatex import NoEscape

# create a placeholder for pydash to handle errors
EQ_PLACEHOLDER = "Error Formatting Equation"


def format(data):
    """
    Formats equations with NoEscape
    """

    eq = pydash.get(obj=data, path="children.0.text", default=EQ_PLACEHOLDER)
    eq = eq.replace("\\\\", "\\")
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
