import json
import operator
import os
from pathlib import Path
from typing import Annotated, List, Literal, TypedDict

from langchain_astradb import AstraDBVectorStore
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langsmith import Client

from src.code_validation import CodeValidationState, code_validation_graph
from src.models import CodeResponse, Question
from src.utils import (
    save_graph_visualization,
    to_serializable,
)


model = init_chat_model(
    model="gpt-4o",
    model_provider="openai",
)
embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDINGS", ""),
)
client = Client()
base_prompt = client.pull_prompt("solution_html_graph_prompt")
if isinstance(base_prompt, str):
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(base_prompt)
else:
    prompt: ChatPromptTemplate = base_prompt

vector_store = AstraDBVectorStore(
    collection_name="gestalt_module",
    embedding=embeddings,
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT", None),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN", None),
    namespace=os.getenv("ASTRA_DB_KEYSPACE", None),
)


class State(TypedDict):
    question: Question
    isAdaptive: bool
    solution_html: str | None
    server_file: str | None

    retrieved_documents: Annotated[List[Document], operator.add]
    formatted_examples: str


def retrieve_examples(state: State) -> Command[Literal["generate_code"]]:
    filter = {
        "isAdaptive": state["isAdaptive"],
        "input_col": "question.html",
        "output_col": "solution.html",
        "output_is_nan": False,
    }
    question_html = state["question"].question_html
    if not question_html:
        question_html = state["question"].question_text
    results = vector_store.similarity_search(question_html, k=2, filter=filter)
    # Format docs
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
    messages = prompt.format_prompt(
        question=question_html, examples=examples, solution=solution
    ).to_messages()

    structured_model = model.with_structured_output(CodeResponse)
    solution_html = structured_model.invoke(messages)
    solution_html = CodeResponse.model_validate(solution_html)
    return {"solution_html": solution_html.code}


def solution_present(state: State) -> Literal["validate_solution", "END"]:
    if state["question"].solution_guide:
        return "validate_solution"
    return "END"


def validate_server(state: State):
    server_file = state["server_file"]
    if not server_file:
        return

    input_state: CodeValidationState = {
        "prompt": f"""
        You are validating a generated HTML solution file.

        Context:
        - A server file may be provided. This server file is responsible for
        generating values, parameters, or logic that the solution HTML depends on.
        - The solution HTML consumes outputs from the server file but does not
        reimplement its logic.

        Your task:
        - Validate that the solution HTML is consistent with the server file’s
        generated values and intended behavior.
        - Ensure variable names, identifiers, and references used in the solution
        HTML match those produced or exposed by the server file.
        - Verify that the solution logic is coherent, executable, and internally
        consistent.
        - Do NOT change the problem statement or pedagogical intent.
        - Do NOT add new logic that does not exist in the server file or solution.

        Server File:
        {server_file}
        """,
        "generated_code": state["solution_html"] or "",
        "validation_errors": [],
        "refinement_count": 0,
        "final_code": "",
    }

    result = code_validation_graph.invoke(input_state)  # type: ignore
    final_code = result["final_code"]

    return {"solution_html": final_code}


def server_present(state: State) -> Literal["validate_server", "END"]:
    if state["server_file"]:
        return "validate_server"
    return "END"


def validate_solution(state: State):
    solution_guide = state["question"].solution_guide

    input_state: CodeValidationState = {
        "prompt": f"""You are tasked with analyzing the following HTML file 
            "containing a solution guide. Verify that the solution guide 
            "HTML correctly follows the provided solution.
            "Solution Guide {solution_guide } """,
        "generated_code": state["solution_html"] or "",
        "validation_errors": [],
        "refinement_count": 0,
        "final_code": "",
    }

    # Run the code validation refinement graph
    result = code_validation_graph.invoke(input_state)  # type: ignore
    final_code = result["final_code"]

    return {"solution_html": final_code}


workflow = StateGraph(State)
# Define Nodes
workflow.add_node("retrieve_examples", retrieve_examples)
workflow.add_node("generate_code", generate_code)
workflow.add_node("validate_solution", validate_solution)
workflow.add_node("validate_server", validate_server)
# Connect
workflow.add_edge(START, "retrieve_examples")
workflow.add_conditional_edges(
    "generate_code",
    solution_present,
    {"END": END, "validate_solution": "validate_solution"},
)
workflow.add_conditional_edges(
    "validate_solution",
    server_present,
    {"END": END, "validate_server": "validate_server"},
)
workflow.add_edge("validate_solution", END)
workflow.add_edge("validate_server", END)
workflow.add_edge("retrieve_examples", END)

# memory = MemorySaver()
# app = workflow.compile(checkpointer=memory)
app = workflow.compile()
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "customer_123"}}
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
    result = app.invoke(input_state, config=config)  # type: ignore
    print(result["solution_html"])

    # Save output
    output_path = Path(
        r"langgraph_server/gestalt_graphs/code_generator/outputs/solution_html"
    )
    save_graph_visualization(app, output_path, filename="graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
