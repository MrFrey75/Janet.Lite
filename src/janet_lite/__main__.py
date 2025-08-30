# src/janet_twin/__main__.py
import sys
from PyQt6.QtWidgets import QApplication
from src.janet_lite.ui.main_window import GPTClientUI

def main():
    app = QApplication(sys.argv)
    window = GPTClientUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()