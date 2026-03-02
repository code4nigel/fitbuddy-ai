from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def generate_flash_workout_plan(name, age, weight, goal, intensity): 
    # Combine the form variables into a single prompt
    prompt = f"Act as an expert personal trainer. Create a highly detailed, {intensity} workout plan for {name}. They are {age} years old, weigh {weight}kg/lbs, and their primary fitness goal is: {goal}."
    
    # Call the 2.5-flash model
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=prompt
    )
    
    return response.text