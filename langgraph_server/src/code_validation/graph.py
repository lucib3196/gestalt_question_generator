from typing import TypedDict, Literal, List
from langgraph.graph import StateGraph, START, END
from langchain.chat_models import init_chat_model
from langgraph.types import Command
from typing import Annotated
from operator import add
from langgraph_server.gestalt_graphs.code_validation.models import (
    CodeResponse,
    ValidationResult,
)
from pathlib import Path
import json
from langgraph_server.src.utils import (
    save_graph_visualization,
    to_serializable,
)

model = init_chat_model(
    model="gpt-4o",
    model_provider="openai",
)


class State(TypedDict):
    prompt: str
    generated_code: str
    validation_errors: Annotated[List[str], add]
    # Amount of times going through generation
    refinement_count: int
    final_code: str | None


def generate_code(state: State) -> Command[Literal["validate_code"]]:
    """Generate code with structured output schema."""

    refinement_context = ""
    if state["refinement_count"] > 0:
        errors = "\n".join(state["validation_errors"])
        refinement_context = f"\nFix these issues:\n{errors}"

    prompt = f"{state['prompt']}{refinement_context} Code to be fixed: {state['generated_code']}"

    # Generate with structured output
    structured_model = model.with_structured_output(CodeResponse)
    response = structured_model.invoke(prompt)
    response = CodeResponse.model_validate(response)

    return Command(
        update={
            "generated_code": response.code,
            "refinement_count": state["refinement_count"] + 1,  # Increment here
        },
        goto="validate_code",
    )


def validate_code(state: State):
    """Validate generated code against criteria."""

    errors = []
    user_prompt = state["prompt"]
    generated_code = state["generated_code"]

    validation_prompt = f"""
    Review the following code to ensure it implements the user's requirement.
    
    Check for:
    1. Does it implement the requirement correctly?
    2. Is error handling present?
    
    User Prompt: {user_prompt}
    
    Generated Code: {generated_code}
    """

    evaluator_model = model.with_structured_output(ValidationResult)
    validation_result = evaluator_model.invoke(validation_prompt)
    validation_result = ValidationResult.model_validate(validation_result)

    if validation_result.errors:
        errors.extend(validation_result.errors)

    return Command(update={"validation_errors": errors})


def should_refine(state: State) -> Literal["accept", "generate_code"]:
    """Decide whether to refine or accept code."""

    # Max refinements to prevent loops
    if state["refinement_count"] >= 3:
        return "accept"

    # No errors = accept
    if not state["validation_errors"]:
        return "accept"

    # Has errors = generate code again
    return "generate_code"


def accept_code(state: State) -> Command:
    """Accept the code as final."""
    final_code = state["generated_code"]
    return Command(update={"final_code": final_code})


# Create graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("generate_code", generate_code)
workflow.add_node("validate_code", validate_code)
workflow.add_node("accept", accept_code)

# Add edges - START with generation, not validation
workflow.add_edge(START, "validate_code")

# Conditional edge from should_refine
workflow.add_conditional_edges(
    "validate_code",
    should_refine,
    {
        "accept": "accept",
        "generate_code": "generate_code",
    },
)
workflow.add_edge("generate_code", END)
workflow.add_edge("accept", END)

# Compile
graph = workflow.compile()


if __name__ == "__main__":
    folder_path = Path(
        r"src/ai_processing/code_generator/outputs/code_validation"
    ).resolve()

    save_graph_visualization(graph, folder_path, "code_validation.png")
    input_state: State = {
        "prompt": "Refactor this function to be more readable and ensure it handles division safely.",
        "generated_code": "def compute(a,b): return a/b",
        "validation_errors": [],
        "refinement_count": 0,
        "final_code": "",
    }

    result = graph.invoke(input_state)
    print(result)

    save_output = folder_path / "output.json"
    save_output.write_text(json.dumps(to_serializable(result)))
