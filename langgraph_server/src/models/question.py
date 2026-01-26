from typing import Literal
from pydantic import BaseModel

QuestionTypes = Literal[
    "conceptual", "computational", "derivation", "analysis", "design"
]


class Question(BaseModel):
    question_text: str
    solution_guide: str | None
    final_answer: str | None
    question_html: str
