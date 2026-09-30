import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv(override=True)


def create_local_workout(username, age, weight, goal, intensity):
    return f"""
7-DAY WORKOUT PLAN

User: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Fitness Level: {intensity}

Day 1:
- Exercise: Bodyweight Squats
- Sets: 3
- Repetitions: 12
- Rest: 60 seconds

Day 2:
- Exercise: Push-ups
- Sets: 3
- Repetitions: 10
- Rest: 60 seconds

Day 3:
- Exercise: Walking
- Duration: 30 minutes
- Rest: Recovery day

Day 4:
- Exercise: Lunges
- Sets: 3
- Repetitions: 10 each leg
- Rest: 60 seconds

Day 5:
- Exercise: Plank
- Sets: 3
- Duration: 30 seconds
- Rest: 60 seconds

Day 6:
- Exercise: Light Jogging
- Duration: 20 minutes
- Rest: Recovery as needed

Day 7:
- Exercise: Full Body Stretching
- Duration: 20 minutes
- Rest: Recovery day

NOTE:
This local plan is being used because the Gemini API is currently unavailable.
"""


def generate_workout_gemini(username, age, weight, goal, intensity):

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("WORKOUT_MODEL", "gemini-3.8-flash")

    if not api_key:
        print("Gemini API key not found.")
        print("Using local workout plan.")
        return create_local_workout(
            username, age, weight, goal, intensity
        )

    prompt = f"""
Create a simple and safe 7-day workout plan.

User details:
Name: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Fitness Level: {intensity}

Requirements:
1. Create exactly 7 days.
2. Clearly label Day 1 to Day 7.
3. Give exercises for each day.
4. Include sets and repetitions where appropriate.
5. Include rest or recovery days.
6. Keep the plan suitable for the fitness level.
7. Keep the explanation simple.
8. Do not include dangerous exercises.
9. Do not provide medical advice.

Use this format:

Day 1:
- Exercise:
- Sets:
- Repetitions:
- Rest:

Day 2:
- Exercise:
- Sets:
- Repetitions:
- Rest:

Day 3:
- Exercise:
- Sets:
- Repetitions:
- Rest:

Day 4:
- Exercise:
- Sets:
- Repetitions:
- Rest:

Day 5:
- Exercise:
- Sets:
- Repetitions:
- Rest:

Day 6:
- Exercise:
- Sets:
- Repetitions:
- Rest:

Day 7:
- Exercise:
- Sets:
- Repetitions:
- Rest:
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/{model}:generateContent"
        f"?key={api_key}"
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
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 3000
        }
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:

        print(f"Trying Gemini model: {model}")

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            response_data = response.read().decode("utf-8")

        result = json.loads(response_data)

        candidates = result.get("candidates", [])

        if not candidates:
            raise RuntimeError(
                "Gemini returned no candidates."
            )

        content = candidates[0].get(
            "content",
            {}
        )

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
                "Gemini returned an empty response."
            )

        print("Gemini workout generated successfully.")

        return "\n".join(text_parts)

    except urllib.error.HTTPError as e:

        print(
            f"Gemini HTTP error: {e.code}"
        )

        print(
            "Gemini is unavailable. "
            "Using local workout plan."
        )

        return create_local_workout(
            username,
            age,
            weight,
            goal,
            intensity
        )

    except urllib.error.URLError as e:

        print(
            f"Gemini network error: {e.reason}"
        )

        print(
            "Using local workout plan."
        )

        return create_local_workout(
            username,
            age,
            weight,
            goal,
            intensity
        )

    except Exception as e:

        print(
            f"Gemini error: {e}"
        )

        print(
            "Using local workout plan."
        )

        return create_local_workout(
            username,
            age,
            weight,
            goal,
            intensity
        )