from __future__ import annotations
from pydantic import BaseModel, validator, root_validator, AnyUrl, Field
from typing import Optional, List, Dict, Any, Union
from enum import Enum


class TextLeaf(BaseModel):
    text: str
    underline: Optional[Union[str, bool]]
    italic: Optional[Union[str, bool]]
    bold: Optional[Union[str, bool]]
    subscript: Optional[Union[str, bool]]
    superscript: Optional[Union[str, bool]]

    @root_validator()
    def validate(cls, values: Dict[str, Union[str, bool]]):
        for v in ["underline", "italic", "bold", "subscript", "superscript"]:
            if isinstance(values.get(v), str):
                if values["text"] == "":
                    raise ValueError(
                        f"Text formatting option {v} cannot be applied to empty text"
                    )
                values[v] = values[v].lower() == "true"

        return values


class TypesEnum(str, Enum):
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


class BaseNode(BaseModel):
    type: str
    children: List[TextLeaf]


class LinkNode(BaseNode):
    type: TypesEnum
    url: AnyUrl
    children: List[TextLeaf]


class ReferenceNode(BaseNode):
    type: TypesEnum
    refId: str
    children: List[TextLeaf]


class DivNode(BaseNode):
    type: TypesEnum
    children: List[Union[TextLeaf, LinkNode, ReferenceNode]]


class OrderedListNode(BaseNode):
    type: TypesEnum
    children: List[ListItemNode]


class UnorderedListNode(BaseNode):
    type: TypesEnum
    children: List[ListItemNode]


class ListItemNode(BaseNode):
    type: TypesEnum
    children: List[Union[DivNode, OrderedListNode, UnorderedListNode]]


OrderedListNode.update_forward_refs()

UnorderedListNode.update_forward_refs()


class SubsectionNode(BaseNode):
    id: str
    type: TypesEnum


class EquationNode(BaseNode):
    type: TypesEnum


class ImageNode(BaseNode):
    type: TypesEnum
    objectKey: str


class CaptionNode(BaseNode):
    type: TypesEnum


class ImageBlockNode(BaseNode):
    type: TypesEnum
    children: List[Union[ImageNode, CaptionNode]]

    @validator("children")
    def validate_children(cls, v):
        if len(v) != 2:
            raise ValueError(
                "`Children` field of `Image-Block` type must contain one `Image` model and one `Caption` model"
            )
        if not (
            all([isinstance(v[0], ImageNode), isinstance(v[0], CaptionNode)])
            or all([isinstance(v[0], CaptionNode), isinstance(v[0], ImageNode)])
        ):
            raise ValueError(
                "`Children` field of `Image-Block` type must contain one `Image` model and one `Caption` model"
            )


class TableCellNode(BaseNode):
    type: TypesEnum
    children: List[DivNode]


class TableRowNode(BaseNode):
    type: TypesEnum
    children: List[TableCellNode]


class TableNode(BaseNode):
    type: TypesEnum
    children: List[TableRowNode]


class TableBlockNode(BaseNode):
    type: TypesEnum
    children: List[Union[TableNode, CaptionNode]]

    @validator("children")
    def validate_children(cls, v):
        if len(v) != 2:
            raise ValueError(
                "`Children` field of `Image-Block` type must contain one `Image` model and one `Caption` model"
            )
        if not (
            all([isinstance(v[0], TableNode), isinstance(v[0], CaptionNode)])
            or all([isinstance(v[0], CaptionNode), isinstance(v[0], TableNode)])
        ):
            raise ValueError(
                "`Children` field of `Image-Block` type must contain one `Image` model and one `Caption` model"
            )


class DataAccessUrl(BaseModel):
    url: AnyUrl
    description: str


class DivWrapperNode(BaseModel):
    children: List[DivNode]


class AlgorithmVariable(BaseModel):
    name: DivWrapperNode
    long_name: DivWrapperNode
    unit: DivWrapperNode


class PublicationReference(BaseModel):
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
    children: List[
        Union[
            ImageBlockNode,
            TableBlockNode,
            DivNode,
            OrderedListNode,
            UnorderedListNode,
            SubsectionNode,
            EquationNode,
        ]
    ]


class Document(BaseModel):
    introduction: Optional[SectionWrapper]
    historical_perspective: Optional[SectionWrapper]
    algorithm_description: Optional[SectionWrapper]
    scientific_theory: Optional[SectionWrapper]
    scientific_theory_assumptions: Optional[SectionWrapper]
    mathematical_theory: Optional[SectionWrapper]
    mathematical_theory_assumptions: Optional[SectionWrapper]
    algorithm_input_variables: Optional[List[AlgorithmVariable]]
    algorithm_output_variables: Optional[List[AlgorithmVariable]]
    algorithm_implementations: Optional[List[DataAccessUrl]]
    algorithm_usage_constraints: Optional[SectionWrapper]
    performance_assessment_validation_methods: Optional[SectionWrapper]
    performance_assessment_validation_uncertainties: Optional[SectionWrapper]
    performance_assessment_validation_errors: Optional[SectionWrapper]
    data_access_input_data: Optional[List[DataAccessUrl]]
    data_access_output_data: Optional[List[DataAccessUrl]]
    data_access_related_urls: Optional[List[DataAccessUrl]]
    journal_dicsussion: Optional[SectionWrapper]
    journal_acknowledgements: Optional[SectionWrapper]
    publication_references: Optional[List[PublicationReference]]

    @validator(
        "algorithm_implementations",
        "data_access_input_data",
        "data_access_output_data",
        "data_access_related_urls",
        whole=True,
    )
    def check_if_list_has_value(cls, value):
        return value or None
