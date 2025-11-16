from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
                            QDialog, QVBoxLayout, QPushButton,
                            QTextEdit, QLabel, QHBoxLayout,
                            QCheckBox, QMessageBox)

class DetailedNoteWindow(QDialog):
    """Дополнительное окно приложения с детализацией заметки"""
    def __init__(self, note_title, parent=None):
        super().__init__(parent)
        self.note_title = note_title
        self.setWindowTitle(f"Подробности заметки {self.note_title}")
        self.resize(600, 500)
        # Используем стиль главного окна
        if parent:
            self.setStyleSheet(parent.styleSheet())

        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Запиши всё здесь...")

        layout.addWidget(self.text_edit)

        save_btn = QPushButton("📝 Записать в блокнотик")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def get_detailed_text(self):
        return self.text_edit.toPlainText()


class DetailedReadWindow(QDialog):
    """Окно для просмотра/редактирования содержания заметки"""
    def __init__(self, note_title, details, parent=None, note_number=None): # Заменён note_index на note_number
        super().__init__(parent)
        self.note_title = note_title
        self.details = details
        self.note_number = note_number # Сохраняем номер заметки (1-based)
        self.parent_window = parent # Сохраняем ссылку на родительское окно (ToDoApp)

        self.setWindowTitle(f"Чтение/Редактирование заметки: {self.note_title}")
        self.resize(600, 500)
        if parent:
            self.setStyleSheet(parent.styleSheet())

        layout = QVBoxLayout()

        # Заголовок
        title_label = QLabel(f"Заметка: {self.note_title}")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Текст заметки
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(self.details)
        self.text_edit.setReadOnly(True)  # По умолчанию только для чтения
        layout.addWidget(self.text_edit)

        # Кнопка закрытия
        btn_close = QPushButton("🏃‍♂️ Слишком сложно, До свидания!")
        chb_process = QCheckBox("✎ Редактировать")
        btn_update = QPushButton("🔥 Обновить миссию")

        # Логика редактирования
        def toggle_readonly():
            self.text_edit.setReadOnly(not chb_process.isChecked())
        chb_process.toggled.connect(toggle_readonly)

        btn_close.clicked.connect(self.accept)
        # Подключаем кнопку обновления к новому методу
        btn_update.clicked.connect(self.update_note)

        update_layout = QHBoxLayout()
        update_layout.addWidget(chb_process)
        update_layout.addStretch(1)
        update_layout.addWidget(btn_update)
        layout.addLayout(update_layout)
        layout.addWidget(btn_close)

        self.setLayout(layout)

    def update_note(self):
        """Обновляет содержание заметки."""
        if self.note_number is None or self.parent_window is None:
            # Если номер или родитель не задан, обновление невозможно
            QMessageBox.warning(self, "Ошибка", "Номер заметки или родительское окно не заданы.")
            return

        new_content = self.text_edit.toPlainText() # Получаем новый текст

        # Обновляем заметку в NotePreprocessor
        # Вызываем метод update_note_content у экземпляра NotePreprocessor из родителя
        # передаём номер (1-based) и новый контент
        try:
            # note_number - это номер (1-based), который ожидает update_note_content
            self.parent_window.todo.update_note_content(self.note_number, new_content)
            # QMessageBox.information(self, "Успех", f"Заметка {self.note_number} обновлена.")
            # Сообщение об успехе можно оставить, если нужно
            self.accept() # Закрываем диалог после обновления
        except AttributeError:
            print("Ошибка: В NotePreprocessor отсутствует метод update_note_content.")
            QMessageBox.critical(self, "Ошибка", "Внутренняя ошибка: метод обновления не найден.")
        except Exception as e:
            print(f"Ошибка при обновлении заметки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении: {e}")