from langchain.tools import tool
from typing import Dict, Optional
import base64
import io
import zipfile


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
        "filename": zip_name,  # type: ignore
        "mime_type": "application/zip",
        "zip_base64": encoded,
    }
