import os  
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QMessageBox, QDateEdit,
    QTableWidget, QTableWidgetItem,
    QCommandLinkButton, QLabel, QGridLayout, QDialog
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QIcon
from core.todo_logic import NotePreprocessor
from gui.dialogs import DetailedNoteWindow, DetailedReadWindow
from gui.deadline_item import DeadlineTableWidgetItem
from config import APP_NAME, MAIN_WINDOW_TITLE


class ToDoApp(QMainWindow):
    """Главное окно приложения. Наследуется от QMainWindow"""
    def __init__(self):
        super().__init__()
        self.todo = NotePreprocessor()
        self.init_ui()
        self.load_notes()

    def init_ui(self):
        """Создает и настраивает интерфейс"""
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon("icon/icon.png"))  
        self.resize(600, 500)
        
        self.load_styles()        

        main = QWidget()
        self.setCentralWidget(main)
        VLayout = QVBoxLayout(main)

        title = QLabel(MAIN_WINDOW_TITLE)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Lucida Sans Unicode", 18, QFont.Weight.Bold))
        VLayout.addWidget(title)

        self.note_input = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.date_edit.setMaximumDate(QDate.currentDate().addDays(365 * 2))

        self.note_input.setPlaceholderText("Не стесняйтесь, вываливайте сюда свои дела! 🗑️")
        self.add_btn = QPushButton("➕ Добавить и забыть")
        self.write_note_btn = QPushButton("📝 Записать подробнее")
        self.write_note_btn.clicked.connect(self.open_detailed_note_window)
        self.add_btn.clicked.connect(self.add_note)

        self.deadline_text = QLabel("Deadline: или ты его, или он тебя!")
        self.deadline_text.setObjectName("deadline_text") # Важно для селектора QLabel#deadline_text
        self.deadline_text.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)

        grid = QGridLayout()
        grid.addWidget(self.note_input, 0, 0)
        grid.addWidget(self.add_btn, 0, 1)
        grid.addWidget(self.write_note_btn, 1, 1)
        deadline_layout = QHBoxLayout()
        deadline_layout.addWidget(self.deadline_text)
        deadline_layout.addWidget(self.date_edit)
        grid.addLayout(deadline_layout, 1, 0)
        VLayout.addLayout(grid)

        self.note_table = QTableWidget()
        self.note_table.setColumnCount(4)
        self.note_table.setHorizontalHeaderLabels([
            "Список дел выжившего",
            "Статус выживания",
            "Точка отсчёта",
            "Deadline"
        ])
        self.note_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.note_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Сортировка через заголовки
        self.note_table.setSortingEnabled(True)

        header = self.note_table.horizontalHeader()
        header.setSectionResizeMode(3, header.ResizeMode.Stretch)
        VLayout.addWidget(self.note_table)

        btn_layout = QHBoxLayout()
        btn_Vlayout = QVBoxLayout()
        self.done_btn = QPushButton("✅ Миссия выполнена")
        self.delete_btn = QPushButton("🗑 Аннигилировать")
        self.read_btn = QCommandLinkButton("💭 Вспомнить суть вопроса")
        self.done_btn.clicked.connect(self.mark_done)
        self.delete_btn.clicked.connect(self.remove_note)
        self.read_btn.clicked.connect(self.open_detailed_read_window)

        btn_Vlayout.addWidget(self.read_btn)
        btn_layout.addWidget(self.done_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_Vlayout.addLayout(btn_layout)
        VLayout.addLayout(btn_Vlayout)

        self.update_button_states()
        self.note_table.itemSelectionChanged.connect(self.update_button_states)

    def load_styles(self):
        """Загружает QSS-стили из файла styles.qss"""    
        # Добавляем подпапку styles
        style_file_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.qss')

        print(f"Попытка загрузить стили из: {style_file_path}") # Отладочный вывод

        try:
            with open(style_file_path, 'r', encoding='utf-8') as file:
                stylesheet = file.read()
                print(f"Содержимое файла (первые 100 символов): {stylesheet[:100]}...") # Отладочный вывод
                print(f"Длина содержимого файла: {len(stylesheet)}") # Отладочный вывод
                self.setStyleSheet(stylesheet)
                print("Стили успешно загружены и применены.") # Отладочный вывод
        except FileNotFoundError:
            print(f"Предупреждение: Файл стилей '{style_file_path}' не найден. Стили не будут применены.")
        except Exception as e:
            print(f"Ошибка при загрузке стилей: {e}")


    def update_button_states(self):
        selected = bool(self.note_table.selectedItems())
        self.done_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)

    def load_notes(self):
        """Загружает заметки в QTableWidget"""
        self.note_table.setRowCount(0)
        for note in self.todo.notes:
            row = self.note_table.rowCount()
            self.note_table.insertRow(row)

            title_note = QTableWidgetItem(note.get("Название", ""))

            status_val = note.get("Статус", False) # Получаем булевое значение
            status = "✅ Выполнено" if status_val else "⏳ В процессе"
            status_note = QTableWidgetItem(status)
            status_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            date_note = QTableWidgetItem(note.get("Время", ""))
            deadline = note.get("Deadline", "Срок не определён")            
            deadline_note = DeadlineTableWidgetItem(deadline, status_val)            
            deadline_note.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.note_table.setItem(row, 0, title_note)
            self.note_table.setItem(row, 1, status_note)
            self.note_table.setItem(row, 2, date_note)
            self.note_table.setItem(row, 3, deadline_note)

    def add_note(self):
        """Добавляет заметку в список задач"""
        text = self.note_input.text().strip()
        date = self.date_edit.date().toString("dd.MM.yyyy")
        if not text:
            QMessageBox.warning(self, "Ошибка!", "Введите заметку!")
            return
        self.todo.create(text, date)
        self.note_input.clear()
        self.load_notes()

    def get_selected_row(self):
        """Возвращает выбранную заметку"""
        selected = self.note_table.selectionModel().selectedRows()
        return selected[0].row() if selected else None

    def mark_done(self):
        """Отмечает задачу как выполненную, перезаписывает файл"""
        row = self.get_selected_row()
        if row is not None:
            # update ожидает номер с 1, а row - индекс с 0
            self.todo.update(row + 1)            
            # Найдём элемент статуса и дедлайна в строке row
            status_item = self.note_table.item(row, 1)
            deadline_item = self.note_table.item(row, 3)
            if status_item and deadline_item and isinstance(deadline_item, DeadlineTableWidgetItem):
                # Обновим текст статуса
                status_item.setText("✅ Выполнено")
                # Обновим статус в DeadlineTableWidgetItem, чтобы он знал, что теперь выполнено
                deadline_item.set_status(True) 

    def remove_note(self):
        """Удаляет заметку и перезаписывает файл"""
        row = self.get_selected_row()
        if row is None:
            return
        if 0 <= row < len(self.todo.notes):
            removed = self.todo.notes.pop(row)
            self.todo.save()
            QMessageBox.information(
                self, "Аннигилировано!",
                f"Задача '{removed['Название']}' удалена."
            )
            self.load_notes()
        else:
            QMessageBox.warning(self, "Ошибка", "Задача не найдена.")

    def open_detailed_note_window(self):
        """Открывает окно для записи подробностей заметки"""
        note_text = self.note_input.text().strip()
        if not note_text:
            QMessageBox.warning(self, "Предупреждение", "Введите название заметки!")
            return
        dialog = DetailedNoteWindow(note_text, self)
        if dialog.exec() == QDialog.DialogCode.Accepted: # Исправлено для PyQt6
            detailed_text = dialog.get_detailed_text()
            date = self.date_edit.date().toString("dd.MM.yyyy")
            self.todo.create(note_text, date, detailed_text)
            self.note_input.clear()
            self.load_notes()

    def open_detailed_read_window(self):
        selected = self.get_selected_row()
        if selected is None:
            QMessageBox.warning(self, "Ошибка", "Выберите заметку для просмотра.")
            return
        note = self.todo.notes[selected]
        details = note.get("Детали", "")
        title = note.get("Название", "")
        dialog = DetailedReadWindow(title, details, self, note_number=selected + 1)
        dialog.exec()
