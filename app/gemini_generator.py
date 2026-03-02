import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1"}  
)

def generate_workout_plan(name, age, weight, goal, intensity):

    prompt = f"""
    Create a structured 7-day workout plan.

    Name: {name}
    Age: {age}
    Weight: {weight}
    Fitness Goal: {goal}
    Preferred Intensity: {intensity}

    Format:
    Day 1:
    Warm-up:
    Main workout:
    Cooldown:
    """

    response = client.models.generate_content(
        model="gemini-1.5-flash-latest",
        contents=prompt
    )

    return response.text