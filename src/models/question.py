from typing import Literal
from pydantic import BaseModel, Field

QuestionTypes = Literal[
    "conceptual", "computational", "derivation", "analysis", "design"
]


class Question(BaseModel):
    question_text: str
    solution_guide: str | None
    final_answer: str | None
    question_html: str


class CodeResponse(BaseModel):
    """Output schema from the LLM for code generation."""

    code: str = Field(..., description="The generated code. Only return the code.")


class ValidationResult(BaseModel):
    is_valid: bool = Field(
        ..., description="Is the code valid? based on the requirements"
    )
    errors: list[str] = Field(
        default_factory=list, description="List of validation issues"
    )
    severity: Literal["pass", "warning", "critical"] = Field(...)
