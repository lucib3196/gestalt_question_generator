from langchain.chat_models import init_chat_model
from pathlib import Path
import json
from src.utils import to_serializable
from langchain.messages import AIMessage
import base64
from pathlib import Path
from uuid import uuid4

image_generation_model = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
)

response = image_generation_model.invoke("Generate an image of a cat")

response = json.loads(Path("./image_data.json").read_text())


def parse_image(response: AIMessage | dict):
    if isinstance(response, dict):
        response = AIMessage(**response)
    for c in response.content:
        ctype = None
        if isinstance(c, dict):
            ctype = c.get("type", None)
            if ctype == "image_url":
                image_url = c.get("image_url", {}).get("url", None)
                if image_url:
                    return image_url


image_url = parse_image(response)


def save_base64_image(
    base64_string: str,
    output_dir: str | Path,
    filename: str | None = None,
) -> Path:
    """
    Saves a base64 image to disk.

    Supports:
    - raw base64 strings
    - data URLs like:
      data:image/png;base64,...

    Returns:
        Path to saved image.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Handle data URL format
    if "," in base64_string:
        header, encoded = base64_string.split(",", 1)

        # Attempt extension extraction
        if "image/" in header:
            ext = header.split("image/")[1].split(";")[0]
        else:
            ext = "png"

    else:
        encoded = base64_string
        ext = "png"

    if filename is None:
        filename = f"{uuid4()}.{ext}"

    output_path = output_dir / filename

    image_bytes = base64.b64decode(encoded)

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return output_path

save_base64_image(image_url, "./", filename="image.png")