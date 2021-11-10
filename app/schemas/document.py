"""Models for the Versions.document field"""

from __future__ import annotations

import re
from enum import Enum, unique
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AnyUrl, BaseModel, validator


@unique
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

    text: str = ""
    underline: Optional[Union[str, bool]]
    italic: Optional[Union[str, bool]]
    bold: Optional[Union[str, bool]]
    subscript: Optional[Union[str, bool]]
    superscript: Optional[Union[str, bool]]

    @validator("underline", "italic", "bold", "subscript", "superscript")
    def _remove_formatting_if_text_empty(
        cls, v: Union[str, bool], values: Dict[str, Union[str, bool]], field: str
    ) -> bool:
        """Ensure that formatting is not applied to empty text (will break latex)"""

        # cast to bool
        if isinstance(v, str):
            v = v.lower() == "true"

        # set the formatting option to None if no text is present
        # (this happens if multiple lines were bolded, for example)
        if v and not values["text"]:
            return None

        return v


class BaseNode(BaseModel):
    """Generic WYSIWYG node type"""

    type: TypesEnum
    id: Optional[str]
    children: List[TextLeaf]


class LinkNode(BaseNode):
    """href Link WYSIWYG node"""

    type: Literal[TypesEnum.link]
    url: AnyUrl


class ReferenceNode(BaseNode):
    """Reference to bib item WYSIWYG node"""

    type: Literal[TypesEnum.reference]
    refId: str


class DivNode(BaseNode):
    """Generic text container WYSIWYG node"""

    type: Literal[TypesEnum.div]
    children: List[Union[LinkNode, ReferenceNode, TextLeaf]]


class OrderedListNode(BaseNode):
    """Ordered (numerical) List WYSIWYG node"""

    type: Literal[TypesEnum.ordered_list]
    children: List[ListItemNode]


class UnorderedListNode(BaseNode):
    """Unordered (bullet points) list WYSIWYG node"""

    type: Literal[TypesEnum.unordered_list]
    children: List[ListItemNode]


class ListItemNode(BaseNode):
    """List item node that gets wrapped with OrderedList or UnorderedList.
    List items can also contain other orderd or unordered lists"""

    type: Literal[TypesEnum.list_item]
    children: List[Union[OrderedListNode, UnorderedListNode, DivNode]]


# OrderedList and UnorderedList are both possible children
# elements of a ListItem - to avoid circular dependency issues,
# references to ListItems in OrderedListNode and UnorderedListNode are
# suspended and updated after ListItemNode has been evaluated
OrderedListNode.update_forward_refs()
UnorderedListNode.update_forward_refs()


class SubsectionNode(BaseNode):
    """Custom/user defined `sub-sections` items"""

    type: Literal[TypesEnum.subsection]


class EquationNode(BaseNode):
    """Equation WYSIWYG node"""

    type: Literal[TypesEnum.equation]


class ImageNode(BaseNode):
    """Image WYSIWYG node"""

    objectKey: str
    type: Literal[TypesEnum.image]


class CaptionNode(BaseNode):
    """Caption nodes (for Table or Image WYSIWYG nodes)"""

    type: Literal[TypesEnum.caption]
    children: List[Union[LinkNode, ReferenceNode, TextLeaf]]


class ImageBlockNode(BaseNode):
    """Image block node (contains image and caption)"""

    type: Literal[TypesEnum.image_block]
    children: List[Union[CaptionNode, ImageNode]]

    @validator("children")
    def _validate_children(cls, v):
        if len(v) != 2:
            raise ValueError(
                "`Children` field of `Image-Block` type must contain one `Image` model and"
                " one `Caption` model"
            )
        # TODO: make this more pythonic
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

    type: Literal[TypesEnum.table_cell]
    children: List[DivNode]


class TableRowNode(BaseNode):
    """Table row WYSIWYG node"""

    type: Literal[TypesEnum.table_row]
    children: List[TableCellNode]


class TableNode(BaseNode):
    """Table WYSIWYG node"""

    type: Literal[TypesEnum.table]
    children: List[TableRowNode]


class TableBlockNode(BaseNode):
    """Wrapper for Table WYSIWYG node and Caption WYSIWYG nodes"""

    type: Literal[TypesEnum.table_block]
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

    url: Optional[Union[AnyUrl, str]]
    description: Optional[str]

    @validator("url", "description", always=True)
    def _set_empty_if_missing(cls, v: Union[AnyUrl, str]):
        if not v:
            return ""


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
            ImageBlockNode,
            OrderedListNode,
            UnorderedListNode,
            TableBlockNode,
            SubsectionNode,
            EquationNode,
            DivNode,
        ]
    ]


class PublicationUnits(BaseModel):
    """
    Publication Units (contains numbers of words, images and tables)
    """

    words: int = 0
    images: int = 0
    tables: int = 0

    def __add__(self, d: PublicationUnits) -> PublicationUnits:
        """Overloaded `+` operator so that I can combine the publication
        units for 2 leaves (or sub-trees) within a document with a single
        addition operation. Eg:
        >>> leaf_1 = PublicationUnits(words=2, images=2, tables=2)
        >>> leaf_2 = PublicationUnits(words=4, images=4, tables=4)

        >>> sub_tree = leaf_1 + leaf_2
        >>> sub_tree
        PublicationUnits(words=6, images=6, tables=6)
        """
        return PublicationUnits(
            words=self.words + d.words,
            images=self.images + d.images,
            tables=self.tables + d.tables,
        )

    def __radd__(self, d: PublicationUnits) -> PublicationUnits:
        """Overloaded `__radd__` operand (reverse add) in order to enable
        the `sum()` operation (which attempts to add items in reverse if
        it can resolve the types going forward)
        >>> leaf_1 = PublicationUnits(words=2, images=2, tables=2)
        >>> leaf_2 = PublicationUnits(words=4, images=4, tables=4)
        >>> leaf_3 = PublicationUnits(words=6, images=6, tables=6)

        >>> sub_tree = sum([leaf_1, leaf_2, leaf_3])
        >>> sub_tree
        PublicationUnits(words=12, images=12, tables=12ß)

        """
        return PublicationUnits(
            words=d + self.words, images=d + self.images, tables=d + self.tables,
        )


class DocumentSummary(BaseModel):
    """Document node to be returned in the `SummaryOutput` of
    Atbds and AtbdVersions.
    """

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
    publication_units: Optional[PublicationUnits]

    @validator(
        "algorithm_implementations",
        "data_access_input_data",
        "data_access_output_data",
        "data_access_related_urls",
        whole=True,
    )
    def _check_if_list_has_value(cls, value):
        return value or None

    @validator("publication_units", always=True)
    def _generate_publication_units(cls, v, values: Dict[str, Any]) -> PublicationUnits:
        # "words" field is initialized to 58, the number of
        # words in all of the titles of the journal sections
        # TODO: calculate this dynamically based on the sections
        # in the document
        # The following line is ignore because mypy assumes that `sum()`
        # returns a numerical type, and complains that PublicationUnits()
        # can't be added to the PublicationUnits type
        return PublicationUnits(images=0, tables=0, words=58) + sum(  # type: ignore
            [
                # The following line is ignored because of a bug in mypy
                # ref: https://github.com/python/mypy/issues/4290
                cls._count_images_tables_words(v)  # type: ignore
                for k, v in values.items()
                if k not in ["version_description", "plain_summary"]
            ]
        )

    def _count_images_tables_words(doc: Document) -> PublicationUnits:  # noqa: C901
        def _helper(d: Any) -> PublicationUnits:
            if not d or any(
                isinstance(d, i) for i in (bool, PublicationReference, ReferenceNode)
            ):
                return PublicationUnits(images=0, tables=0, words=0)

            if isinstance(d, AlgorithmVariable):
                return _helper(d.name) + _helper(d.unit)

            if isinstance(d, DataAccessUrl):
                return _helper(d.url) + _helper(d.description)

            if isinstance(d, TextLeaf):
                return _helper(d.text)

            if isinstance(d, EquationNode):
                return PublicationUnits(images=0, tables=0, words=1)

            if isinstance(d, TableNode):
                return PublicationUnits(images=0, tables=1, words=0)

            if isinstance(d, ImageNode):
                return PublicationUnits(images=1, tables=0, words=0)

            if isinstance(d, str):
                return PublicationUnits(
                    images=0, tables=0, words=len(re.findall(r"\w+", d))
                )

            if isinstance(d, list):
                # the following line is ignored for the same reason as
                # above - mypy assumes that sum returns a numerical type
                # which is incompatible with the return type of the method
                return sum(_helper(_d) for _d in d)  # type: ignore

            if any(
                isinstance(d, i) for i in (SectionWrapper, DivWrapperNode, BaseNode)
            ):
                return _helper(d.children)

            raise Exception("Unhandled Node!")

        return _helper(doc)
