from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_workout_plan(name, age, weight, goal, intensity): 
    # Combine the variables into a prompt for Gemini
    prompt = f"Act as an expert personal trainer. Create a detailed, {intensity} workout plan for {name}. They are {age} years old, weigh {weight}kg/lbs, and their primary goal is: {goal}."
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    return response.text