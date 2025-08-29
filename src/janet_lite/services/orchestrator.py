import os
from typing import Dict, List, Optional, Any
import yaml
from dataclasses import dataclass
import requests
import ollama  # Import ollama to use in the generate response method


class Orchestrator:
    """
    Manages conversation flow and routes user input to the appropriate
    action or model response.
    """

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.current_task = None
        self.conversation_history = []
        self._initialize_models()

    @staticmethod
    def _load_config(config_path: str) -> Dict[str, Any]:
        """Loads configuration from a YAML file."""
        if not os.path.exists(config_path):
            return {}
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _initialize_models(self) -> None:
        """Initializes any required models or connections."""
        self.models = {}
        model_configs = self.config.get('models', {})
        for model_name, settings in model_configs.items():
            self.models[model_name] = self._setup_model(model_name, settings)

    def _setup_model(self, model_name: str, settings: Dict[str, Any]) -> Any:
        # Placeholder for model initialization logic
        pass

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Processes user input and returns a structured response for action or display.
        The response is a dictionary with 'type' and 'content' keys.
        """
        # First, add the user message to the conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Identify the task based on the user's input
        task = self._identify_task(user_input)

        if task.get('type') == 'action':
            # If the task is an action, we return the action type and content directly.
            # No LLM call is needed for a simple action.
            response = {'type': 'action', 'content': task['action']}
        else:
            # If no action is identified, we generate a response using the LLM.
            assistant_message = self._generate_response()
            # Add the assistant's response to the conversation history
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            response = {'type': 'display', 'content': assistant_message}

        return response

    @staticmethod
    def _identify_task(user_input: str) -> Dict[str, Any]:
        """
        Identifies a specific task or action from the user's input.
        This is a simple placeholder. In a real app, this would be more complex.
        """
        if user_input.lower().strip() == "save conversation":
            return {'type': 'action', 'action': 'save_conversation'}

        return {'type': 'display'}  # Default to a display task

    def _generate_response(self) -> str:
        """
        Generates a text response from the LLM based on conversation history.
        """
        try:
            llm_response = ollama.chat(model="llama2", messages=self.conversation_history)
            assistant_message = llm_response['message']['content']
            return assistant_message
        except Exception as e:
            return f"An error occurred while generating a response: {str(e)}"

    def reset_conversation(self) -> None:
        """Resets the conversation history and current task."""
        self.current_task = None
        self.conversation_history = []
