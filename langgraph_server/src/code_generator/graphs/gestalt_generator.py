from typing import Annotated, TypedDict, Literal
from pathlib import Path
import json

from typing import Sequence

# --- LangChain / LangGraph ---
from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from langgraph_server.gestalt_graphs.code_generator.graphs.question_html_graph import (
    app as question_html_generator,
    State as QState,
)
from langgraph_server.gestalt_graphs.code_generator.graphs.server_js_graph import (
    app as server_py_generator,
    State as JSState,
    app as server_js_generator,
)

from langgraph_server.gestalt_graphs.code_generator.graphs.solution_html_graph import (
    app as solution_html_generator,
    State as SolutionState,
)
from langgraph_server.gestalt_graphs.code_generator.graphs.question_metadata_graph import (
    app as question_metadata_generator,
)
from langgraph_server.gestalt_graphs.code_generator.graphs.server_py_graph import (
    app as server_py_generator,
    State as PyState,
)
from langgraph_server.gestalt_graphs.models import Question
from langgraph_server.gestalt_graphs.code_generator.graphs.question_metadata_graph import (
    QuestionMetaData,
)
from langgraph_server.gestalt_graphs.utils.utils import (
    save_graph_visualization,
    to_serializable,
)


memory = MemorySaver()
config = {"configurable": {"thread_id": "customer_123"}}


class State(TypedDict):
    question: Question
    metadata: QuestionMetaData | None
    isAdaptive: bool
    # Append any files
    files: Annotated[dict, lambda a, b: {**a, **b}]


def classify_question(state: State):
    input_state = {"question": state["question"], "metadata": None}
    result = question_metadata_generator.invoke(input_state, config)  # type: ignore

    return {"metadata": result["metadata"]}


def generate_question_html(state: State):
    metadata = state["metadata"]
    assert metadata

    input_state: QState = {
        "question": state["question"],
        "isAdaptive": state["isAdaptive"],
        "question_html": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }

    result = question_html_generator.invoke(input_state, config)  # type: ignore

    updated_question = state["question"].model_copy(
        update={"question_html": result["question_html"]}
    )

    return {
        "question": updated_question,
        "files": {"question.html": result["question_html"]},
    }


def generate_solution_html(state: State):
    metadata = state["metadata"]
    assert metadata

    input_state: SolutionState = {
        "question": state["question"],
        "isAdaptive": state["isAdaptive"],
        "solution_html": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }

    result = solution_html_generator.invoke(input_state, config)  # type: ignore

    return {"files": {"solution.html": result["solution_html"]}}


def generate_server_js(state: State):
    metadata = state["metadata"]
    assert metadata

    input_state: JSState = {
        "question": state["question"],
        "isAdaptive": state["isAdaptive"],
        "server_js": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }

    result = server_js_generator.invoke(input_state, config)  # type: ignore

    return {"files": {"server.js": result["server_js"]}}


def generate_server_py(state: State):
    metadata = state["metadata"]
    assert metadata

    input_state: PyState = {
        "question": state["question"],
        "isAdaptive": state["isAdaptive"],
        "server_py": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }

    result = server_py_generator.invoke(input_state, config)  # type: ignore

    return {"files": {"server.py": result["server_py"]}}


def generate_info_json(state: State):
    metadata = state["metadata"]
    assert metadata

    info_metadata = metadata.model_dump()
    info_metadata["ai_generated"] = True

    if state["isAdaptive"]:
        info_metadata["languages"] = ["javascript", "python"]
        info_metadata["isAdaptive"] = True
    else:
        info_metadata["languages"] = []
        info_metadata["isAdaptive"] = False

    return {"files": {"info.json": json.dumps(to_serializable(info_metadata))}}


def router(
    state: State,
) -> Sequence[
    Literal["generate_solution_html", "generate_server_js", "generate_server_py"]
]:
    metadata = state["metadata"]
    assert metadata
    if state["isAdaptive"]:
        return ["generate_server_py", "generate_server_js", "generate_solution_html"]
    else:
        return ["generate_solution_html"]


# Build the graph

graph = StateGraph(State)

graph.add_node("classify_question", classify_question)
graph.add_node("generate_question_html", generate_question_html)
graph.add_node("generate_solution_html", generate_solution_html)
graph.add_node("generate_server_js", generate_server_js)
graph.add_node("generate_server_py", generate_server_py)
graph.add_node("generate_info_json", generate_info_json)

graph.add_edge(START, "classify_question")
graph.add_edge("classify_question", "generate_question_html")

# Add the path mapping here
graph.add_conditional_edges(
    "generate_question_html",
    router,
    {
        "generate_solution_html": "generate_solution_html",
        "generate_server_js": "generate_server_js",
        "generate_server_py": "generate_server_py",
    },
)

graph.add_edge("generate_server_js", "generate_info_json")
graph.add_edge("generate_server_py", "generate_info_json")
graph.add_edge("generate_solution_html", "generate_info_json")

graph.add_edge("generate_info_json", END)


# memory = MemorySaver()
# app = workflow.compile(checkpointer=memory)
app = graph.compile()
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
        "metadata": None,
        "files": {},
    }
    result = app.invoke(input_state, config=config)  # type: ignore

    # Save output
    output_path = Path(
        r"langgraph_server/gestalt_graphs/code_generator/outputs/gestalt_module"
    )
    save_graph_visualization(app, output_path, filename="gestalt_generator_graph.png")
    data_path = output_path / "output.json"
    data_path.write_text(json.dumps(to_serializable(result)))
