# --- Standard Library ---
from typing import List, Optional
from src.models import Question
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.documents import Document
from langchain_core.tools import tool
from src.code_generator.agents import (
    question_html_tool,
    QState,
    server_js_tool,
    JSState,
    solution_html_tool,
    SolutionState,
    server_py_generator,
    PyState,
    model,
)
from pydantic import BaseModel, Field
from src.code_generator.graphs.question_metadata_graph import (
    QuestionMetaData,
    State as MetaInput,
    app as generate_metadata,
)
from pathlib import Path

import re
import html
from typing import Optional


def safe_string_cleanup(
    text: Optional[str],
    *,
    remove_markdown_fences: bool = True,
    normalize_newlines: bool = True,
    unescape_html_entities: bool = True,
    collapse_excess_newlines: bool = True,
    strip_trailing_whitespace: bool = True,
    strip_surrounding_whitespace: bool = True,
) -> str:
    """
    General-purpose safe cleanup utility for LLM-generated strings.

    Designed to safely normalize common formatting artifacts WITHOUT
    aggressively modifying meaningful content such as:
    - LaTeX
    - template braces
    - escaped math expressions
    - custom HTML tags

    Safe operations include:
    - newline normalization
    - markdown fence removal
    - whitespace cleanup
    - HTML entity unescaping
    - excess blank line collapsing

    Parameters
    ----------
    text : Optional[str]
        Input text to normalize.

    remove_markdown_fences : bool
        Removes surrounding markdown code fences such as ```html.

    normalize_newlines : bool
        Normalizes \\r\\n and escaped \\n values.

    unescape_html_entities : bool
        Converts entities like &lt; into <.

    collapse_excess_newlines : bool
        Reduces excessive blank lines.

    strip_trailing_whitespace : bool
        Removes trailing spaces from each line.

    strip_surrounding_whitespace : bool
        Strips leading/trailing whitespace from entire document.

    Returns
    -------
    str
        Cleaned string.
    """

    if text is None:
        return ""

    # Ensure string
    text = str(text)

    # HTML entity cleanup
    if unescape_html_entities:
        text = html.unescape(text)

    # Normalize line endings
    if normalize_newlines:

        # Windows -> Unix
        text = text.replace("\r\n", "\n")

        # Old Mac -> Unix
        text = text.replace("\r", "\n")

        # Escaped newlines -> actual newlines
        text = text.replace("\\n", "\n")

        # Escaped tabs
        text = text.replace("\\t", "\t")

    # Remove markdown fences
    if remove_markdown_fences:

        text = re.sub(
            r"^\s*```[a-zA-Z0-9_-]*\s*\n",
            "",
            text,
        )

        text = re.sub(
            r"\n\s*```\s*$",
            "",
            text,
        )

    # Collapse excessive blank lines
    if collapse_excess_newlines:
        text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove trailing whitespace per line
    if strip_trailing_whitespace:
        text = "\n".join(line.rstrip() for line in text.splitlines())

    # Final strip
    if strip_surrounding_whitespace:
        text = text.strip()

    return text


def cleanup_file_content(filename: str, content: str) -> str:

    suffix = Path(filename).suffix

    if suffix == ".html":
        return safe_string_cleanup(
            content,
            unescape_html_entities=False,
        )

    elif suffix in [".js", ".ts"]:
        return safe_string_cleanup(
            content,
            normalize_newlines=False,
        )

    elif suffix == ".py":
        return safe_string_cleanup(content)

    return content


class File(BaseModel):
    filename: str = Field(..., description="The file name")
    content: str = Field(..., description="The actual text content of the file.")
    extension: str = Field(..., description="The file extension (e.g., '.js', '.py').")


class FinalQuestionPayload(BaseModel):
    """Final payload containing metadata and generated files for persistence."""

    metadata: QuestionMetaData = Field(
        ...,
        description="Canonical question metadata produced by generate_question_metadata.",
    )
    files: List[File] = []


class ImageResponse(BaseModel):
    url: str


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
def generate_question_metadata(
    question_text: str,
    question_html: Optional[str],
    isAdaptive: bool,
):
    """
    Build canonical question metadata used by the final packaging step.

    Call this after question generation and before building the final payload so
    metadata is normalized to platform schema expectations. If `question_html`
    is missing, it is treated as an empty string.
    """
    if not question_html:
        question_html = ""
    question = Question(
        question_text=question_text,
        solution_guide=None,
        question_html=question_html,
        final_answer=None,
    )
    result = generate_metadata.invoke(
        MetaInput(question=question, isAdaptive=isAdaptive)
    )
    return result.get("metadata", None)


@tool
def generate_solution_html(
    question_html: str,
    solution_guide: Optional[str] = None,
    isAdaptive: bool = False,
    server_file: str | None = None,
):
    """
    Generate a fully structured `solution.html` file that presents the
    step-by-step solution and final answer for a question.

    This tool takes a **complete `question.html` file** as its primary
    reference and an optional **solution guide**, and produces a
    platform-compliant `solution.html` that:
    - Explains the reasoning and steps required to solve the question
    - Uses variables, symbols, and structure defined in `question.html`
    - Produces a solution suitable for adaptive or non-adaptive execution

    Optional Server File:
    - A `server_file` may be provided when the question uses server-side logic
      to generate parameters, values, or intermediate results.
    - The server file is treated as the **source of truth** for generated
      values and naming conventions.
    - When provided, the solution HTML must reference and remain consistent
      with the outputs, variables, and semantics defined by the server file.
    - The solution HTML MUST NOT reimplement or duplicate server-side logic.

    Adaptive Behavior:
    - If `isAdaptive=True`, the solution is written symbolically and generically
      so it remains valid across different parameter realizations.
    - If `isAdaptive=False`, the solution may include concrete values and
      explicit computations.

    This tool returns TWO outputs:
    1. A generated `solution.html` file containing the structured explanation,
       derivation, and final answer presentation.
    2. The retrieved reference documents used to guide formatting and
       instructional style.

    Use this tool when:
    - A finalized `question.html` already exists.
    - You need a clear, pedagogically sound solution presentation.
    - The solution must align structurally and semantically with the question.
    - The question may optionally depend on a server file for value generation.

    The retrieved reference documents provide **grounding context** and must
    inform structure and instructional style, but MUST NOT be copied verbatim.
    The generated solution HTML should be original, readable, and ready for
    direct use within the platform’s rendering environment.
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
        "server_file": server_file,
    }
    result = solution_html_tool.invoke(input_state)
    server = {"solution_html": result.get("solution_html")}
    retrieved_context: List[Document] = result.get("retrieved_documents", [])
    return server, retrieved_context


@tool
def final_question_payload(metadata: QuestionMetaData, files: List[File]):
    """
    Create the final question payload for storage.

    Use this as the LAST tool call when the educator is ready to finalize.
    Requirements:
    - Metadata must be generated via `generate_question_metadata`.
    - At least one generated file must be included.
    - File names must use proper extensions that match file contents
      (for example, use `server.js`, not `server_js`).

      Since this is the final payload message do not show the files or metadata directly unless specirfically mentioned this is meant to keep the chat messages complete.
      On the frontend of our application we are allowing users to accepts and persist the question just mention that the initial generation is complete and now the user should be able to save the
      generated content on approval.

    """
    payload = FinalQuestionPayload(metadata=metadata, files=files)
    return payload.model_dump()


tools = [
    generate_question_html,
    generate_server_js,
    generate_solution_html,
    generate_server_py,
    generate_question_metadata,
    final_question_payload,
    # generate_image,
]
system_prompt = Path(r"src/prompts/gestalt_educator_agent_prompt.md").read_text()

system_prompt += """You can also generate images. Available Tools. """

for t in tools:
    system_prompt += str(t.__doc__)

agent = create_agent(
    model,
    tools=tools,
    system_prompt=system_prompt,
)
