from dotenv import load_dotenv
import openai
import os

# Load environment variables from a .env file
load_dotenv(override=True)

# Set the API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_questions(subject, topic, question_type):
    prompt = f"Generate 5 {question_type} questions for Class 12 {subject} on the topic '{topic}'."
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or "gpt-4" if you have access
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message["content"]

# Test the function
print(generate_questions("Physics", "Thermodynamics", "MCQ"))