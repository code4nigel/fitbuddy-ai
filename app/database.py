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
    # Updated to match the specific form inputs requested
    username = Column(String)
    user_id = Column(String) 
    age = Column(Integer)
    weight = Column(Integer)
    goal = Column(String)
    intensity = Column(String)


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer) # This links back to the User.id primary key
    original_plan = Column(Text)
    updated_plan = Column(Text)
    nutrition_tip = Column(String, nullable=True)