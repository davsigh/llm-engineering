import os
import requests
import json
import time
import re
from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import gradio as gr # oh yeah!

# Load environment variables
load_dotenv()

# Headers for web requests to avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Ollama configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")

# A generic system message - no more snarky adversarial AIs!

system_message = "You are a helpful assistant"

def call_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=30)
    response.raise_for_status()
    
    result = response.json()
    return result.get("response", "")

def message_gpt(prompt):
    full_prompt = f"{system_message}\n\nUser: {prompt}\nAssistant:"
    return call_ollama(full_prompt)

# here's a simple function

def shout(text):
    print(f"Shout has been called with input {text}")
    return text.upper()

shout("hello")

# The simplicty of gradio. This might appear in "light mode" - I'll show you how to make this in dark mode later.

# Adding share=True means that it can be accessed publically
# A more permanent hosting is available using a platform called Spaces from HuggingFace, which we will touch on next week
# NOTE: Some Anti-virus software and Corporate Firewalls might not like you using share=True. If you're at work on on a work network, I suggest skip this test.

#gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never").launch(share=True)
# Inputs and Outputs

view = gr.Interface(
    fn=message_gpt,
    inputs=[gr.Textbox(label="Your message:", lines=6)],
    outputs=[gr.Textbox(label="Response:", lines=8)],
    flagging_mode="never",
)
view.launch(share=True)


# Step-by-Step Breakdown: Gradio AI Chat Interface
# 1. Environment Setup
# Import required libraries including gradio, requests, os, and dotenv
# Load environment variables from .env file using load_dotenv()
# 2. Configuration
# Set HTTP headers with User-Agent to avoid being blocked by web servers
# Configure Ollama server URL (defaults to http://localhost:11434/api/generate)
# Configure Ollama model name (defaults to llama3.2:latest)
# Define system message for AI behavior: "You are a helpful assistant"
# 3. Core AI Communication Function
# Create call_ollama(prompt) function
# Build JSON payload with model name, prompt text, and streaming disabled
# Send POST request to Ollama server with 30-second timeout
# Parse JSON response and extract the "response" field
# Return AI-generated text or empty string if failed
# 4. High-Level Messaging Function
# Create message_gpt(prompt) function
# Format user input into conversational structure with system message
# Combine system message, user prompt, and assistant role indicator
# Call call_ollama() with formatted prompt
# Return AI response
# 5. Test Function (Optional)
# Define shout(text) function for demonstration
# Convert input text to uppercase
# Print function call details to console
# Execute test call with "hello"
# 6. Gradio Interface Setup
# Create gr.Interface object with AI function as backend
# Configure input textbox with 6 lines and "Your message:" label
# Configure output textbox with 8 lines and "Response:" label
# Disable flagging feature for cleaner interface
# 7. Launch Application
# Call view.launch(share=True) to start web server
# Enable public sharing for external access
# Application becomes accessible via web browser
# Users can input messages and receive AI responses in real-time
# 8. User Interaction Flow
# User types message in input textbox
# Message gets processed through message_gpt() function
# Formatted prompt sent to local Ollama server
# AI response displayed in output textbox
# Process repeats for each new user input