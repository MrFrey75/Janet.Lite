from datetime import datetime
import yaml
import os
import ollama
import json
import time
from typing import Dict, List, Optional, Any

from google.auth.transport import requests

from src.janet_lite.models.user_task import UserTask, Conversation, TaskAction

class Orchestrator:
    """
    Manages conversation flow and routes user input to the appropriate
    action or model response.
    """
    def __init__(self):
        # In a real application, you would load a config from a file.
        # For this self-contained example, we'll use a placeholder config.
        self.config = {'models': {'llama2': {}}}
        self.current_task = None
        self.conversation_history = []
        self.intents = self.load_intents('src/config/intent.yaml')

    @staticmethod
    def load_intents(file_path: str) -> Optional[List[Dict]]:
        """
        Loads intent definitions from a YAML file.
        """
        if not os.path.exists(file_path):
            print(f"Error: Intent configuration file not found at: {file_path}")
            return None
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
                return data.get('intents', [])
        except Exception as e:
            print(f"Error loading intent configuration: {e}")
            return None

    def get_intent(self, message: str) -> str:
        """
        Uses Ollama with llama2 to classify the intent of a message based on loaded data.
        """
        if not self.intents:
            return "general_query"  # Fallback if config isn't loaded

        # Dynamically build the list of categories for the prompt
        intent_names = [i['intent'] for i in self.intents]
        categories_list = "\n".join([f"- {name}" for name in intent_names])

        try:
            prompt = f"""
You are an intent classification assistant.
Classify the following user message into one of these categories:
{categories_list}

Samples for each category include"
{json.dumps(self.intents, indent=2)}

Message: "{message}"

Respond with one word,  only the category name.
"""
            result = ollama.chat(
                model="llama2",
                messages=[{"role": "user", "content": prompt}]
            )
            # Directly use the model's single-line response
            intent_response = result["message"]["content"].strip().lower()
            print(f"Model raw output: {result['message']['content']}")

            # Validate the response against the known intents
            if intent_response in intent_names:
                return intent_response
            else:
                print(f"Warning: Model returned an unknown intent: {intent_response}")
                return "general_query"

        except Exception as e:
            # Fallback if Ollama call fails
            print(f"Intent detection error: {e}")
            return "general_query"

    def do_google_search(self, query: str) -> str:
        GOOGLE_SEARCH_API = "https://www.googleapis.com/customsearch/v1"
        API_KEY = "AIzaSyAOIIoJUoEMvD7qOUEYKkewSRinxYYNhdo"  # Replace with actual API key
        SEARCH_ENGINE_ID = "51feee7a93400443e"  # Replace with actual search engine ID

        if not query:
            return "No search query provided"

        try:
            params = {
                'key': API_KEY,
                'cx': SEARCH_ENGINE_ID,
                'q': query
            }
            response = requests.get(GOOGLE_SEARCH_API, params=params)
            response.raise_for_status()

            results = response.json()
            if 'items' not in results:
                return "No results found"

            summary = []
            for item in results['items'][:3]:
                summary.append(f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item['snippet']}\n")

            return "\n".join(summary)

        except requests.RequestException as e:
            return f"Error performing search: {str(e)}"

    def process_input(self, task: UserTask) -> UserTask:
        """
        Processes user input and returns a structured response for action or display.
        """

        if not task or not task.user_query:
            raise ValueError("Invalid task or empty user query.")

        if task.intent == "general_query":
            return self.handle_general_query(task)

        if task.intent == "web_search":
            # Placeholder for web search handling
            task.response = self.do_google_search(task.user_query)
            task.timestamp = datetime.utcnow().isoformat() + 'Z'
            task.model = "web-search-model"
            task.prompt = task.user_query
            return task


        response = f"Echo: {task.user_query}"
        task.response = response
        task.timestamp = datetime.utcnow().isoformat() + 'Z'
        task.model = "echo-model"
        task.prompt = task.user_query
        return task

    def handle_general_query(self, task: UserTask) -> UserTask:
        """
        Handles general queries by routing to the appropriate model.
        """
        try:
            # For simplicity, we use a hardcoded model name. In a real app, this could be dynamic.
            model_name = "llama2"
            print(f"Routing to model: {model_name}")

            # Call Ollama to get the response
            result = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": task.user_query}]
            )

            # Extract and set the response
            task.response = result["message"]["content"]
            task.model = model_name
            task.prompt = task.user_query
            task.timestamp = datetime.utcnow().isoformat() + 'Z'

            return task

        except Exception as e:
            print(f"Error processing general query: {e}")
            task.response = "Sorry, I encountered an error processing your request."
            task.model = "error"
            task.prompt = task.user_query
            task.timestamp = datetime.utcnow().isoformat() + 'Z'
            return task
