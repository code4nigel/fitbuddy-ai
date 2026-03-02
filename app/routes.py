from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel # Added for Activity 2.1 schema validation

from app.database import SessionLocal, User, WorkoutPlan
from app.gemini_generator import generate_workout_gemini, generate_nutrition_tip_with_flash, update_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# --- ACTIVITY 2.1: PYDANTIC SCHEMAS ---
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
# ---------------------------------------

@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route updated to /generate-workout
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
    # Validate structure using Pydantic
    user_data = UserInput(
        username=username, 
        user_id=user_id, 
        age=age, 
        weight=weight, 
        goal=goal, 
        intensity=intensity
    )

    # Use renamed Gemini functions
    plan = generate_workout_gemini(user_data.username, user_data.age, user_data.weight, user_data.goal, user_data.intensity)
    nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)

    db = SessionLocal()
    try:
        new_user = User(
            username=user_data.username, 
            user_id=user_data.user_id, 
            age=user_data.age, 
            weight=user_data.weight, 
            goal=user_data.goal, 
            intensity=user_data.intensity
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        new_plan = WorkoutPlan(user_id=new_user.id, original_plan=plan, nutrition_tip=nutrition_tip)
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan) 
    finally:
        db.close()

    return templates.TemplateResponse(
        "result.html",
        {"request": request, "plan": plan, "nutrition_tip": nutrition_tip, "plan_id": new_plan.id}
    )

# Route updated to /submit-feedback
@router.post("/submit-feedback", response_class=HTMLResponse)
def update_plan(
    request: Request,
    plan_id: int = Form(...),
    feedback: str = Form(...)
):
    # Validate structure using Pydantic
    feedback_data = FeedbackRequest(plan_id=plan_id, feedback=feedback)

    db = SessionLocal()
    try:
        db_plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == feedback_data.plan_id).first()
        
        if not db_plan:
            return HTMLResponse("Plan not found", status_code=404)

        updated_plan_text = update_workout_plan(db_plan.original_plan, feedback_data.feedback)

        db_plan.original_plan = updated_plan_text
        db.commit()
        
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
        users = db.query(User).all()
    finally:
        db.close()

    return templates.TemplateResponse(
        "all_users.html", 
        {"request": request, "users": users}
    )