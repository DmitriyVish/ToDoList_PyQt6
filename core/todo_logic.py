import os
import json
import uuid
from datetime import datetime

# Импортируем путь из конфига
from config import PATH

class ToDoList:
    def __init__(self, filename: str = PATH):
        self.filename = filename
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        self.notes = self.json_load()

    def save(self):
        """Метод сохраняет заметки в json-файл"""
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.notes, file, ensure_ascii=False, indent=4)
        print(f"Заметки сохранены. Количество заметок: {len(self.notes)}")

    def json_load(self):
        """Метод читает файл и загружает заметки в список"""
        notes = []
        if not os.path.exists(self.filename):
            print(f"Файл с именем {self.filename} не найден!")
            return []
        if os.path.getsize(self.filename) == 0:
            print("Файл не содержит записей")
            return []
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                notes = json.load(file)
                return notes
        except (OSError, json.JSONDecodeError):
            print("Ошибка чтения файла")
            return []

    @staticmethod
    def get_month(month: int) -> str:
        months = ["Января", "Февраля", "Марта", "Апреля", "Мая", "Июня",
                  "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
        return months[month - 1]

    @staticmethod
    def get_day_of_week(day: int) -> str:
        days = ["Понедельник", "Вторник", "Среда",
                "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[day]

    def get_date_time(self):
        """Метод возвращает строку с текущим днем недели, датой и временем"""
        now = datetime.now()
        date = f"{now.day} {self.get_month(now.month)} {now.year}"
        time = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"
        weekday = self.get_day_of_week(now.weekday())
        return f"{weekday} {date} {time}"


class NotePreprocessor(ToDoList):
    """Класс наследуется от ToDoList. Управляет созданием и изменением заметок."""
    def __init__(self):
        super().__init__()
        self.done = False
        self.time = self.get_date_time()
        self.note_text = ""
        self.note = {}

    def create(self, note_text: str, deadline: str, details: str = ""):
        """Метод создает заметку в виде словаря"""
        if not note_text.strip():
            print("Заметка пустая")
            return
        new_note = {
            "id": str(uuid.uuid4()),
            "Название": note_text.strip(),
            "Статус": False,
            "Время": self.get_date_time(),
            "Deadline": deadline,
            "Детали": details
        }
        self.notes.append(new_note)
        self.note = new_note
        self.save()

    def update(self, number: int):
        """Заменяет статус задачи на True"""
        if not self.notes:
            print("Нет сохранённых заметок")
            return None
        note = self.find_note(number, self.notes)
        if note and not note["Статус"]:
            note["Статус"] = True
            print("Статус заметки изменен")
            self.save()
            return 0
        
    def update_note_content(self, number: int, new_details: str):
        """
        Обновляет поле 'Детали' заметки по её номеру (1-based).
        """
        if not self.notes:
            print("Нет сохранённых заметок для обновления содержимого.")
            return None

        note = self.find_note(number, self.notes) # find_note ожидает номер (1-based)
        if note:
            note["Детали"] = new_details
            print(f"Содержимое заметки {number} обновлено.")
            self.save() # Сохраняем изменения
            return 0
        else:
            print(f"Заметка с номером {number} не найдена для обновления содержимого.")
            return None

    def read(self):
        """Метод печатает список задач"""
        notes = self.json_load()
        if not notes:
            print("Нет сохраненных заметок")
        for index, note in enumerate(notes):
            print("="*20, f"Заметка № {index + 1}", "="*40)
            for key, value in note.items():
                if key != "id":
                    print(f"{key}: {value}")
            print("="*73)

    def find_note(self, number: int, notes: list):
        """Метод ищет заметку по номеру"""
        try:
            assert isinstance(number, int)
        except AssertionError:
            print("Введите целое число")
            return None
        if 1 <= number <= len(notes):
            return notes[number - 1]
        else:
            print("Заметка с таким номером не найдена")
            return None

    def delete(self, number: int):
        """Удаляет заметку по номеру"""
        if not isinstance(number, int):
            print("Номер заметки должен быть целым числом.")
            return
        if 1 <= number <= len(self.notes):
            removed_note = self.notes.pop(number - 1)
            self.save()
            print(f"Заметка '{removed_note['Название']}' удалена.")
        else:
            print(f"Заметка с номером {number} не найдена.")