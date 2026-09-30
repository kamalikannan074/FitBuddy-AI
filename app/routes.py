
import os

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.ai.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.ai.gemini_generator import generate_workout_gemini
from app.ai.updated_plan import update_workout_plan

from app.database import (
    get_all_plans,
    get_all_users,
    get_original_plan,
    get_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
    delete_user
)

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()


# ============================================================
# LOCAL / DEMO WORKOUT
# ============================================================

def create_demo_workout(username, age, weight, goal, intensity):

    return f"""
7-DAY WORKOUT PLAN

User: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Fitness Level: {intensity}

Day 1:
- Bodyweight Squats
- Push-ups
- Walking
- 3 sets each
- 10-12 repetitions
- Rest 60 seconds

Day 2:
- Brisk Walking
- Light Stretching
- 20-30 minutes
- Focus on recovery

Day 3:
- Lunges
- Glute Bridges
- Plank
- 3 sets
- 10-12 repetitions
- Rest 60 seconds

Day 4:
- Rest Day
- Light stretching
- Drink enough water

Day 5:
- Shoulder Press
- Knee Push-ups
- Bicep Curls
- 3 sets
- 10-12 repetitions
- Rest 60 seconds

Day 6:
- Light Jogging or Walking
- Full Body Stretching
- 20-30 minutes

Day 7:
- Complete Rest
- Recovery and stretching

Note:
The local workout plan was used because AI generation
was temporarily unavailable.
"""


# ============================================================
# LOCAL / DEMO NUTRITION
# ============================================================

def create_demo_nutrition_tip(goal):

    return f"""
NUTRITION TIP FOR {goal}

- Eat enough protein from eggs, milk, fish, chicken,
  beans, lentils or other protein-rich foods.
- Choose healthy carbohydrates such as rice, oats,
  whole grains, fruits and vegetables.
- Include healthy fats such as nuts, seeds and
  moderate amounts of healthy oils.
- Drink enough water throughout the day.
- Maintain a balanced diet and avoid excessive
  processed food.

Note:
This nutrition tip is generated locally because the
AI nutrition service was temporarily unavailable.
"""


# ============================================================
# LOCAL UPDATED WORKOUT
# ============================================================

def create_demo_updated_plan(
    username,
    age,
    weight,
    goal,
    intensity,
    feedback
):

    return f"""
UPDATED 7-DAY WORKOUT PLAN

User: {username}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Fitness Level: {intensity}

USER FEEDBACK:
{feedback}

The workout plan has been adjusted based on the feedback.

Day 1:
- Bodyweight Squats
- Wall Push-ups
- Light Walking
- 2-3 sets
- 10-12 repetitions
- Rest 60 seconds

Day 2:
- Brisk Walking
- Light Stretching
- 20-30 minutes
- Focus on comfortable movement

Day 3:
- Lunges
- Glute Bridges
- Modified Plank
- 2-3 sets
- 10-12 repetitions
- Rest 60-90 seconds

Day 4:
- Rest Day
- Gentle stretching
- Recovery
- Drink enough water

Day 5:
- Shoulder Press
- Knee Push-ups
- Light Bicep Curls
- 2-3 sets
- 10-12 repetitions
- Rest 60-90 seconds

Day 6:
- Walking or Light Jogging
- Full Body Stretching
- 20-30 minutes

Day 7:
- Complete Rest
- Recovery and light stretching

WARM-UP:
5-10 minutes of easy walking and gentle movements
before starting the workout.

COOL-DOWN:
5-10 minutes of slow walking and gentle stretching
after the workout.

SAFETY NOTE:
Stop exercising if you experience unusual pain,
dizziness or difficulty breathing. Adjust exercise
intensity according to your comfort and ability.

Note:
The updated plan was generated locally because the
AI update service was temporarily unavailable.
"""


# ============================================================
# HOME PAGE
# ============================================================

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None,
            "message": None
        }
    )


# ============================================================
# GENERATE WORKOUT
# ============================================================

@router.post("/generate-workout", response_class=HTMLResponse)
async def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):

    username = username.strip()
    user_id = user_id.strip()
    goal = goal.strip()
    intensity = intensity.strip()

    # --------------------------------------------------------
    # BASIC VALIDATION
    # --------------------------------------------------------

    if not username:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please enter your name.",
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity
            }
        )

    if not user_id:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please enter a User ID.",
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity
            }
        )

    if age < 13 or age > 100:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please enter an age between 13 and 100.",
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity
            }
        )

    if weight <= 0 or weight > 500:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please enter a valid weight.",
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity
            }
        )

    # --------------------------------------------------------
    # FITNESS LEVEL VALIDATION
    # --------------------------------------------------------

    allowed_intensities = {
        "beginner",
        "intermediate",
        "advanced",
        "moderate",
        "low",
        "medium",
        "high"
    }

    if intensity.lower() not in allowed_intensities:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please select a valid fitness level.",
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity
            }
        )

    if not goal:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please select or enter a fitness goal.",
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity
            }
        )

    # --------------------------------------------------------
    # GENERATE PLAN
    # --------------------------------------------------------

    try:

        print("=" * 60)
        print("FITBUDDY: GENERATING WORKOUT")
        print("User:", username)
        print("User ID:", user_id)
        print("Age:", age)
        print("Weight:", weight)
        print("Goal:", goal)
        print("Fitness Level:", intensity)
        print("=" * 60)

        # ----------------------------------------------------
        # WORKOUT GENERATION
        # ----------------------------------------------------

        try:

            workout_plan = generate_workout_gemini(
                username=username,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity
            )

            print("Workout generated successfully.")

        except Exception as workout_error:

            print("=" * 60)
            print("WORKOUT AI UNAVAILABLE")
            print(str(workout_error))
            print("Using local workout plan.")
            print("=" * 60)

            workout_plan = create_demo_workout(
                username,
                age,
                weight,
                goal,
                intensity
            )

        # ----------------------------------------------------
        # NUTRITION GENERATION
        # ----------------------------------------------------

        try:

            nutrition_tip = generate_nutrition_tip_with_flash(
                goal=goal
            )

            print("Nutrition generated successfully.")

        except Exception as nutrition_error:

            print("=" * 60)
            print("NUTRITION AI UNAVAILABLE")
            print(str(nutrition_error))
            print("Using local nutrition tip.")
            print("=" * 60)

            nutrition_tip = create_demo_nutrition_tip(
                goal
            )

        # ----------------------------------------------------
        # SAVE USER
        # ----------------------------------------------------

        save_user(
            user_id=user_id,
            username=username,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity
        )

        print("User saved successfully.")

        # ----------------------------------------------------
        # SAVE PLAN
        # ----------------------------------------------------

        save_plan(
            user_id=user_id,
            original_plan=workout_plan,
            nutrition_tip=nutrition_tip
        )

        print("Plan saved successfully.")

        # ----------------------------------------------------
        # SHOW RESULT PAGE
        # ----------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity,
                "workout_plan": workout_plan,
                "nutrition_tip": nutrition_tip,
                "updated_plan": None,
                "feedback": None,
                "message": "Workout plan generated successfully!",
                "error": None
            }
        )

    except Exception as exc:

        print("=" * 60)
        print("FITBUDDY ERROR")
        print(str(exc))
        print("=" * 60)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": (
                    "Unable to generate the plan. "
                    f"Details: {str(exc)}"
                ),
                "username": username,
                "user_id": user_id,
                "age": age,
                "weight": weight,
                "goal": goal,
                "intensity": intensity
            }
        )


# ============================================================
# SUBMIT FEEDBACK
# ============================================================

@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...)
):

    user_id = user_id.strip()
    feedback = feedback.strip()

    if not user_id:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "User ID is required."
            }
        )

    if not feedback:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": "Please enter feedback."
            }
        )

    try:

        # ----------------------------------------------------
        # GET USER
        # ----------------------------------------------------

        user = get_user(user_id)

        if user is None:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": "User not found."
                }
            )

        # ----------------------------------------------------
        # GET ORIGINAL PLAN
        # ----------------------------------------------------

        original_plan = get_original_plan(user_id)

        if original_plan is None:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": "Original workout plan not found."
                }
            )

        print("=" * 60)
        print("GENERATING UPDATED WORKOUT PLAN")
        print("User:", user.username)
        print("User ID:", user.user_id)
        print("Feedback:", feedback)
        print("=" * 60)

        # ----------------------------------------------------
        # TRY AI UPDATED PLAN
        # ----------------------------------------------------

        try:

            updated_plan = update_workout_plan(
                original_plan=original_plan.original_plan,
                feedback=feedback,
                username=user.username,
                age=user.age,
                weight=user.weight,
                goal=user.goal,
                intensity=user.intensity
            )

            print("Updated workout generated successfully.")

        except Exception as update_error:

            print("=" * 60)
            print("UPDATED PLAN AI UNAVAILABLE")
            print(str(update_error))
            print("Using local updated workout plan.")
            print("=" * 60)

            updated_plan = create_demo_updated_plan(
                username=user.username,
                age=user.age,
                weight=user.weight,
                goal=user.goal,
                intensity=user.intensity,
                feedback=feedback
            )

        # ----------------------------------------------------
        # SAVE UPDATED PLAN
        # ----------------------------------------------------

        update_plan(
            user_id=user_id,
            updated_plan=updated_plan,
            feedback=feedback
        )

        print("Updated plan saved successfully.")

        # ----------------------------------------------------
        # GET LATEST PLAN
        # ----------------------------------------------------

        latest_plan = get_plan(user_id)

        # ----------------------------------------------------
        # SHOW UPDATED RESULT
        # ----------------------------------------------------

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "username": user.username,
                "user_id": user.user_id,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "workout_plan": original_plan.original_plan,
                "nutrition_tip": original_plan.nutrition_tip,
                "updated_plan": updated_plan,
                "feedback": feedback,
                "message": "Workout plan updated successfully!",
                "error": None,
                "plan": latest_plan
            }
        )

    except Exception as exc:

        print("=" * 60)
        print("FEEDBACK ERROR")
        print(str(exc))
        print("=" * 60)

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"Unable to update the plan: {str(exc)}"
            }
        )


# ============================================================
# VIEW ALL USERS
# ============================================================

@router.get("/view-all-users", response_class=HTMLResponse)
async def view_all_users(request: Request):

    try:

        users = get_all_users()

        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={
                "users": users,
                "error": None
            }
        )

    except Exception as exc:

        print("=" * 60)
        print("VIEW USERS ERROR")
        print(str(exc))
        print("=" * 60)

        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={
                "users": [],
                "error": str(exc)
            }
        )


# ============================================================
# VIEW USER
# ============================================================

@router.get("/user/{user_id}", response_class=HTMLResponse)
async def view_user(
    request: Request,
    user_id: str
):

    try:

        user = get_user(user_id)

        if user is None:
            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "error": "User not found."
                }
            )

        plan = get_plan(user_id)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "username": user.username,
                "user_id": user.user_id,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "workout_plan": (
                    plan.original_plan
                    if plan else None
                ),
                "nutrition_tip": (
                    plan.nutrition_tip
                    if plan else None
                ),
                "updated_plan": (
                    plan.updated_plan
                    if plan else None
                ),
                "feedback": (
                    plan.feedback
                    if plan else None
                ),
                "message": None,
                "error": None
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": str(exc)
            }
        )


# ============================================================
# DELETE USER
# ============================================================

@router.post("/delete-user/{user_id}")
async def remove_user(user_id: str):

    try:

        delete_user(user_id)

        return {
            "success": True,
            "message": "User deleted successfully."
        }

    except Exception as exc:

        return {
            "success": False,
            "message": str(exc)
        }


# ============================================================
# API - GET ALL USERS
# ============================================================

@router.get("/api/users")
async def api_users():

    users = get_all_users()

    return {
        "success": True,
        "count": len(users),
        "users": [
            {
                "user_id": user.user_id,
                "username": user.username,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "created_at": user.created_at
            }
            for user in users
        ]
    }


# ============================================================
# API - GET USER PLAN
# ============================================================

@router.get("/api/users/{user_id}/plan")
async def api_user_plan(user_id: str):

    user = get_user(user_id)
    plan = get_plan(user_id)

    if user is None:
        return {
            "success": False,
            "message": "User not found."
        }

    if plan is None:
        return {
            "success": False,
            "message": "Plan not found."
        }

    return {
        "success": True,
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity
        },
        "plan": {
            "id": plan.id,
            "original_plan": plan.original_plan,
            "updated_plan": plan.updated_plan,
            "nutrition_tip": plan.nutrition_tip,
            "feedback": plan.feedback,
            "plan_type": plan.plan_type,
            "created_at": plan.created_at
        }
    }


# ============================================================
# API - GET ALL PLANS
# ============================================================

@router.get("/api/plans")
async def api_plans():

    plans = get_all_plans()

    return {
        "success": True,
        "count": len(plans),
        "plans": [
            {
                "id": plan.id,
                "user_id": plan.user_id,
                "original_plan": plan.original_plan,
                "updated_plan": plan.updated_plan,
                "nutrition_tip": plan.nutrition_tip,
                "feedback": plan.feedback,
                "plan_type": plan.plan_type,
                "created_at": plan.created_at
            }
            for plan in plans
        ]
    }


# ============================================================
# DEMO TEST ROUTE
# ============================================================

@router.get("/demo")
async def demo():

    return {
        "message": "FitBuddy API is working.",
        "demo_mode": os.getenv(
            "DEMO_MODE",
            "false"
        )
    }