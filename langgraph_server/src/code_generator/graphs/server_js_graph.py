# --- Standard Library ---
import json
import operator
import os
from pathlib import Path
from typing import Annotated, List, Literal, TypedDict, Dict

# --- Local / Project Models ---
from langgraph_server.gestalt_graphs.models  import (
    Question,
    CodeResponse,
)

# --- LangChain Integrations ---
from langchain_openai import OpenAIEmbeddings
from langchain_astradb import AstraDBVectorStore
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

# --- LangGraph ---
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langgraph_server.gestalt_graphs.code_validation.graph import (
    State as CodeValidationState,
    graph as code_validation_graph,
)

# --- Project Utilities ---
from langgraph_server.gestalt_graphs.utils.utils import (
    save_graph_visualization,
    to_serializable,
    extract_langsmith_prompt,
)


# --- External Services ---
from langsmith import Client

model = init_chat_model(
    model="gpt-4o",
    model_provider="openai",
)
embeddings = OpenAIEmbeddings(
    model=os.getenv("EMBEDDINGS", ""),
)

vector_store = AstraDBVectorStore(
    collection_name="gestalt_module",
    embedding=embeddings,
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT", None),
    token=os.getenv("ASTRA_DB_APPLICATION_TOKEN", None),
    namespace=os.getenv("ASTRA_DB_KEYSPACE", None),
)

client = Client()
base_prompt = client.pull_prompt("server_js_graph_prompt")
if isinstance(base_prompt, str):
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_template(base_prompt)
else:
    prompt: ChatPromptTemplate = base_prompt


class State(TypedDict):
    question: Question
    isAdaptive: bool
    server_js: str | None

    retrieved_documents: Annotated[List[Document], operator.add]
    formatted_examples: str


def retrieve_examples(state: State) -> Command[Literal["generate_code"]]:

    question_html = state["question"].question_html
    if not question_html:
        question_html = state["question"].question_text

    filter = {
        "isAdaptive": state["isAdaptive"],
        "input_col": "question.html",
        "output_col": "server.js",
        "output_is_nan": False,
    }
    results = vector_store.similarity_search(question_html, k=2, filter=filter)
    # Format docs
    formatted_docs = "\n".join(p.page_content for p in results)
    return Command(
        update={"formatted_examples": formatted_docs, "retrieved_documents": results},
        goto="generate_code",
    )


def generate_code(state: State):
    solution = state["question"].solution_guide
    examples = state["formatted_examples"]

    question_html = state["question"].question_html
    if not question_html:
        question_html = state["question"].question_text

    messages = prompt.format_prompt(
        question=question_html, examples=examples, solution=solution
    ).to_messages()

    structured_model = model.with_structured_output(CodeResponse)
    server = structured_model.invoke(messages)
    server = CodeResponse.model_validate(server)
    return {"server_js": server.code}


def solution_present(state: State) -> Literal["validate_solution", "improve_code"]:
    if state["question"].solution_guide:
        return "validate_solution"
    return "improve_code"


def validate_solution(state: State):
    solution_guide = state["question"].solution_guide

    input_state: CodeValidationState = {
        "prompt": (
            "You are tasked with analyzing the following Javascript server file. "
            "Verify that the generated code is valid, consistent, and follows "
            "the logic described in the provided solution guide.\n\n"
            f"Solution Guide:\n{solution_guide}"
        ),
        "generated_code": state["server_js"] or "",
        "validation_errors": [],
        "refinement_count": 0,
        "final_code": "",
    }

    # Run the code validation refinement graph
    result = code_validation_graph.invoke(input_state)  # type: ignore

    final_code = result["final_code"]

    return {"server_js": final_code}


def improve_code(state: State):
    input_state: CodeValidationState = {
        "prompt": (
            "You are tasked with reviewing and improving the following Python "
            "server file. Your goal is to ensure that the code is correct, "
            "numerically consistent, and integrates dynamic unit handling "
            "based on the problem statement.\n\n"
            "Carefully analyze the logic, verify alignment with the solution "
            "guide, and update the code to properly account for variable units, "
            "scaling factors, or engineering constants that may be required.\n\n"
            f"General Guidelines for Server File Guide:\n{extract_langsmith_prompt(base_prompt)}"
        ),
        "generated_code": state.get("server_js", "") or "",
        "validation_errors": [],
        "refinement_count": 0,
        "final_code": "",
    }

    # Execute the refinement / validation graph
    result = code_validation_graph.invoke(input_state)  # type: ignore

    final_code = result["final_code"]

    return {"server_js": final_code}


workflow = StateGraph(State)
# Define Nodes
workflow.add_node("retrieve_examples", retrieve_examples)
workflow.add_node("generate_code", generate_code)
workflow.add_node("validate_solution", validate_solution)
workflow.add_node("improve_code", improve_code)
# Connect
# Connect
workflow.add_edge(START, "retrieve_examples")
workflow.add_conditional_edges(
    "generate_code",
    solution_present,
    {"improve_code": "improve_code", "validate_solution": "validate_solution"},
)
workflow.add_edge("validate_solution", "improve_code")
workflow.add_edge("improve_code", END)
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
        question_html="",
    )
    input_state: State = {
        "question": question,
        "isAdaptive": True,
        "server_js": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }
    result = app.invoke(input_state, config=config)  # type: ignore
    print(result["server_js"])

    # Save output
    output_path = Path(
        r"langgraph_server/gestalt_graphs/code_generator/outputs/server_js"
    )
    save_graph_visualization(app, output_path, filename="graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
