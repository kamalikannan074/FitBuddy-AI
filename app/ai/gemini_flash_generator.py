import os
import json
import time
import random
import urllib.request
import urllib.error

from dotenv import load_dotenv

# Load values from .env
load_dotenv()


def generate_nutrition_tip_with_flash(goal):
    """
    Generate a simple nutrition tip using Gemini.
    """

    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")

    # Get nutrition model
    model = os.getenv(
        "NUTRITION_MODEL",
        "gemini-3.8-flash"
    )

    # Check API key
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing in the .env file."
        )

    # Prompt
    prompt = f"""
Give a simple and useful nutrition tip for a person
whose fitness goal is: {goal}

Requirements:
- Give practical food advice.
- Mention protein-rich foods.
- Mention healthy carbohydrates.
- Mention healthy fats.
- Mention water intake.
- Keep the answer simple.
- Keep the answer short.
- Do not provide medical advice.

Format the answer with a short heading and
3 to 5 simple bullet points.
"""

    # Gemini API URL
    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )

    # Request data
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }

    # Convert to JSON
    data = json.dumps(payload).encode("utf-8")

    # Create request
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    # Retry temporary errors
    max_retries = 2

    for attempt in range(max_retries):

        try:

            print(
                f"Sending nutrition request to Gemini "
                f"using model: {model}"
            )

            with urllib.request.urlopen(
                request,
                timeout=10
            ) as response:

                response_data = response.read().decode(
                    "utf-8"
                )

            # Parse JSON
            result = json.loads(response_data)

            # Get candidates
            candidates = result.get(
                "candidates",
                []
            )

            if not candidates:
                raise RuntimeError(
                    "Gemini returned no nutrition response."
                )

            # Get content
            content = candidates[0].get(
                "content",
                {}
            )

            # Get parts
            parts = content.get(
                "parts",
                []
            )

            text_parts = []

            for part in parts:

                if "text" in part:
                    text_parts.append(
                        part["text"]
                    )

            if not text_parts:
                raise RuntimeError(
                    "Gemini returned an empty nutrition response."
                )

            return "\n".join(text_parts)

        except urllib.error.HTTPError as e:

            error_body = e.read().decode(
                "utf-8",
                errors="replace"
            )

            # Retry temporary errors
            if e.code in (
                429,
                500,
                502,
                503,
                504
            ):

                if attempt < max_retries - 1:

                    delay = (
                        (2 ** attempt)
                        + random.uniform(0, 1)
                    )

                    print(
                        f"Gemini returned HTTP {e.code}."
                    )

                    print(
                        f"Retrying in "
                        f"{delay:.1f} seconds..."
                    )

                    time.sleep(delay)

                    continue

                raise RuntimeError(
                    f"Gemini API HTTP Error "
                    f"{e.code}: {error_body}"
                )

            # Permanent error
            raise RuntimeError(
                f"Gemini API HTTP Error "
                f"{e.code}: {error_body}"
            )

        except urllib.error.URLError as e:

            if attempt < max_retries - 1:

                delay = (
                    (2 ** attempt)
                    + random.uniform(0, 1)
                )

                print(
                    f"Network error: {e.reason}"
                )

                print(
                    f"Retrying in "
                    f"{delay:.1f} seconds..."
                )

                time.sleep(delay)

                continue

            raise RuntimeError(
                f"Gemini network error: "
                f"{e.reason}"
            )

        except json.JSONDecodeError:

            raise RuntimeError(
                "Gemini returned invalid JSON."
            )

    raise RuntimeError(
        "Gemini request failed after multiple attempts."
    )