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


def solution_present(state: State) -> Literal["validate_solution", "improve_code"]:
    if state["question"].solution_guide:
        return "validate_solution"
    return "improve_code"


def validate_solution(state: State):
    solution_guide = state["question"].solution_guide

    input_state: CodeValidationState = {
        "prompt": (
            "You are tasked with analyzing the following HTML solution file. "
            "Verify that the generated HTML is valid, consistent, and follows "
            "the logic described in the provided solution guide.\n\n"
            f"Solution Guide:\n{solution_guide}"
        ),
        "generated_code": state["solution_html"] or "",
        "validation_errors": [],
        "refinement_count": 0,
        "final_code": "",
    }

    result = code_validation_graph.invoke(input_state)  # type: ignore
    final_code = result["final_code"]

    return {"solution_html": final_code}


def improve_code(state: State):
    input_state: CodeValidationState = {
        "prompt": (
            "You are tasked with reviewing and improving the following HTML "
            "solution file. Your goal is to ensure that the code is correct, "
            "clear, and pedagogically aligned with the question context.\n\n"
            "Carefully analyze structure, variable consistency, and mathematical "
            "formatting, then improve readability and correctness while preserving "
            "the intended instructional flow.\n\n"
            f"General Guidelines for Solution File Guide:\n{resolve_prompt('solution_html_graph_prompt')}"
        ),
        "generated_code": state.get("solution_html", "") or "",
        "validation_errors": [],
        "refinement_count": 0,
        "final_code": "",
    }

    result = code_validation_graph.invoke(input_state)  # type: ignore
    final_code = result["final_code"]

    return {"solution_html": final_code}


workflow = StateGraph(State)
workflow.add_node("retrieve_examples", retrieve_examples)
workflow.add_node("generate_code", generate_code)
workflow.add_node("validate_solution", validate_solution)
workflow.add_node("improve_code", improve_code)

workflow.add_edge(START, "retrieve_examples")
workflow.add_conditional_edges(
    "generate_code",
    solution_present,
    {"improve_code": "improve_code", "validate_solution": "validate_solution"},
)
workflow.add_edge("validate_solution", "improve_code")
workflow.add_edge("improve_code", END)
workflow.add_edge("retrieve_examples", END)

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
