from pydantic import BaseModel
from typing import Dict, Literal, List

ALLOWED_MODE = Literal["text", "file"]

CHAT_NAMES = Literal["gestalt_generate_module", "gestalt_build_module"]


class ChatOption(BaseModel):
    label: str
    url: str
    description: str
    mode: ALLOWED_MODE = "text"
    active: bool = False


CHAT_OPTIONS: Dict[CHAT_NAMES, ChatOption] = {
    "gestalt_generate_module": ChatOption(
        label="Module Generator",
        url="agent_gestalt_module",
        description=(
            "Generate a complete, ready-to-use Gestalt module in a single pass. "
            "This mode creates and packages all required files "
            "(question.html, solution.html, server logic, and metadata) "
            "from finalized input with minimal iteration."
        ),
        active=True,
    ),
    "gestalt_build_module": ChatOption(
        label="Module Builder",
        url="agent_gestalt",
        description=(
            "Build and refine Gestalt modules incrementally using a "
            "file-by-file, tool-driven workflow. Ideal for "
            "fine-grained control, iteration, and targeted generation "
            "of question, solution, server logic, and metadata files."
        ),
        active=True,
    ),
}
