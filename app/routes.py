from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import the new helper functions from database.py
from app.database import SessionLocal, WorkoutPlan, save_user, save_plan, update_plan, get_all_users, get_all_plans
from app.gemini_generator import generate_workout_gemini, generate_nutrition_tip_with_flash, update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# --- PYDANTIC SCHEMAS ---
class UserInput(BaseModel):
    username: str
    user_id: str
    age: int
    weight: int
    goal: str
    intensity: str

class FeedbackRequest(BaseModel):
    plan_id: int
    feedback: str
# ------------------------

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate-workout", response_class=HTMLResponse)
def generate_plan(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: int = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    # 1. Validate structure using Pydantic
    user_data = UserInput(
        username=username, user_id=user_id, age=age, 
        weight=weight, goal=goal, intensity=intensity
    )

    # 2. Call Gemini APIs
    plan = generate_workout_gemini(user_data.username, user_data.age, user_data.weight, user_data.goal, user_data.intensity)
    nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)

    # 3. Save using helper functions
    db = SessionLocal()
    try:
        user = save_user(db, user_data)
        new_plan = save_plan(db, user.id, plan, nutrition_tip)
    finally:
        db.close()

    return templates.TemplateResponse(
        "result.html",
        {"request": request, "plan": plan, "nutrition_tip": nutrition_tip, "plan_id": new_plan.id}
    )

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    plan_id: int = Form(...),
    feedback: str = Form(...)
):
    # 1. Validate structure using Pydantic
    feedback_data = FeedbackRequest(plan_id=plan_id, feedback=feedback)

    db = SessionLocal()
    try:
        # Fetch original plan to pass to AI
        db_plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == feedback_data.plan_id).first()
        if not db_plan:
            return HTMLResponse("Plan not found", status_code=404)

        # 2. Generate updated plan via Gemini
        updated_plan_text = update_workout_plan(db_plan.original_plan, feedback_data.feedback)

        # 3. Save to database using helper function
        update_plan(db, feedback_data.plan_id, updated_plan_text)
        
        nutrition_tip = db_plan.nutrition_tip
    finally:
        db.close()

    return templates.TemplateResponse(
        "result.html",
        {"request": request, "plan": updated_plan_text, "nutrition_tip": nutrition_tip, "plan_id": feedback_data.plan_id}
    )

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    db = SessionLocal()
    try:
        # Calls both get functions as requested
        users = get_all_users(db)
        plans = get_all_plans(db)
    finally:
        db.close()

    return templates.TemplateResponse(
        "all_users.html", 
        {"request": request, "users": users, "plans": plans}
    )