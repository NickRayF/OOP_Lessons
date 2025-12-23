import sys
from PySide6.QtWidgets import QApplication
from src.app import VectorEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VectorEditorWindow()
    window.show()
    sys.exit(app.exec())