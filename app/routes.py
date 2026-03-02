from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# ✅ ADD THESE IMPORTS
from app.database import SessionLocal, User, WorkoutPlan
from app.gemini_generator import generate_workout_plan

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate", response_class=HTMLResponse)
def generate_plan(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: int = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):

    # 🔥 1️⃣ Generate plan using Gemini
    plan = generate_workout_plan(name, age, weight, goal, intensity)

    # 🔥 2️⃣ Save to database
    db = SessionLocal()

    # Save user
    new_user = User(
        name=name,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Save workout plan
    new_plan = WorkoutPlan(
        user_id=new_user.id,
        original_plan=plan
    )

    db.add(new_plan)
    db.commit()

    db.close()

    # 🔥 3️⃣ Return result page
    return templates.TemplateResponse(
        "result.html",
        {"request": request, "plan": plan}
    )