from datetime import datetime
import sys
import ollama
import yaml
import os

from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QSizePolicy, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal


class GPTClientUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Janet" + " - GPT Client")
        self.setGeometry(100, 100, 1200, 800)

        # Track conversation state
        self.current_conversation = []
        self.conversation_file = None

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

    def start_new_conversation(self):
        """
        Saves the current conversation and initializes a new one.
        """
        if self.current_conversation:
            self.save_current_conversation()
        self.current_conversation = []
        self.chat_display.clear()
        self.conversation_file = None

    def save_current_conversation(self):
        """
        Saves the current conversation to a YAML file, updating the last_updated timestamp.
        """
        if not self.current_conversation:
            QMessageBox.information(self, "Save", "No conversation to save.")
            return

        if not self.conversation_file:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Conversation", "conversation.yaml", "YAML Files (*.yaml)")
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

    def send_message(self):
        """
        Send user message to GPT via Ollama.
        """
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        # Display user message
        self.chat_display.append(f"You: {user_message}")
        self.current_conversation.append({"role": "user", "content": user_message})
        self.input_field.clear()

        try:
            response = ollama.chat(model="llama2", messages=self.current_conversation)
            assistant_message = response['message']['content']

            # Display GPT response
            self.chat_display.append(f"Janet: {assistant_message}")
            self.current_conversation.append({"role": "assistant", "content": assistant_message})

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")

