from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import time

from app.database import SessionLocal, User, WorkoutPlan, save_user, save_plan, update_plan, get_all_users, get_all_plans
from app.gemini_generator import generate_workout_gemini, generate_nutrition_tip_with_flash, update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

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
    user_data = UserInput(
        username=username, user_id=user_id, age=age, 
        weight=weight, goal=goal, intensity=intensity
    )

    # 1. Generate Workout Plan
    plan = generate_workout_gemini(user_data.username, user_data.age, user_data.weight, user_data.goal, user_data.intensity)
    
    # Pause for 2 seconds to avoid Google Free Tier spam blockers
    time.sleep(2) 

    # 2. Generate Nutrition Tip
    nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)

    db = SessionLocal()
    try:
        user = save_user(db, user_data)
        new_plan = save_plan(db, user.id, plan, nutrition_tip)
    finally:
        db.close()

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request, 
            "username": user_data.username,
            "goal": user_data.goal,
            "intensity": user_data.intensity,
            "workout_plan": plan, 
            "nutrition_tip": nutrition_tip, 
            "plan_id": new_plan.id
        }
    )

@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    plan_id: int = Form(...),
    feedback: str = Form(...)
):
    feedback_data = FeedbackRequest(plan_id=plan_id, feedback=feedback)

    db = SessionLocal()
    try:
        db_plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == feedback_data.plan_id).first()
        if not db_plan:
            return HTMLResponse("Plan not found", status_code=404)

        user = db.query(User).filter(User.id == db_plan.user_id).first()

        updated_plan_text = update_workout_plan(db_plan.original_plan, feedback_data.feedback)
        update_plan(db, feedback_data.plan_id, updated_plan_text)
        
        nutrition_tip = db_plan.nutrition_tip
        
        # 🔥 FIX: We must extract these attributes BEFORE the db.close() runs!
        safe_username = user.username
        safe_goal = user.goal
        safe_intensity = user.intensity
        
    finally:
        db.close() # The database connection is closed here

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request, 
            "username": safe_username,    # Using the safe, extracted variables
            "goal": safe_goal,            # instead of the disconnected "user" object
            "intensity": safe_intensity,
            "workout_plan": updated_plan_text, 
            "nutrition_tip": nutrition_tip, 
            "plan_id": feedback_data.plan_id,
            "success_message": "✅ Success! Your plan has been dynamically updated based on your feedback." 
        }
    )

@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    db = SessionLocal()
    try:
        users = get_all_users(db)
        plans = get_all_plans(db)
    finally:
        db.close()

    return templates.TemplateResponse(
        "all_users.html", 
        {"request": request, "users": users, "plans": plans}
    )