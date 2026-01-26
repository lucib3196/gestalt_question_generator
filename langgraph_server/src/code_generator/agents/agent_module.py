from langchain.agents import create_agent
from langchain_core.tools import tool

from langgraph_server.gestalt_graphs.models  import Question
from langgraph_server.gestalt_graphs.code_generator.prompts.prompts import (
    GESTALT_EDUCATOR_AGENT_PROMPT,
)
from langgraph_server.gestalt_graphs.ai_tools.ai_tools import (
    prepare_zip,
)
from langgraph_server.gestalt_graphs.code_generator.graphs.gestalt_generator import (
    app as gestalt_generator,
    State as GestaltState,
)


@tool
def generate_gestalt_module(
    question_text: str,
    solution_guide: str | None,
    final_answer: str | None,
    isAdaptive: bool = True,
) -> dict:
    """
    Generate a complete Gestalt module package.

    This tool should be invoked whenever a user wants to create a **full Gestalt module**.
    A Gestalt module is a fully self-contained set of educational assets representing a
    polished, textbook-style STEM problem that is ready for immediate deployment.

    ------------------------------
    Required Inputs
    ------------------------------

    question_text : str
        A fully formatted, high-quality problem statement—written exactly as it would
        appear in a textbook, exam, or structured engineering module.
        This must include:
        - Descriptive problem narration
        - Clean mathematical formatting (inline and block LaTeX using `$` and `$$`)
        - All variables, symbols, and units required for evaluation
        - No missing assumptions or contextual gaps

    solution_guide : str | None
        If the problem is computational, this is the complete step-by-step solution guide
        showing reasoning, formulas, substitutions, and intermediate results.
        This content is used to generate `solution.html`.
        If the problem is purely conceptual or qualitative, this may be `None`.

    final_answer : str | None
        The final numeric or conceptual answer to the question.
        This value is used for grading and validation logic and MUST be provided for
        questions that require correctness evaluation.
        For conceptual questions, this may be a concise written response.

    isAdaptive : bool, default=True
        Controls whether the generated module is **adaptive** or **static**.
        
        The question being adaptive tends to be the right choice in most cases
        unless you are working with a purely conceptual question which does not require any
        computation. 

        - If `isAdaptive=True`:
          • The module supports runtime parameter generation.
          • `server.py` and `server.js` are generated with logic to dynamically
            produce variables and compute correct answers.
          • The solution and backend logic are written symbolically so the question
            remains valid across parameter variations.

        - If `isAdaptive=False`:
          • The module is treated as static with fixed values.
          • Backend logic is simplified or omitted according to platform conventions.
          • The solution may include concrete numeric values and explicit computations.

    ------------------------------
    What This Tool Generates
    ------------------------------

    Calling this tool automatically constructs a full Gestalt module package, including:

    - `question.html`
      Generated from `question_text`, structured using Gestalt/PL components.

    - `solution.html`
      Derived from `solution_guide`, formatted for clarity, pedagogy, and vectorstore alignment.

    - `server.py` (if computational and adaptive)
      Python backend implementing deterministic parameter generation and answer evaluation.

    - `server.js` (if computational and adaptive)
      JavaScript runtime that mirrors the Python backend behavior.

    - Metadata required by the Gestalt rendering, grading, and execution system.

    ------------------------------
    Developer Note
    ------------------------------
    This tool returns a JSON structure only.
    The calling agent is responsible for assembling and managing all generated
    module files based on the returned output.
    """
    question = Question(
        question_text=question_text,
        solution_guide=solution_guide,
        final_answer=final_answer,
        question_html="",
    )
    input_state: GestaltState = {
        "question": question,
        "metadata": None,
        "isAdaptive": isAdaptive,
        "files": {},
    }

    result = gestalt_generator.invoke(input_state)  # type: ignore
    files: dict = result["files"]
    return files


agent = create_agent(
    model="gpt-4o",
    # checkpointer=InMemorySaver(),
    tools=[generate_gestalt_module, prepare_zip],
    system_prompt=GESTALT_EDUCATOR_AGENT_PROMPT,
)
