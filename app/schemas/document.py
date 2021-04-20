from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any, Union, ForwardRef
from enum import Enum


class WysiwygText(BaseModel):
    text: str
    underline: Optional[Any]
    italic: Optional[Any]
    bold: Optional[Any]
    subscript: Optional[Any]
    superscript: Optional[Any]


class WysiwygElementTypes(str, Enum):
    div: str = "p"
    link: str = "a"
    reference: str = "ref"
    equation: str = "equation"
    subsection: str = "sub-section"
    image: str = "img"


WysiwygElement = ForwardRef("WysiwygElement")


class WysiwygElement(BaseModel):

    refId: Optional[str]
    url: Optional[str]
    objectKey: Optional[str]  # TODO: S3 format object key check?
    type: WysiwygElementTypes
    children: List[Union[WysiwygElement, WysiwygText]]

    @validator("type",)
    def validate(cls, v, values, **kwargs):
        if v == "ref" and values.get("refId") is None:
            raise ValueError(
                "WYSIWYG Element with type `ref` must contain a field `refId"
            )
        if v == "a" and values.get("url") is None:
            raise ValueError("WYSIWYG Element with type `a` must contain a field `url`")
        if v == "img" and values.get("objectKey") is None:
            raise ValueError(
                "WYSIWYG Element with type `img` must contain a field `objectKey`"
            )
        return v


# Allows us to use WysiwygElement as a type within itself
WysiwygElement.update_forward_refs()


class WysiwygListTypes(str, Enum):
    ordered_list: str = "ol"
    unordered_list: str = "ul"


class WysiwygListItems(BaseModel):
    type: str = "li"
    children: List[WysiwygElement]


class WysiwygList(BaseModel):
    type: WysiwygListTypes
    children: List


class WysiwygContent(BaseModel):
    children: Optional[List[Union[WysiwygList, WysiwygElement]]]


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


class DataAccessUrl(BaseModel):
    url: Optional[str]  # TODO: URL formatting check?
    description: Optional[str]


class Document(BaseModel):

    introduction: Optional[WysiwygContent]
    historical_perspective: Optional[WysiwygContent]
    algorithm_description: Optional[WysiwygContent]
    scientific_theory: Optional[WysiwygContent]
    scientific_theory_assumptions: Optional[WysiwygContent]

    mathematical_theory: Optional[WysiwygContent]
    mathematical_theory_assumptions: Optional[WysiwygContent]

    algorithm_input_variables: Optional[List]

    algorithm_output_variables: Optional[List]

    algorithm_implementations: Optional[List[DataAccessUrl]]

    algorithm_usage_constraints: Optional[WysiwygContent]

    performance_assessment_validation_methods: Optional[WysiwygContent]
    performance_assessment_validation_uncertainties: Optional[WysiwygContent]
    performance_assessment_validation_errors: Optional[WysiwygContent]

    data_access_input_data: Optional[List[DataAccessUrl]]
    data_access_output_data: Optional[List[DataAccessUrl]]
    data_access_related_urls: Optional[List[DataAccessUrl]]

    journal_dicsussion: Optional[WysiwygContent]
    journal_acknowledgements: Optional[WysiwygContent]
    contacts: Optional[Dict]  # TODO: class for contacts
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
