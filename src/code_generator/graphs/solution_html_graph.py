import json
import operator
from pathlib import Path
from typing import Annotated, List, Literal, TypedDict

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from src.code_generator.graphs import (
    model,
    resolve_prompt,
    vector_store,
    save_graph_visualization,
    to_serializable,
    CodeValidationState,
    code_validation_graph,
)
from src.models import CodeResponse, Question


class State(TypedDict):
    question: Question
    isAdaptive: bool
    solution_html: str | None
    server_file: str | None

    retrieved_documents: Annotated[List[Document], operator.add]
    formatted_examples: str


def retrieve_examples(state: State) -> Command[Literal["generate_code"]]:
    question_html = state["question"].question_html
    if not question_html:
        question_html = state["question"].question_text

    filter = {
        "isAdaptive": state["isAdaptive"],
        "input_col": "question.html",
        "output_col": "solution.html",
        "output_is_nan": False,
    }
    results = vector_store.similarity_search(question_html, k=2, filter=filter)
    formatted_docs = "\n".join(p.page_content for p in results)
    return Command(
        update={"formatted_examples": formatted_docs, "retrieved_documents": results},
        goto="generate_code",
    )


def generate_code(state: State):
    question_html = state["question"].question_html
    if not question_html:
        question_html = state["question"].question_text

    solution = state["question"].solution_guide
    examples = state["formatted_examples"]

    prompt = resolve_prompt("solution_html_graph_prompt")
    prompt += (
        f"""question html {question_html} examples: {examples} solution: {solution}"""
    )

    structured_model = model.with_structured_output(CodeResponse)
    solution_html = structured_model.invoke(prompt)
    solution_html = CodeResponse.model_validate(solution_html)
    return {"solution_html": solution_html.code}


workflow = StateGraph(State)
workflow.add_node("retrieve_examples", retrieve_examples)
workflow.add_node("generate_code", generate_code)


workflow.add_edge(START, "retrieve_examples")
workflow.add_edge("generate_code", END)


app = workflow.compile()

if __name__ == "__main__":
    question = Question(
        question_text="A car is traveling along a straight rode at a constant speed of 100mph for 5 hours calculate the total distance traveled",
        solution_guide=None,
        final_answer=None,
        question_html="A car is traveling along a straight rode at a constant speed of 100mph for 5 hours calculate the total distance traveled",
    )
    input_state: State = {
        "question": question,
        "isAdaptive": True,
        "solution_html": None,
        "retrieved_documents": [],
        "formatted_examples": "",
        "server_file": None,
    }
    result = app.invoke(input_state)  # type: ignore
    print(result["solution_html"])

    output_path = Path(r"src/code_generator/outputs/solution_html")
    save_graph_visualization(app, output_path, filename="graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
