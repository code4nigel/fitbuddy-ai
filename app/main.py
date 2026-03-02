import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router
from app.database import Base, engine

# 1. Ensure the SQLite database tables are created
Base.metadata.create_all(bind=engine)

# 2. Initialize the FastAPI application
app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")

# 3. Mount static files safely (prevents crashes if the folder doesn't exist yet)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. Include all the routes we built in app/routes.py
app.include_router(router)