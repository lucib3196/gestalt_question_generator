
from datetime import date, datetime, time
from pathlib import Path
from typing import Any
from uuid import UUID
from pydantic import BaseModel
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import CompiledStateGraph


def write_image_data(image_bytes: bytes, folder_path: str | Path, filename: str) -> str:
    try:
        path = Path(folder_path).resolve()
        path.mkdir(exist_ok=True)
        save_path = path / filename

        if save_path.suffix != ".png":
            raise ValueError(
                "Suffix allowed is only PNG either missing or nnot allowed"
            )
        save_path.write_bytes(image_bytes)
        return save_path.as_posix()
    except Exception as e:
        raise ValueError(f"Could not save image {str(e)}")


def save_graph_visualization(
    graph: CompiledStateGraph | Any,
    folder_path: str | Path,
    filename: str,
):
    try:
        image_bytes = graph.get_graph().draw_mermaid_png()
        save_path = write_image_data(image_bytes, folder_path, filename)

        print(f"✅ Saved graph visualization at: {save_path}")
    except ValueError:
        raise
    except Exception as error:
        print(f"❌ Graph visualization failed: {error}")


def to_serializable(obj: Any) -> Any:
    """
    Recursively convert Pydantic models (and nested dicts/lists thereof)
    into plain Python data structures.
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]

    # --- Special cases ---
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Path):
        return obj.as_posix()

    return obj



def extract_langsmith_prompt(base) -> str:
    try:
        if not isinstance(base, ChatPromptTemplate):
            raise ValueError("expected a ChatPromptTemplate")

        if not base.messages:
            raise ValueError("ChatPromptTemplate.messages is empty")

        messages = base.messages[0]
        if hasattr(messages, "prompt") and getattr(messages, "prompt") is not None and hasattr(messages.prompt, "template"):  # type: ignore
            template = messages.prompt.template  # type: ignore
        elif isinstance(messages, SystemMessage):
            template = messages.content
            if isinstance(template, list):
                template = template[0]
        else:
            raise ValueError(f"Unsupported message type: {type(messages).__name__}")

        return template  # type: ignore

    except Exception as e:
        raise ValueError(f"Could not extract prompt {str(e)}")
