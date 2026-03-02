from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# 1. Renamed to match Activity 2.1 instructions
def generate_workout_gemini(username, age, weight, goal, intensity): 
    prompt = f"Act as an expert personal trainer. Create a detailed, {intensity} workout plan for {username}. They are {age} years old, weigh {weight}kg/lbs, and their primary goal is: {goal}."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    # 🔥 FIX: Added the missing return statement!
    return response.text

# 2. Renamed to match Activity 2.1 instructions
def generate_nutrition_tip_with_flash(goal):
    prompt = f"Give me one highly effective, actionable, and short nutrition tip for someone whose main fitness goal is: {goal}."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    # 🔥 FIX: Added the missing return statement!
    return response.text

# 3. Matches Activity 2.1 instructions
def update_workout_plan(current_plan, feedback):
    prompt = f"Here is a user's current fitness plan:\n{current_plan}\n\nThe user provided this feedback: '{feedback}'. Please rewrite and update the workout plan to accommodate this feedback while keeping it effective."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    return response.text