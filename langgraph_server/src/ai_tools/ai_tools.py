from pathlib import Path
from langchain.tools import tool
from typing import Dict,Optional
from core.settings import get_settings
import base64
import io
import zipfile

output = get_settings().output_path
OUTPUT_DIR = Path(output).resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@tool
def save_file(filename: str, content: str) -> str:
    """
    Save text content to a file in the application's output directory.

    This tool is intended for use by an LLM to persist generated text
    (e.g., reports, code, summaries, or data files) to disk so the file
    can later be listed and downloaded by the user via the Streamlit UI.

    The file is written using UTF-8 encoding and will overwrite any
    existing file with the same name.

    Args:
        filename (str):
            Name of the file to create (including extension), relative
            to the application's output directory (e.g., "report.txt",
            "solution.md", "data.json").

        content (str):
            The text content to write into the file.

    Returns:
        str:
            The filesystem path to the saved file as a string.
    """
    path = OUTPUT_DIR / filename
    path.write_text(content)
    return str(path)


@tool
def prepare_zip(
    files: Dict[str, str],
    zip_name: Optional[str] = "gestalt_module.zip",
) -> Dict[str, str]:
    """
    Packages provided files into a ZIP archive and returns it as Base64.

    Args:
        files:
            A dictionary mapping filenames to file contents.
            Example:
                {
                    "question.html": "<html>...</html>",
                    "solution.html": "<html>...</html>"
                }

        zip_name:
            Optional name of the generated ZIP file.
            Defaults to "gestalt_module.zip".

    Returns:
        A dictionary containing:
        - filename: Name of the generated ZIP file
        - mime_type: MIME type of the file ("application/zip")
        - zip_base64: Base64-encoded ZIP file contents
    """

    memory_file = io.BytesIO()

    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)

    memory_file.seek(0)
    encoded = base64.b64encode(memory_file.read()).decode("utf-8")

    return {
        "filename": zip_name, # type: ignore
        "mime_type": "application/zip",
        "zip_base64": encoded,
    }


if __name__ == "__main__":
    print(OUTPUT_DIR)
    # save_file("content.html", "hellWorld")
