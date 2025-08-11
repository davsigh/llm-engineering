import os
import requests
import json
from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup

# Headers for web requests to avoid being blocked
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"  # Change to your preferred model

class Website:
    """
    A utility class to represent a Website that we have scraped, including links
    """
    def __init__(self, url):
        self.url = url
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            self.body = response.content
            soup = BeautifulSoup(self.body, 'html.parser')
            self.title = soup.title.string if soup.title else "No title found"
            
            if soup.body:
                for irrelevant in soup.body(["script", "style", "img", "input"]):
                    irrelevant.decompose()
                self.text = soup.body.get_text(separator="\n", strip=True)
            else:
                self.text = ""
                
            # Extract links and resolve relative URLs
            links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    # Convert relative links to absolute
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(url, href)
                    links.append(href)
            self.links = links
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            self.body = ""
            self.title = "Error fetching page"
            self.text = ""
            self.links = []

    def get_contents(self) -> str:
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

def get_ai_links_prompt(website: Website) -> str:
    """Generate a prompt for the AI to identify relevant AI news links"""
    system_prompt = "You are provided with a list of links found on a webpage. "
    system_prompt += "Identify only links that are relevant to artificial intelligence news, "
    system_prompt += "such as new research, product announcements, or industry developments. "
    system_prompt += "Respond with valid JSON in this exact format:\n"
    system_prompt += """
    {
        "links": [
            {"type": "News", "url": "https://www.artificialintelligence-news.com/news/googles-newest-gemini-2-5-model-aims-intelligence-per-dollar/"},
            {"type": "Research", "url": "https://www.artificialintelligence-news.com/news/alibaba-new-qwen-reasoning-ai-model-open-source-records/"}
        ]
    }
    """
    
    user_prompt = f"Here is the list of links from {website.url}.\n"
    user_prompt += "Please identify only links that contain artificial intelligence news:\n"
    user_prompt += "\n".join(website.links[:100])  # Limit to first 100 links to avoid token limits
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return full_prompt

def get_article_summary_prompt(article: Website) -> str:
    """Generate a prompt for the AI to summarize an article"""
    system_prompt = "You are an AI news summarizer that creates concise summaries of "
    system_prompt += "artificial intelligence news articles. Focus on key information: "
    system_prompt += "what happened, which companies/technologies are involved, and why it matters. "
    system_prompt += "Use neutral language and include only factual information from the article."
    
    user_prompt = f"Summarize this AI news article in 3-5 sentences:\n"
    user_prompt += f"Title: {article.title}\n\n"
    user_prompt += f"Content: {article.text[:3000]}"  # Limit to avoid token limits
    
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    return full_prompt

def call_ollama(prompt: str) -> str:
    """Call the Ollama API with a prompt and return the response"""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "No response generated")
    except requests.exceptions.RequestException as e:
        return f"Error calling Ollama API: {e}"
    except json.JSONDecodeError:
        return "Error: Invalid response from Ollama"

def extract_ai_news(url: str) -> str:
    """Extract and summarize AI news from a URL"""
    print(f"Fetching webpage: {url}")
    main_site = Website(url)
    if not main_site.links:
        return "No links found on the webpage."
    
    print("Identifying AI news links...")
    links_prompt = get_ai_links_prompt(main_site)
    links_response = call_ollama(links_prompt)
    
    # Try to parse the JSON response
    try:
        # Sometimes the model might include markdown code blocks or extra text
        json_str = links_response
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()
            
        links_data = json.loads(json_str)
        relevant_links = links_data.get("links", [])
        
        if not relevant_links:
            return "No relevant AI news links found on this page."
            
        print(f"Found {len(relevant_links)} relevant AI news links")
        
        # Get content from the first 3 links only
        results = ["# AI News Summary\n"]
        
        for i, link_info in enumerate(relevant_links[:3]):
            link_url = link_info.get("url")
            link_type = link_info.get("type", "Article")
            
            print(f"Fetching content from: {link_url}")
            article = Website(link_url)
            
            summary_prompt = get_article_summary_prompt(article)
            summary = call_ollama(summary_prompt)
            
            results.append(f"## {article.title}")
            # results.append(f"**Type**: {link_type}")
            results.append(f"**URL**: {link_url}\n")
            results.append(summary)
            results.append("\n---\n")
        
        return "\n".join(results)
        
    except json.JSONDecodeError as e:
        return f"Error parsing AI response: {e}\n\nRaw response: {links_response[:200]}..."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # url = input("Enter URL to extract AI news from: ")
        url = "https://bair.berkeley.edu/blog/"
    result = extract_ai_news(url)
    print("\n" + result)