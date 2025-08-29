# File: main_window.py
from datetime import datetime
import sys
import ollama

from PyQt6.QtWidgets import QMainWindow, QToolBar, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, \
    QScrollArea, QSizePolicy, QTextEdit
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, pyqtSignal


class GPTClientUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Janet" + " - GPT Client")
        self.setGeometry(100, 100, 1200, 800)


    def start_new_conversation(self):
        """
        Saves the current conversation and initializes a new one.
        """

    def save_current_conversation(self):
        """
        Saves the current conversation to a YAML file, updating the last_updated timestamp.
        """


    def send_message(self):
        """
        Send user a message to GPT.
        """