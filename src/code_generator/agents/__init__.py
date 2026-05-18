from src.core.settings import get_settings
from langchain.chat_models import init_chat_model

from src.code_generator.graphs.question_html_graph import (
    app as question_html_tool,
    State as QState,
)
from src.code_generator.graphs.server_js_graph import (
    app as server_js_tool,
    State as JSState,
)
from src.code_generator.graphs.solution_html_graph import (
    app as solution_html_tool,
    State as SolutionState,
)
from src.code_generator.graphs.server_py_graph import (
    app as server_py_generator,
    State as PyState,
)

from src.code_generator.generator.gestalt_generator import (
    app as gestalt_generator,
    State as GestaltState,
)

settings = get_settings()

model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)
image_generation_model = init_chat_model(
    model="gemini-3.1-flash-image-preview",
    model_provider="google_genai",
)
