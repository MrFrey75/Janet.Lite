from datetime import datetime
import sys
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QSizePolicy, QTextEdit, QFileDialog, QMessageBox,
    QPushButton, QApplication, QStatusBar
)
from PyQt6.QtGui import QAction, QIcon, QTextCursor, QTextCharFormat, QColor
from PyQt6.QtCore import Qt

from src.janet_lite.models.user_task import UserTask, Conversation, TaskAction
from src.janet_lite.services.orchestrator import Orchestrator


class GPTClientUI(QMainWindow):
    """
    Main UI for the GPT client, now integrated with the Orchestrator.
    """

    def __init__(self):
        super().__init__()

        self.intent = None
        self.setWindowTitle("Janet - GPT Client")
        self.setGeometry(100, 100, 1200, 800)

        # Track conversation state
        self.conversation = Conversation()
        self.current_task: UserTask | None = None

        # Instantiate the Orchestrator
        self.orchestrator = Orchestrator()

        # Add a status bar
        self.setStatusBar(QStatusBar())

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
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type your message...")
        self.input_field.setFixedHeight(100)

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

        # Autofocus
        self.input_field.setFocus()

        # Override keypress for Enter vs Shift+Enter
        self.input_field.keyPressEvent = self.handle_input_key_press

    def handle_input_key_press(self, event):
        """Custom event handler for key presses in the input field."""
        if event.key() == Qt.Key.Key_Return and not (
            event.modifiers() & Qt.KeyboardModifier.ShiftModifier or event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # Enter alone sends the message
            self.send_message()
            event.accept()
        elif event.key() == Qt.Key.Key_Return and (
            event.modifiers() & Qt.KeyboardModifier.ShiftModifier or event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # Shift+Enter or Ctrl+Enter adds a new line
            self.input_field.insertPlainText("\n")
            event.accept()
        else:
            QTextEdit.keyPressEvent(self.input_field, event)

    def append_colored_text(self, text: str, color: str):
        """Helper to insert colored text into chat display."""
        cursor: QTextCursor = self.chat_display.textCursor()
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.insertText(text + "\n")
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def send_message(self):
        """
        Sends a user message to the Orchestrator and handles the response.
        """
        user_message = self.input_field.toPlainText().strip()
        if not user_message:
            return

        # Display user message in blue
        self.append_colored_text(f"You: {user_message}", "#1E90FF")  # Dodger Blue
        self.input_field.clear()
        self.statusBar().showMessage("Sending query to Janet...")

        try:
            # Create a proper UserTask
            self.current_task = UserTask(user_query=user_message, prompt=user_message)
            self.orchestrator.current_task = self.current_task

            # Get the intent from the orchestrator
            self.intent = self.orchestrator.get_intent(user_message)
            print(f"Detected intent: {self.intent}")
            self.current_task.intent = self.intent

            # Route the user message through the Orchestrator
            response_task = self.orchestrator.process_input(self.current_task)

            # Save to conversation history
            self.conversation.tasks.append(response_task)

            # Display response
            self.display_response(response_task)

            self.statusBar().showMessage("Ready", 3000)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process message: {str(e)}")
            self.statusBar().showMessage("Error processing message", 3000)

    def display_response(self, response_task: UserTask):
        """Displays the response from the Orchestrator."""
        if response_task.response:
            # Show Janet’s responses in green
            self.append_colored_text(f"Janet: {response_task.response}", "#228B22")  # Forest Green
        else:
            self.append_colored_text("Janet: [No response]", "#228B22")


# Run standalone
if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = GPTClientUI()
    client.show()
    sys.exit(app.exec())