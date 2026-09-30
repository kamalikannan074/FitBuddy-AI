# FitBuddy - AI Fitness & Nutrition Plan Generator

FitBuddy is an intelligent fitness and nutrition planner built with FastAPI, Jinja2, and Google Gemini AI. It creates personalized 7-day workout routines and targeted nutritional guidance based on individual physical metrics, fitness goals, and training experience levels.

---

## Features

- **Personalized 7-Day Workout Routine:** Generates structured, day-by-day workout splits tailored to age, weight, target fitness goal, and training intensity.
- **Tailored Nutrition Guidance:** Supplies goal-aligned dietary guidelines, macronutrient focus, and hydration targets.
- **Google Gemini AI Integration:** Employs Gemini models to synthesize safe, progressive workout and nutrition plans.
- **Reliable Local Fallback Engine:** Features built-in local plan generators that seamlessly activate if the Gemini API is temporarily unreachable or experiences high load (e.g. HTTP 503).
- **Interactive Feedback-Based Updates:** Allows users to submit adjustments (e.g., knee-friendly exercises, home dumbbells only, shorter sessions) and receive an AI-recalibrated routine.
- **Built-in SQLite Storage:** Automatically creates and persists user profiles and generated plans locally with zero manual database setup required.
- **Modern Responsive Web Interface:** Clean, mobile-friendly interface with day-card formatting, print-to-PDF support, clipboard copying, and double-submission protection.

---

## Project Structure

```
FitBuddy-AI/
├── app/
│   ├── main.py              # FastAPI application initialization and health check endpoint
│   ├── routes.py            # APIRouter defining form handlers, HTML page views, and JSON REST APIs
│   ├── database.py          # SQLite database connection, schema setup, and query functions
│   ├── models.py            # Data model definitions
│   ├── ai/
│   │   ├── gemini_generator.py         # 7-day workout generator using Gemini with local fallback
│   │   ├── gemini_flash_generator.py   # Nutrition advice generator using Gemini Flash with retry handling
│   │   └── updated_plan.py             # Plan recalibration based on user feedback
│   └── templates/
│       ├── index.html       # Home page: user profile onboarding and plan generation form
│       ├── result.html      # Plan dashboard: 7-day workout cards, nutrition tips, and feedback form
│       └── all_users.html   # User directory: overview of all saved profiles in SQLite
├── requirements.txt         # Python package dependencies
├── .env.example             # Sample environment configuration template
├── .gitignore               # Excludes virtual environments, databases, cache, and secrets
├── run.bat                  # Optional Windows launcher script
└── README.md                # Project documentation and setup guide
```

### Important Files Explained

- **`app/main.py`**: The application entry point. Creates the FastAPI instance, mounts Jinja2 templates, registers API routes, and serves the `/health` diagnostic endpoint.
- **`app/routes.py`**: The core controller. Manages all web routes (`/`, `/generate-workout`, `/submit-feedback`, `/view-all-users`, `/user/{user_id}`), input validation, fallback delegation, and REST API endpoints.
- **`app/database.py`**: SQLite database interface. Automatically creates `users` and `plans` tables on initialization and provides functions to save, update, query, and delete records.
- **`app/ai/gemini_generator.py`**: Connects to the Gemini API to generate the initial 7-day workout plan. Falls back to a local demo routine if unavailable.
- **`app/ai/gemini_flash_generator.py`**: Queries Gemini for targeted nutrition tips with fast timeouts and backoff handling.
- **`app/ai/updated_plan.py`**: Recalibrates existing plans using user feedback while preserving safety and baseline structure.
- **`app/templates/index.html`**: User-friendly form collecting physical metrics, primary goal, and workout intensity with double-submission protection.
- **`app/templates/result.html`**: Comprehensive dashboard rendering day-by-day workout cards, nutrition advice, user summary metrics, and the plan update interface.
- **`app/templates/all_users.html`**: Administrative view listing all saved profiles.

---

## Requirements

- **Python 3.10+** (tested on Python 3.10 – 3.14)
- **Google Gemini API Key** (obtainable from [Google AI Studio](https://aistudio.google.com/))
- **Web Browser** (Chrome, Firefox, Edge, Safari)

---

## Installation

Open **Windows PowerShell** (or your terminal) and run:

1. **Clone or extract** the project into your preferred directory.
2. **Open a terminal** inside the project root folder.
3. **Create a virtual environment:**
   ```powershell
   python -m venv venv
   ```
4. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   *(On macOS/Linux: `source venv/bin/activate`)*

5. **Install the dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

---

## Environment Setup

1. Copy the example environment file to create your active `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   *(On macOS/Linux: `cp .env.example .env`)*

2. Open `.env` in a text editor and add your personal Google Gemini API key:
   ```ini
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   WORKOUT_MODEL=gemini-3.8-flash
   NUTRITION_MODEL=gemini-3.8-flash
   DATABASE_URL=sqlite:///./fitbuddy.db
   DEMO_MODE=false
   ```

> **Note:** If `GEMINI_API_KEY` is not provided or Gemini is unreachable, FitBuddy automatically engages its local fallback generator so you can still test and use the application completely offline.

---

## Run

With your virtual environment activated, start the Uvicorn development server:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Or on Windows, you can simply double-click or execute:
```cmd
run.bat
```

Once started, open your web browser and navigate to:
```
http://127.0.0.1:8001/
```

---

## API Documentation

FastAPI provides interactive Swagger documentation automatically. With the server running, visit:
- **Interactive Swagger UI:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Alternative ReDoc UI:** [http://127.0.0.1:8001/redoc](http://127.0.0.1:8001/redoc)
- **System Health Check:** [http://127.0.0.1:8001/health](http://127.0.0.1:8001/health)

---

## Important Security Note

- **Never commit or distribute `.env`**: The `.env` file contains your private API key and must remain local to your machine. It is already listed in `.gitignore`.
- **Keep API Keys Confidential**: Do not post API keys in issues, chat messages, or public code repositories.
- **Individual Keys**: Each user or developer running FitBuddy should generate their own API key from [Google AI Studio](https://aistudio.google.com/).
