import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field
from langgraph.graph import END, START, StateGraph
from pydantic import Field
from src.models import Question, QuestionTypes
from src.code_generator.graphs import (
    model,
    resolve_prompt,
    to_serializable,
    save_graph_visualization,
)


class QuestionMetaData(BaseModel):
    title: str = Field(..., description="A concise title summarizing the question")
    qTypes: List[QuestionTypes] = []
    topics: List[str] = Field(
        default=[],
        description="A list of comma seperated values for the topics that represents the question properly",
    )
    isAdaptive: bool


class State(BaseModel):
    question: Question
    metadata: QuestionMetaData | None = Field(
        default=None,
        description="The metadata to generate",
    )
    isAdaptive: bool | None = Field(
        default=None,
        description="Whether the question is adaptive or not. If the None is passed it will auto generate during metadata generation. ",
    )


def generate_question_metadata(state: State):
    question_text = state.question.question_text

    structured_model = model.with_structured_output(QuestionMetaData)
    prompt = resolve_prompt("question_metadata")
    prompt += f"question: {question_text}"
    result = structured_model.invoke(prompt)
    metadata = QuestionMetaData.model_validate(result)

    # Override
    if state.isAdaptive is not None:
        metadata.isAdaptive = state.isAdaptive

    return {"metadata": metadata}


workflow = StateGraph(State)
# Define Nodes
workflow.add_node("generate_question_metadata", generate_question_metadata)
# Connect
workflow.add_edge(START, "generate_question_metadata")
workflow.add_edge("generate_question_metadata", END)

app = workflow.compile()
if __name__ == "__main__":
    question = Question(
        question_text="A car is traveling along a straight rode at a constant speed of 100mph for 5 hours calculate the total distance traveled",
        solution_guide=None,
        final_answer=None,
        question_html="",
    )
    input_state = State(question=question)
    print(input_state)
    result = app.invoke(input_state)  # type: ignore
    print(result["metadata"])

    # Save output
    output_path = Path(r"src/code_generator/outputs/metadata")
    save_graph_visualization(app, output_path, filename="graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
