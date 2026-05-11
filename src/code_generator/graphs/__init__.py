from src.core.settings import get_settings
from langchain.chat_models import init_chat_model
from src.prompts.load_prompts import resolve_prompt

settings = get_settings()
model = init_chat_model(
    model=settings.model,
    model_provider="google_genai",
)
