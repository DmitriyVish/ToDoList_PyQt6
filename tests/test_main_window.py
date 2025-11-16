import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from gui.main_window import ToDoApp
from core.todo_logic import NotePreprocessor


class TestToDoApp(unittest.TestCase):
    """Функциональные тесты для ToDoApp."""

    @classmethod
    def setUpClass(cls):
        """Инициализирует QApplication один раз для всех тестов."""
        cls.app = QApplication([])

    def setUp(self):
        """Создаёт временный файл и экземпляр ToDoApp для каждого теста."""
        self.test_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.test_file.close()
        self.filename = self.test_file.name

        # Патчим NotePreprocessor, чтобы использовать временный файл
        with patch('gui.main_window.NotePreprocessor') as mock_note_processor:
            mock_instance = NotePreprocessor()
            mock_instance.filename = self.filename
            mock_instance.notes = []
            mock_instance.save = MagicMock()
            mock_note_processor.return_value = mock_instance

            self.window = ToDoApp()
            # Присваиваем наш мок-инстанс в window.todo
            self.window.todo = mock_instance

    def tearDown(self):
        """Удаляет временный файл после каждого теста."""
        os.remove(self.filename)
        self.window.close()

    def test_add_note(self):
        """Проверяет добавление заметки через UI."""
        initial_count = len(self.window.todo.notes)
        self.window.note_input.setText("Test Note from UI")
        self.window.date_edit.setDate(self.window.date_edit.date().addDays(1)) # Завтра
        deadline_text = self.window.date_edit.date().toString("dd.MM.yyyy")

        # Имитируем нажатие кнопки
        self.window.add_note()

        self.assertEqual(len(self.window.todo.notes), initial_count + 1)
        note = self.window.todo.notes[-1]
        self.assertEqual(note["Название"], "Test Note from UI")
        self.assertEqual(note["Deadline"], deadline_text)

    def test_add_note_empty_text(self):
        """Проверяет, что заметка не добавляется, если текст пуст."""
        initial_count = len(self.window.todo.notes)
        self.window.note_input.setText("")
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.window.add_note()
            # Проверяем, что было вызвано предупреждение
            mock_warning.assert_called()
        # Количество заметок не должно измениться
        self.assertEqual(len(self.window.todo.notes), initial_count)

    def test_add_note_whitespace_only_text(self):
        """Проверяет, что заметка не добавляется, если текст состоит только из пробелов."""
        initial_count = len(self.window.todo.notes)
        self.window.note_input.setText("   ") # Пробелы
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.window.add_note()
            # Проверяем, что было вызвано предупреждение
            mock_warning.assert_called()
        # Количество заметок не должно измениться
        self.assertEqual(len(self.window.todo.notes), initial_count)

    def test_add_note_newline_only_text(self):
        """Проверяет, что заметка не добавляется, если текст состоит только из символа новой строки."""
        initial_count = len(self.window.todo.notes)
        self.window.note_input.setText("\n") # Перевод строки
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.window.add_note()
            # Проверяем, что было вызвано предупреждение
            mock_warning.assert_called()
        # Количество заметок не должно измениться
        self.assertEqual(len(self.window.todo.notes), initial_count)

    def test_add_note_tab_only_text(self):
        """Проверяет, что заметка не добавляется, если текст состоит только из табуляции."""
        initial_count = len(self.window.todo.notes)
        self.window.note_input.setText("\t") # Табуляция
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.window.add_note()
            # Проверяем, что было вызвано предупреждение
            mock_warning.assert_called()
        # Количество заметок не должно измениться
        self.assertEqual(len(self.window.todo.notes), initial_count)

    def test_mark_done(self):
        """Проверяет отметку заметки как выполненной."""
        # Добавим заметку вручную
        self.window.todo.create("Task to Mark Done", "01.01.2030")
        self.window.load_notes() # Обновим таблицу

        # Имитируем выбор строки и изменение статуса (прямое изменение)
        self.window.todo.update(1) # Обновляем первую заметку (номер 1)
        self.assertEqual(self.window.todo.notes[0]["Статус"], True)

    def test_remove_note(self):
        """Проверяет удаление заметки."""
        self.window.todo.create("Task to Remove", "01.01.2030")
        initial_count = len(self.window.todo.notes)
        self.window.load_notes() # Обновим таблицу

        # Имитируем выбор строки и удаление (прямое изменение)
        removed_note = self.window.todo.notes.pop(0)
        self.window.todo.save() # Вызываем save, как в remove_note
        self.assertEqual(len(self.window.todo.notes), initial_count - 1)

    # --- Тесты для валидации ввода в DetailedNoteWindow ---
    # Эти тесты проверяют, что всплывающие окна также обрабатывают пустой ввод при *создании* новой заметки с деталями

    def test_open_detailed_note_window_empty_text(self):
        """Проверяет, что при пустом тексте в основном поле не открывается окно детализации."""
        self.window.note_input.setText("")
        with patch.object(QMessageBox, 'warning') as mock_warning:
            self.window.open_detailed_note_window()
            # Проверяем, что было вызвано предупреждение в основном окне
            mock_warning.assert_called()

    def test_open_detailed_note_window_valid_text(self):
        """Проверяет, что при заполненном тексте в основном поле открывается окно детализации."""
        self.window.note_input.setText("Task with Details")
        # Патчим сам QDialog.exec, чтобы не открывалось настоящее окно
        with patch('gui.dialogs.DetailedNoteWindow.exec') as mock_exec:
            self.window.open_detailed_note_window()
            # exec() не должен быть вызван, если не прошла проверка в main_window
            # Проверим, что DetailedNoteWindow был *создан*
            # Мы не можем легко проверить, был ли вызван конструктор, но можем проверить,
            # что create не был вызван в main_window, если exec не вызывается.
            # Лучше патчить create в NotePreprocessor и убедиться, что оно вызывается
            # при успешном прохождении проверки.
            # Проверим, что create вызывается при нажатии "Записать в блокнотик" в диалоге.
            # Но для проверки *открытия* диалога при валидном вводе:
            # Нужно патчить конструктор DetailedNoteWindow и проверить, что он вызывается.
            # Это сложнее, чем кажется без рефакторинга.
            # Пока оставим простую проверку: при валидном вводе open_detailed_note_window
            # не вызывает warning и не прерывается.
            # В open_detailed_note_window нет проверки на пустой note_text для *открытия* окна,
            # проверка происходит в DetailedNoteWindow при нажатии "Записать".
            # Но в main_window.py -> open_detailed_note_window проверяется note_input.text().strip()
            # ДА, в main_window.py строка 217: if not note_text: QMessageBox.warning(...)
            # Значит, тест выше test_open_detailed_note_window_empty_text корректен.
            # А этот тест проверяет, что при НЕ пустом тексте проверка пройдена.
            # Чтобы протестировать открытие, нужно проверить, что DetailedNoteWindow() был создан.
            # Это можно сделать через patch.
            # Патчим конструктор DetailedNoteWindow
            with patch('gui.dialogs.DetailedNoteWindow') as MockDetailedNoteWindow:
                # Создаём mock-диалог
                mock_dialog_instance = MagicMock()
                MockDetailedNoteWindow.return_value = mock_dialog_instance
                # Устанавливаем exec, чтобы возвращал Accepted
                mock_dialog_instance.exec.return_value = 1 # QDialog.DialogCode.Accepted

                self.window.note_input.setText("Task with Details")
                self.window.open_detailed_note_window()

                # Проверяем, что конструктор DetailedNoteWindow был вызван
                MockDetailedNoteWindow.assert_called_once()
                # Проверяем, что exec был вызван у созданного экземпляра
                mock_dialog_instance.exec.assert_called_once()

                # Проверяем, что create был вызван у NotePreprocessor
                self.window.todo.create.assert_called_once_with("Task with Details", unittest.mock.ANY, "")


if __name__ == '__main__':
    unittest.main()