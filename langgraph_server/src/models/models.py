from pydantic import BaseModel, Field
from typing import List


class CodeResponse(BaseModel):
    """Output schema from the LLM for code generation."""

    code: str = Field(..., description="The generated code. Only return the code.")


class PageRange(BaseModel):
    start_page: int
    end_page: int


class Option(BaseModel):
    text: str = Field(..., description="Text of the answer choice.")
    is_correct: bool = Field(
        ..., description="True if this option is the correct answer, otherwise False."
    )


class SectionBreakdown(BaseModel):
    contains: bool = Field(
        ..., description="Whether it contains the section we are looking for"
    )
    sections: List[PageRange] = Field(
        default_factory=list,
        description="List of page ranges of interest (each containing start_page and end_page)",
    )
