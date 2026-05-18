
from pathlib import Path
from typing import Any
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
