from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    user_id = Column(String)
    age = Column(Integer)
    weight = Column(Integer)
    goal = Column(String)
    intensity = Column(String)

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    original_plan = Column(Text)
    updated_plan = Column(Text, nullable=True) # Used to store the feedback revision
    nutrition_tip = Column(String, nullable=True)

# ==========================================
# 🚀 REQUIRED HELPER FUNCTIONS
# ==========================================

def save_user(db, user_data):
    # Using Pydantic data to save the user
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
    return new_user

def save_plan(db, user_id, original_plan, nutrition_tip):
    new_plan = WorkoutPlan(user_id=user_id, original_plan=original_plan, nutrition_tip=nutrition_tip)
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)
    return new_plan

def update_plan(db, plan_id, revised_plan_text):
    db_plan = db.query(WorkoutPlan).filter(WorkoutPlan.id == plan_id).first()
    if db_plan:
        db_plan.updated_plan = revised_plan_text # Save the revised version
        db_plan.original_plan = revised_plan_text # Update main display
        db.commit()
        db.refresh(db_plan)
    return db_plan

def get_all_users(db):
    return db.query(User).all()

def get_all_plans(db):
    return db.query(WorkoutPlan).all()