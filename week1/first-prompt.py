import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display
import json

load_dotenv(override=True)
# Using Ollama instead of OpenAI

# Headers for web requests
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest" # Change to your preferred model

class Website:
    def __init__(self, url):
        """
        Create this Website object from the given url using the BeautifulSoup library
        """
        self.url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        self.text = soup.body.get_text(separator="\n", strip=True)

# Step 1: Create your prompts
system_prompt = "You are an assistant that analyzes the contents of a website \
and provides a short summary, ignoring text that might be navigation related. \
Respond in markdown."

def user_prompt_for(website):
    user_prompt = "\nThe contents of this website is as follows; \
please provide a short summary of this website in markdown. \
If it includes news or announcements, then summarize these too. Add all the links\n\n"
    user_prompt += f"Title: {website.title}\n\n"
    user_prompt += f"Text: {website.text}\n\n"
    return user_prompt

# Step 2: Call Ollama
def get_ollama_response(prompt, system_prompt):
    try:
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_URL, json=payload)
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

# Example usage
if __name__ == "__main__":
    # Get website content
    url = "https://www.kdnuggets.com/10-github-repositories-to-master-web-development-in-2025"
    ed = Website(url)
    print(f"Analyzing website: {ed.title}")
    
    # Generate prompt
    user_prompt = user_prompt_for(ed)
    
    # Get summary from Ollama
    summary = get_ollama_response(user_prompt, system_prompt)
    
    # Display the result
    print("\nSummary from Ollama:")
    print(summary)
    
    # If running in a notebook, you can use the following to display markdown
    # display(Markdown(summary))

