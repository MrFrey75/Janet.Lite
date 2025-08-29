from datetime import datetime
import sys
# Removed 'import ollama' as it's now handled by the Orchestrator
import yaml
import os

from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal

# Import the Orchestrator
from src.janet_lite.services.orchestrator import Orchestrator


class GPTClientUI(QMainWindow):
    """
    Main UI for the GPT client, now integrated with the Orchestrator.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Janet" + " - GPT Client")
        self.setGeometry(100, 100, 1200, 800)

        # Track conversation state
        self.current_conversation = []
        self.conversation_file = None

        # Instantiate the Orchestrator to handle message processing and logic
        self.orchestrator = Orchestrator()

        # --- UI Elements ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message...")
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

        # Connect enter key to send message
        self.input_field.returnPressed.connect(self.send_message)

    def start_new_conversation(self):
        """Saves the current conversation and initializes a new one."""
        if self.current_conversation:
            self.save_current_conversation()
        self.current_conversation = []
        self.chat_display.clear()
        self.conversation_file = None

    def save_current_conversation(self):
        """Saves the current conversation to a YAML file."""
        if not self.current_conversation:
            QMessageBox.information(self, "Save", "No conversation to save.")
            return

        if not self.conversation_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Conversation", "conversation.yaml",
                                                       "YAML Files (*.yaml)")
            if not file_name:
                return
            self.conversation_file = file_name

        conversation_data = {
            "last_updated": datetime.now().isoformat(),
            "messages": self.current_conversation
        }

        with open(self.conversation_file, 'w') as f:
            yaml.safe_dump(conversation_data, f)

        QMessageBox.information(self, "Save", f"Conversation saved to {self.conversation_file}")

    def perform_action(self, action_name: str):
        """
        Performs a specific action based on the name returned by the Orchestrator.
        """
        if action_name == "save_conversation":
            self.save_current_conversation()
            # Optionally, display a message confirming the action
            self.chat_display.append("Janet: The conversation has been saved.")
        else:
            QMessageBox.warning(self, "Action Error", f"Unknown action: {action_name}")

    def send_message(self):
        """
        Sends a user message to the Orchestrator and handles the response.
        """
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        # Display user message
        self.chat_display.append(f"You: {user_message}")
        self.input_field.clear()

        try:
            # Route the user message through the Orchestrator
            response = self.orchestrator.process_input(user_message)

            # Now, check the response type from the Orchestrator
            if response['type'] == 'action':
                # If it's an action, perform the action
                self.perform_action(response['content'])
            elif response['type'] == 'display':
                # If it's for display, append the content to the chat history
                self.chat_display.append(f"Janet: {response['content']}")
            else:
                # Handle unexpected response types
                QMessageBox.critical(self, "Error", f"Unexpected response type from orchestrator: {response['type']}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process message: {str(e)}")
