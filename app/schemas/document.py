"""Models for the Versions.document field"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import AnyUrl, BaseModel, root_validator, validator


class TypesEnum(str, Enum):
    """Enum for all possible WYSIWYG node types"""

    link = "a"
    reference = "ref"
    div = "p"
    list_item = "li"
    ordered_list = "ol"
    unordered_list = "ul"
    subsection = "sub-section"
    equation = "equation"
    image = "img"
    image_block = "image-block"
    table_cell = "td"
    table_row = "tr"
    table = "table"
    table_block = "table-block"
    caption = "caption"


class TextLeaf(BaseModel):
    """Leaf Node:"""

    text: str
    underline: Optional[Union[str, bool]]
    italic: Optional[Union[str, bool]]
    bold: Optional[Union[str, bool]]
    subscript: Optional[Union[str, bool]]
    superscript: Optional[Union[str, bool]]

    @root_validator()
    def validate(cls, values: Dict[str, Union[str, bool]]):
        """Ensure that formatting is not applied to empty text (will break latex)"""
        for formatting in ["underline", "italic", "bold", "subscript", "superscript"]:
            if isinstance(values.get(formatting), str):
                if values["text"] == "":
                    raise ValueError(
                        f"Text formatting option {formatting} cannot be applied to empty text"
                    )

                # type ignore below because mypy complains that `.lower()` cannot be
                # applied to values[formatting] because it might be boolean (even
                # though we've already validated that `values[formatting]` is type(str))
                values[formatting] = values[formatting].lower() == "true"  # type: ignore

        return values


class BaseNode(BaseModel):
    """Generic WYSIWYG node type"""

    type: TypesEnum
    id: Optional[str]
    # _type: str
    children: List[TextLeaf]


class LinkNode(BaseNode):
    """href Link WYSIWYG node"""

    # _type: TypesEnum
    url: AnyUrl
    children: List[TextLeaf]


class ReferenceNode(BaseNode):
    """Reference to bib item WYSIWYG node"""

    # _type: TypesEnum
    refId: str
    children: List[TextLeaf]


class DivNode(BaseNode):
    """Generic text container WYSIWYG node"""

    # _type: TypesEnum
    children: List[Union[TextLeaf, LinkNode, ReferenceNode]]


class OrderedListNode(BaseNode):
    """Ordered (numerical) List WYSIWYG node"""

    # _type: TypesEnum
    children: List[ListItemNode]


class UnorderedListNode(BaseNode):
    """Unordered (bullet points) list WYSIWYG node"""

    # _type: TypesEnum
    children: List[ListItemNode]


class ListItemNode(BaseNode):
    """List item node that gets wrapped with OrderedList or UnorderedList.
    List items can also contain other orderd or unordered lists"""

    # _type: TypesEnum
    children: List[Union[DivNode, OrderedListNode, UnorderedListNode]]


# OrderedList and UnorderedList are both possible children
# elements of a ListItem - to avoid circular dependency issues,
# references to ListItems in OrderedListNode and UnorderedListNode are
# suspended and updated after ListItemNode has been evaluated
OrderedListNode.update_forward_refs()
UnorderedListNode.update_forward_refs()


class SubsectionNode(BaseNode):
    """Custom/user defined `sub-sections` items"""

    pass
    # id: str
    # _type: TypesEnum


class EquationNode(BaseNode):
    """Equation WYSIWYG node"""

    pass
    # _type: TypesEnum


class ImageNode(BaseNode):
    """Image WYSIWYG node"""

    # _type: TypesEnum
    objectKey: str


class CaptionNode(BaseNode):
    """Caption nodes (for Table or Image WYSIWYG nodes)"""

    # _type: TypesEnum
    pass


class ImageBlockNode(BaseNode):
    """Image block node (contains image and caption)"""

    # _type: TypesEnum
    children: List[Union[ImageNode, CaptionNode]]

    @validator("children")
    def _validate_children(cls, v):
        if len(v) != 2:
            raise ValueError(
                "`Children` field of `Image-Block` type must contain one `Image` model and"
                " one `Caption` model"
            )
        if not (
            all([isinstance(v[0], ImageNode), isinstance(v[1], CaptionNode)])
            or all([isinstance(v[0], CaptionNode), isinstance(v[1], ImageNode)])
        ):
            raise ValueError(
                "`Children` field of `Image-Block` type must contain one `Image` model and one"
                " `Caption` model"
            )

        return v


class TableCellNode(BaseNode):
    """Table cell WYSIWYG node"""

    # _type: TypesEnum
    children: List[DivNode]


class TableRowNode(BaseNode):
    """Table row WYSIWYG node"""

    # _type: TypesEnum
    children: List[TableCellNode]


class TableNode(BaseNode):
    """Table WYSIWYG node"""

    # _type: TypesEnum
    children: List[TableRowNode]


class TableBlockNode(BaseNode):
    """Wrapper for Table WYSIWYG node and Caption WYSIWYG nodes"""

    # _type: TypesEnum
    children: List[Union[TableNode, CaptionNode]]

    @validator("children")
    def _validate_children(cls, v):
        if len(v) != 2:
            raise ValueError(
                "`Children` field of `Table-Block` type must contain one `Image` model and one"
                " `Caption` model"
            )
        if not (
            all([isinstance(v[0], TableNode), isinstance(v[1], CaptionNode)])
            or all([isinstance(v[0], CaptionNode), isinstance(v[1], TableNode)])
        ):
            raise ValueError(
                "`Children` field of `Table-Block` type must contain one `Image` model and one"
                " `Caption` model"
            )
        return v


class DataAccessUrl(BaseModel):
    """Data Access URL"""

    url: AnyUrl
    description: str


class DivWrapperNode(BaseModel):
    """Div Wrapper Ndoe"""

    children: List[DivNode]


class AlgorithmVariable(BaseModel):
    """Algorithm Input and Output variables"""

    name: DivWrapperNode
    long_name: DivWrapperNode
    unit: DivWrapperNode


class PublicationReference(BaseModel):
    """Publication Reference"""

    id: str
    authors: Optional[str]
    title: Optional[str]
    series: Optional[str]
    edition: Optional[str]
    volume: Optional[str]
    issue: Optional[str]
    publication_place: Optional[str]
    publisher: Optional[str]
    pages: Optional[str]
    isbn: Optional[str]
    year: Optional[str]


class SectionWrapper(BaseModel):
    """Container Node for a document subsection (eg: `algorithm_input_variables`)"""

    children: List[
        Union[
            DivNode,
            SubsectionNode,
            OrderedListNode,
            UnorderedListNode,
            ImageBlockNode,
            TableBlockNode,
            EquationNode,
        ]
    ]


class DocumentSummary(BaseModel):
    """Document node to be returns in the `SummaryOutput` of
    Atbds and AtbdVersions"""

    abstract: Optional[str]


class Document(DocumentSummary):
    """Top level `document` node"""

    version_description: Optional[SectionWrapper]
    introduction: Optional[SectionWrapper]
    historical_perspective: Optional[SectionWrapper]
    additional_information: Optional[SectionWrapper]
    algorithm_description: Optional[SectionWrapper]
    data_availability: Optional[SectionWrapper]
    scientific_theory: Optional[SectionWrapper]
    scientific_theory_assumptions: Optional[SectionWrapper]
    mathematical_theory: Optional[SectionWrapper]
    mathematical_theory_assumptions: Optional[SectionWrapper]
    algorithm_input_variables: Optional[List[AlgorithmVariable]]
    algorithm_input_variables_caption: Optional[str]
    algorithm_output_variables: Optional[List[AlgorithmVariable]]
    algorithm_output_variables_caption: Optional[str]
    algorithm_implementations: Optional[List[DataAccessUrl]]
    algorithm_usage_constraints: Optional[SectionWrapper]
    performance_assessment_validation_methods: Optional[SectionWrapper]
    performance_assessment_validation_uncertainties: Optional[SectionWrapper]
    performance_assessment_validation_errors: Optional[SectionWrapper]
    data_access_input_data: Optional[List[DataAccessUrl]]
    data_access_output_data: Optional[List[DataAccessUrl]]
    data_access_related_urls: Optional[List[DataAccessUrl]]
    journal_discussion: Optional[SectionWrapper]
    journal_acknowledgements: Optional[SectionWrapper]
    publication_references: Optional[List[PublicationReference]]

    @validator(
        "algorithm_implementations",
        "data_access_input_data",
        "data_access_output_data",
        "data_access_related_urls",
        whole=True,
    )
    def _check_if_list_has_value(cls, value):
        return value or None
