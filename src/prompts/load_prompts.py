from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
from src.core.settings import get_settings
from src.core.logger import logger

"""Helpers for loading, saving, and extracting prompt templates."""

load_dotenv()
client = Client()
settings = get_settings()
VALID_PROMPTS = ["question_html_prompt"]

BASE_PATH = Path("./src/prompts")


def fetch_all_prompts():
    """Fetch all configured prompts from LangSmith and save them locally."""
    for p in VALID_PROMPTS:
        text = ""
        try:
            prompt = client.pull_prompt(p)
            text = extract_langsmith_prompt(prompt)
        except Exception as e:
            logger.warning(f"Failed to get prompt {p} Error: {e}\n Double check name")
            continue
        name = f"{p}.md"
        save_path = BASE_PATH / name
        save_path.write_text(text, encoding="utf-8")


def load_local_prompt(prompt_name: str) -> str:
    """Load a prompt file from the local prompts directory."""
    path = Path("src/prompts") / prompt_name
    if not path.exists():
        raise ValueError(f"Prompt path {path} does not exist")
    content = path.read_text(encoding="utf-8")
    if content is None:
        logger.warning(
            "Warning Prompt is empty. Unexpected behavior with agent will occur"
        )
    return content


def extract_langsmith_prompt(base: Any) -> str:
    """Extract the system prompt text from a LangSmith chat prompt template."""
    try:
        if not isinstance(base, ChatPromptTemplate):
            raise ValueError("expected a ChatPromptTemplate")
        if not base.messages:
            raise ValueError("ChatPromptTemplate.messages is empty")

        messages = base.messages[0]
        if (
            hasattr(messages, "prompt")
            and getattr(messages, "prompt") is not None
            and hasattr(messages.prompt, "template")  # type: ignore
        ):  # type: ignore
            template = messages.prompt.template  # type: ignore
        elif isinstance(messages, SystemMessage):
            template = messages.content
            if isinstance(template, list):
                template = template[0]
        else:
            raise ValueError(f"Unsupported message type: {type(messages).__name__}")

        return str(template)

    except Exception as e:
        raise ValueError(f"Could not extract prompt {str(e)}")


def resolve_prompt(prompt_identifier: str) -> str:
    try:
        if settings.prompt_source == "local":
            prompt = load_local_prompt(f"src/prompts/{prompt_identifier}.md")
        else:
            prompt = extract_langsmith_prompt(client.pull_prompt(prompt_identifier))
        return prompt
    except Exception as e:
        raise ValueError(f"Could not resolve prompt {e}")


if __name__ == "__main__":
    fetch_all_prompts()
