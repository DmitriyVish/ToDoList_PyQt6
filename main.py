import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import ToDoApp
from gui.deadline_item import DeadlineTableWidgetItem


def main():
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()