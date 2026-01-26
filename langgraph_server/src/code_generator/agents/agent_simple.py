# --- Standard Library ---
from typing import List, Optional

# --- LangChain / LangGraph ---
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from langchain_core.tools import tool

# --- Internal: Graph Apps & State ---
from langgraph_server.gestalt_graphs.code_generator.graphs.question_html_graph import (
    app as question_html_tool,
    State as QState,
)
from langgraph_server.gestalt_graphs.code_generator.graphs.server_js_graph import (
    app as server_js_tool,
    State as JSState,
)

# --- Internal: Models ---
from langgraph_server.gestalt_graphs.models  import Question
from langgraph_server.gestalt_graphs.code_generator.graphs.solution_html_graph import (
    app as solution_html_tool,
    State as SolutionState,
)

# --- Internal: Prompts ---
from langgraph_server.gestalt_graphs.code_generator.prompts.prompts import (
    GESTALT_AGENT,
)

# --- Internal: Tools ---
from langgraph_server.gestalt_graphs.ai_tools.ai_tools import (
    prepare_zip,
)
from langgraph_server.gestalt_graphs.code_generator.graphs.server_py_graph import (
    app as server_py_generator,
    State as PyState,
)


model = init_chat_model(
    model="gpt-4o",
    model_provider="openai",
)


@tool
def generate_question_html(question: str, isAdaptive: bool):
    """
    Generate a formatted `question.html` file using established HTML conventions,
    grounded in examples retrieved from the Question HTML vectorstore.

    This tool takes a **complete, finalized natural-language question** and a flag
    indicating whether the question is **Adaptive** or **non-adaptive**.

    It returns TWO things:
    1. A fully formatted `question.html` file that follows the platform’s
       structural, semantic, and stylistic conventions.
    2. The set of retrieved reference documents used to guide the formatting
       and structure (for grounding, inspection, or debugging).

    When presenting results to the end user, you MAY display **only** the generated
    `question.html` content. The retrieved documents are provided for internal
    reference and should not be surfaced unless explicitly requested.

    Use this tool when:
    - You are converting a finalized question stub into `question.html`.
    - You need grounded examples to ensure correct HTML structure and layout.
    - You want to follow existing input, panel, and markup conventions exactly.

    The retrieved examples MUST guide the formatting of the output, but MUST NOT
    be copied verbatim. The final HTML should be original, clean, and ready for
    direct use in the educational system.
    """
    q = Question(
        question_text=question,
        solution_guide=None,
        final_answer=None,
        question_html="",
    )
    input_state: QState = {
        "question": q,
        "isAdaptive": isAdaptive,
        "question_html": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }
    result = question_html_tool.invoke(input_state)
    html = {"question_html": result.get("question_html")}
    retrieved_context: List[Document] = result.get("retrieved_documents", [])
    return html, retrieved_context


@tool
def generate_server_js(
    question_html: str,
    solution_guide: Optional[str] = None,
):
    """
    Generate a fully structured `server.js` file that implements the backend
    logic for an **adaptive question**, grounded in retrieved reference examples.

    This tool takes a **complete `question.html` file** and an optional
    **solution guide**, and synthesizes the JavaScript code required to:
    - Generate dynamic parameters at runtime
    - Compute correct answers programmatically
    - Expose values and results to the frontend question interface

    It returns TWO things:
    1. A generated `server.js` file containing the backend computation and
       parameter-generation logic for the question.
    2. The set of retrieved reference documents used to guide the structure,
       patterns, and conventions of the generated JavaScript.

    The retrieved documents serve as **grounding context** and are intended for
    internal inspection, debugging, or traceability. They SHOULD NOT be exposed
    to end users unless explicitly requested.

    Use this tool when:
    - You are generating backend logic for an **adaptive** question.
    - The `question.html` file contains dynamic variables or placeholders.
    - You need to follow established server-side conventions for parameter
      generation, computation, and data exposure.

    The retrieved examples MUST inform the structure and patterns of the output,
    but MUST NOT be copied verbatim. The generated JavaScript should be original,
    readable, and ready for direct use within the platform’s execution environment.
    """
    question = Question(
        question_text="",
        solution_guide=solution_guide,
        final_answer=None,
        question_html=question_html,
    )
    input_state: JSState = {
        "question": question,
        "isAdaptive": True,
        "server_js": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }
    result = server_js_tool.invoke(input_state)
    server = {"server_js": result.get("server_js")}
    retrieved_context: List[Document] = result.get("retrieved_documents", [])
    return server, retrieved_context


@tool
def generate_server_py(
    question_html: str,
    solution_guide: Optional[str] = None,
):
    """
    Generate a fully structured `server.py` file that implements the backend
    logic for an adaptive question, grounded in retrieved reference examples.

    This tool takes a complete `question.html` file and an optional
    solution guide, and synthesizes the Python code required to:
    - Generate dynamic parameters at runtime
    - Compute correct answers programmatically
    - Expose values and results to the frontend question interface

    The `isAdaptive` flag determines whether runtime parameter generation
    and computation logic should be included:
    - If `isAdaptive=True`, the generated Python code MUST include logic
      for dynamic parameter generation and answer computation.
    - If `isAdaptive=False`, the Python backend should be minimal or omitted,
      depending on platform conventions.

    It returns TWO things:
    1. A generated `server.py` file containing the backend computation and
       parameter-generation logic for the question.
    2. The set of retrieved reference documents used to guide the structure,
       patterns, and conventions of the generated Python code.

    The retrieved documents serve as grounding context and are intended for
    internal inspection, debugging, or traceability. They SHOULD NOT be exposed
    to end users unless explicitly requested.

    Use this tool when:
    - You are generating backend logic for an adaptive question using Python.
    - A finalized and educator-approved `question.html` already exists.
    - The question requires runtime parameter generation or computation.
    - The backend logic must follow established Python-side conventions.

    The retrieved examples MUST inform the structure and patterns of the output,
    but MUST NOT be copied verbatim. The generated Python code should be
    original, readable, and ready for direct use within the platform’s
    execution environment.
    """
    question = Question(
        question_text="",
        solution_guide=solution_guide,
        final_answer=None,
        question_html=question_html,
    )
    input_state: PyState = {
        "question": question,
        "isAdaptive": True,
        "server_py": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }
    result = server_py_generator.invoke(input_state)
    server = {"server_py": result.get("server_py")}
    retrieved_context: List[Document] = result.get("retrieved_documents", [])
    return server, retrieved_context


@tool
def generate_solution_html(
    question_html: str, solution_guide: Optional[str] = None, isAdaptive: bool = False
):
    """
    Generate a fully structured `solution.html` file that presents the
    step-by-step solution and final answer for a question, grounded in
    retrieved reference examples.

    This tool takes a **complete `question.html` file** as its primary
    reference and an optional **solution guide**, and synthesizes a
    platform-compliant `solution.html` that:
    - Explains the reasoning and steps required to solve the question
    - References variables, symbols, and structure defined in `question.html`
    - Presents results clearly for both adaptive and non-adaptive questions

    The `isAdaptive` flag indicates whether the question’s values are
    dynamically generated at runtime:
    - If `isAdaptive=True`, the solution is written generically and symbolically
      to remain valid across parameter variations.
    - If `isAdaptive=False`, the solution may include concrete values and
      fixed computations.

    It returns TWO things:
    1. A generated `solution.html` file containing the structured explanation,
       derivation, and final answer presentation.
    2. The set of retrieved reference documents used to guide formatting,
       structure, and instructional patterns.

    The retrieved documents serve as **grounding context** and are intended for
    internal inspection, debugging, or traceability. They SHOULD NOT be exposed
    to end users unless explicitly requested.

    Use this tool when:
    - A finalized `question.html` already exists.
    - You need a clear, pedagogically sound solution presentation.
    - The solution must align structurally and semantically with the question.
    - The question may be adaptive or non-adaptive, controlled via `isAdaptive`.

    The retrieved examples MUST inform the structure and instructional style
    of the output, but MUST NOT be copied verbatim. The generated solution HTML
    should be original, readable, and ready for direct use within the
    platform’s rendering environment.
    """
    question = Question(
        question_text="",
        solution_guide=solution_guide,
        final_answer=None,
        question_html=question_html,
    )
    input_state: SolutionState = {
        "question": question,
        "isAdaptive": isAdaptive,
        "solution_html": None,
        "retrieved_documents": [],
        "formatted_examples": "",
    }
    result = solution_html_tool.invoke(input_state)
    server = {"solution_html": result.get("solution_html")}
    retrieved_context: List[Document] = result.get("retrieved_documents", [])
    return server, retrieved_context


tools = [
    generate_question_html,
    prepare_zip,
    generate_server_js,
    generate_solution_html,
    generate_server_py,
]

agent = create_agent(
    model,
    tools=tools,
    system_prompt=GESTALT_AGENT,
)
