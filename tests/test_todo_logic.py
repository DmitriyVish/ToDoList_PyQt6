import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from core.todo_logic import ToDoList, NotePreprocessor


class TestToDoList(unittest.TestCase):
    """Тесты для базового класса ToDoList."""

    def setUp(self):
        """Создаёт временный файл и экземпляр ToDoList для каждого теста."""
        self.test_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.test_file.close()
        self.filename = self.test_file.name
        self.todo_list = ToDoList(self.filename)

    def tearDown(self):
        """Удаляет временный файл после каждого теста."""
        os.remove(self.filename)

    def test_initialization_with_existing_file(self):
        """Проверяет, что список загружается из существующего файла."""
        sample_data = [{"name": "Test Note"}]
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f)

        todo_list = ToDoList(self.filename)
        self.assertEqual(todo_list.notes, sample_data)

    def test_initialization_with_nonexistent_file(self):
        """Проверяет, что создаётся пустой список, если файл не существует."""
        # Удаляем файл, созданный в setUp
        os.remove(self.filename)
        # Убедимся, что его больше нет
        self.assertFalse(os.path.exists(self.filename))

        todo_list = ToDoList(self.filename)
        self.assertEqual(todo_list.notes, [])

    def test_save(self):
        """Проверяет, что данные корректно сохраняются в файл."""
        test_note = {"name": "Saved Note"}
        self.todo_list.notes = [test_note]
        self.todo_list.save()

        with open(self.filename, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data, [test_note])

    def test_json_load_nonexistent(self):
        """Проверяет, что json_load возвращает пустой список, если файл не существует."""
        # Удаляем файл, созданный в setUp
        os.remove(self.filename)
        # Убедимся, что его больше нет
        self.assertFalse(os.path.exists(self.filename))

        result = self.todo_list.json_load()
        self.assertEqual(result, [])

    def test_json_load_empty_file(self):
        """Проверяет, что json_load возвращает пустой список, если файл пуст."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write('') # Создаём пустой файл

        result = self.todo_list.json_load()
        self.assertEqual(result, [])

    def test_json_load_invalid_json(self):
        """Проверяет, что json_load возвращает пустой список при ошибке чтения."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write('invalid json content')

        result = self.todo_list.json_load()
        self.assertEqual(result, [])

    def test_get_date_time(self):
        """Проверяет формат возвращаемой строки даты/времени."""
        result = self.todo_list.get_date_time()
        # Проверим, что результат содержит день недели, дату и время
        # Это не идеальная проверка формата, но лучше, чем ничего
        self.assertIn(" ", result) # Должно быть как минимум 2 части
        self.assertGreater(len(result), 10) # Должно быть достаточно длинной строкой


class TestNotePreprocessor(unittest.TestCase):
    """Тесты для класса NotePreprocessor."""

    def setUp(self):
        """Создаёт временный файл и экземпляр NotePreprocessor для каждого теста."""
        self.test_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.test_file.close()
        self.filename = self.test_file.name
        # Передаём имя файла в конструктор
        self.note_processor = NotePreprocessor()
        # Перезаписываем filename вручную, так как ToDoList.__init__ использует PATH по умолчанию
        # Чтобы тестировать с временным файлом, нужно создать ToDoList с нужным именем
        # Или переопределить поведение NotePreprocessor.__init__
        # Лучше всего изменить NotePreprocessor.__init__ или создать его вручную в тестах
        # Пока используем обходной путь: создадим ToDoList с нужным файлом, а потом NotePreprocessor
        # Правильнее будет изменить конструктор NotePreprocessor, чтобы он принимал filename
        # Но для текущей структуры:
        self.note_processor.filename = self.filename
        self.note_processor.notes = [] # Очищаем список перед тестом
        self.note_processor.save() # Создаём пустой файл

    def tearDown(self):
        """Удаляет временный файл после каждого теста."""
        os.remove(self.filename)

    def test_create(self):
        """Проверяет создание заметки."""
        initial_count = len(self.note_processor.notes)
        self.note_processor.create("Test Task", "01.01.2030", "Details here")
        self.assertEqual(len(self.note_processor.notes), initial_count + 1)
        note = self.note_processor.notes[-1] # Последняя заметка
        self.assertEqual(note["Название"], "Test Task")
        self.assertEqual(note["Статус"], False)
        self.assertEqual(note["Deadline"], "01.01.2030")
        self.assertEqual(note["Детали"], "Details here")
        self.assertIn("id", note)
        self.assertIn("Время", note)

    def test_create_empty_text(self):
        """Проверяет, что заметка не создаётся, если текст пуст."""
        initial_count = len(self.note_processor.notes)
        self.note_processor.create("", "01.01.2030", "Details here")
        self.assertEqual(len(self.note_processor.notes), initial_count)

    def test_update(self):
        """Проверяет обновление статуса заметки."""
        self.note_processor.create("Task 1", "01.01.2030")
        self.note_processor.create("Task 2", "02.01.2030")
        self.assertEqual(self.note_processor.notes[0]["Статус"], False)
        self.note_processor.update(1) # Обновляем первую заметку (номер 1)
        self.assertEqual(self.note_processor.notes[0]["Статус"], True)

    def test_update_nonexistent(self):
        """Проверяет, что обновление несуществующей заметки не вызывает ошибки."""
        # Пустой список
        self.note_processor.update(1)
        # Список с одной заметкой
        self.note_processor.create("Task 1", "01.01.2030")
        self.note_processor.update(2) # Попытка обновить вторую
        self.assertEqual(self.note_processor.notes[0]["Статус"], False) # Статус не изменился

    def test_update_note_content(self):
        """Проверяет обновление содержимого заметки."""
        self.note_processor.create("Task 1", "01.01.2030", "Old Details")
        self.note_processor.update_note_content(1, "New Details")
        self.assertEqual(self.note_processor.notes[0]["Детали"], "New Details")

    def test_update_note_content_nonexistent(self):
        """Проверяет, что обновление содержимого несуществующей заметки не вызывает ошибки."""
        # Пустой список
        self.note_processor.update_note_content(1, "New Details")
        # Список с одной заметкой
        self.note_processor.create("Task 1", "01.01.2030", "Old Details")
        self.note_processor.update_note_content(2, "New Details") # Попытка обновить вторую
        self.assertEqual(self.note_processor.notes[0]["Детали"], "Old Details") # Содержимое не изменилось

    def test_delete(self):
        """Проверяет удаление заметки."""
        self.note_processor.create("Task 1", "01.01.2030")
        self.note_processor.create("Task 2", "02.01.2030")
        initial_count = len(self.note_processor.notes)
        self.note_processor.delete(1) # Удаляем первую заметку (номер 1)
        self.assertEqual(len(self.note_processor.notes), initial_count - 1)
        self.assertEqual(self.note_processor.notes[0]["Название"], "Task 2")

    def test_delete_nonexistent(self):
        """Проверяет, что удаление несуществующей заметки не вызывает ошибки."""
        # Пустой список
        self.note_processor.delete(1)
        # Список с одной заметкой
        self.note_processor.create("Task 1", "01.01.2030")
        initial_count = len(self.note_processor.notes)
        self.note_processor.delete(2) # Попытка удалить вторую
        self.assertEqual(len(self.note_processor.notes), initial_count) # Количество не изменилось

    def test_find_note(self):
        """Проверяет поиск заметки по номеру."""
        self.note_processor.create("Task 1", "01.01.2030")
        self.note_processor.create("Task 2", "02.01.2030")
        note = self.note_processor.find_note(1, self.note_processor.notes)
        self.assertIsNotNone(note)
        self.assertEqual(note["Название"], "Task 1")

    def test_find_note_nonexistent(self):
        """Проверяет, что поиск несуществующей заметки возвращает None."""
        self.note_processor.create("Task 1", "01.01.2030")
        note = self.note_processor.find_note(2, self.note_processor.notes)
        self.assertIsNone(note)
        note = self.note_processor.find_note(0, self.note_processor.notes)
        self.assertIsNone(note)


if __name__ == '__main__':
    unittest.main()