import json
import operator
from pathlib import Path
from typing import Annotated, List, Literal, TypedDict

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from src.code_generator.graphs import model, resolve_prompt, vector_store

from src.models import CodeResponse, Question
from src.code_generator.graphs import (
    model,
    resolve_prompt,
    vector_store,
    save_graph_visualization,
    to_serializable,
    CodeValidationState,
    code_validation_graph,
)


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
    prompt = resolve_prompt("server_js_graph_prompt")
    prompt += (
        f"""question html {question_html} examples: {examples} solution: {solution}"""
    )

    structured_model = model.with_structured_output(CodeResponse)
    server = structured_model.invoke(prompt)
    server = CodeResponse.model_validate(server)
    return {"server_js": server.code}


workflow = StateGraph(State)
# Define Nodes
workflow.add_node("retrieve_examples", retrieve_examples)
workflow.add_node("generate_code", generate_code)

# Connect
# Connect
workflow.add_edge(START, "retrieve_examples")
workflow.add_edge("generate_code", END)


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
    output_path = Path(r"src/code_generator/outputs/server_js")
    save_graph_visualization(app, output_path, filename="graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
