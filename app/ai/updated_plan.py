
import os
import json
import urllib.request
import urllib.error


def update_workout_plan(
    original_plan,
    feedback,
    username,
    age,
    weight,
    goal,
    intensity
):
    """
    Update the original workout plan based on user feedback.
    """

    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv(
        "WORKOUT_MODEL",
        "gemini-2.5-pro"
    )

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is missing in the .env file."
        )

    prompt = f"""
Update a user's 7-day workout plan based on feedback.

User details:
Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Intensity: {intensity}

Original workout plan:
{original_plan}

User feedback:
{feedback}

Requirements:
1. Create an improved 7-day workout plan.
2. Consider the user's feedback.
3. Use simple English.
4. Include warm-up and cool-down.
5. Include exercises, sets, repetitions, and rest time.
6. Add a safety note.
7. Do not provide medical diagnosis.
8. Clearly format the updated plan.
"""

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    request_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=request_data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=60
        ) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

        candidates = response_data.get("candidates", [])

        if not candidates:
            raise ValueError(
                "Gemini did not return an updated plan."
            )

        parts = candidates[0].get("content", {}).get(
            "parts", []
        )

        if not parts:
            raise ValueError(
                "Gemini response does not contain text."
            )

        return "\n".join(
            part.get("text", "")
            for part in parts
        ).strip()

    except urllib.error.HTTPError as error:
        error_body = error.read().decode(
            "utf-8",
            errors="ignore"
        )

        raise RuntimeError(
            f"Gemini API error {error.code}: {error_body}"
        ) from error

    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Unable to connect to Gemini API: {error.reason}"
        ) from error