import json
import operator
from pathlib import Path
from typing import Annotated, List, Literal, TypedDict
from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from src.models import Question, CodeResponse

from . import (
    model,
    resolve_prompt,
    vector_store,
    to_serializable,
)
class State(TypedDict):
    question: Question
    isAdaptive: bool
    question_html: str | None

    retrieved_documents: Annotated[List[Document], operator.add]
    formatted_examples: str


def retrieve_examples(state: State) -> Command[Literal["generate_code"]]:

    question_text = state["question"].question_text
    filter = {
        "isAdaptive": state["isAdaptive"],
        "input_col": "question",
        "output_col": "question.html",
        "output_is_nan": False,
    }

    results = vector_store.similarity_search(
        question_text,
        filter=filter,
        k=2,
    )
    # Format docs
    formatted_docs = "\n".join(p.page_content for p in results)
    return Command(
        update={"formatted_examples": formatted_docs, "retrieved_documents": results},
        goto="generate_code",
    )


def generate_code(state: State):
    question_text = state["question"].question_text
    examples = state["formatted_examples"]
    prompt = resolve_prompt("question_html_graph_prompt")
    prompt += f"""
    question : {question_text}
    examples: {examples}
    """

    structured_model = model.with_structured_output(CodeResponse)
    question_html = structured_model.invoke(prompt)
    question_html = CodeResponse.model_validate(question_html)
    return {"question_html": question_html.code}


workflow = StateGraph(State)
# Define Nodes
workflow.add_node("retrieve_examples", retrieve_examples)
workflow.add_node("generate_code", generate_code)
# Connect
workflow.add_edge(START, "retrieve_examples")
workflow.add_edge("retrieve_examples", END)

app = workflow.compile()
if __name__ == "__main__":
    question = Question(
        question_text="A car is traveling along a straight rode at a constant speed of 100mph for 5 hours calculate the total distance traveled",
        solution_guide=None,
        final_answer=None,
        question_html="",
    )
    input_state: State = {
        "question": question,
        "isAdaptive": False,
        "question_html": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }
    result = app.invoke(input_state)  # type: ignore
    print(result["question_html"])

    # Save output
    output_path = Path(r"src/code_generator/outputs/question_html")
    save_graph_visualization(app, output_path, filename="question_html_graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
