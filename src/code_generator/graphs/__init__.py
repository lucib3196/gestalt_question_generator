import src.code_validation
from src.core.settings import get_settings
from langchain.chat_models import init_chat_model
from src.prompts.load_prompts import resolve_prompt
from src.code_generator.vectorstore.vectorstore import vector_store
from src.utils import save_graph_visualization, to_serializable
from src.code_validation.graph import State as CodeValidationState, graph as code_validation_graph

settings = get_settings()
model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)
