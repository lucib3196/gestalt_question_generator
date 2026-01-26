from typing import Literal
from pydantic import BaseModel, Field
from . import CodeResponse
class ValidationResult(BaseModel):
    is_valid: bool = Field(
        ..., description="Is the code valid? based on the requirements"
    )
    errors: list[str] = Field(
        default_factory=list, description="List of validation issues"
    )
    severity: Literal["pass", "warning", "critical"] = Field(...)
