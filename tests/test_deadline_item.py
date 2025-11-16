import unittest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta
from gui.deadline_item import DeadlineTableWidgetItem


class TestDeadlineTableWidgetItem(unittest.TestCase):
    """Тесты для DeadlineTableWidgetItem."""

    @classmethod
    def setUpClass(cls):
        """Инициализирует QApplication один раз для всех тестов."""
        cls.app = QApplication([]) # Создаём QApplication для тестов

    def test_init_with_valid_date(self):
        """Проверяет создание элемента с корректной датой."""
        text = "01.01.2030"
        item = DeadlineTableWidgetItem(text)
        self.assertEqual(item.text(), text)
        self.assertIsNotNone(item._sort_date)
        self.assertEqual(item._sort_date, datetime.strptime(text, "%d.%m.%Y").date())

    def test_init_with_undefined(self):
        """Проверяет создание элемента с 'Срок не определён'."""
        text = "Срок не определён"
        item = DeadlineTableWidgetItem(text)
        self.assertEqual(item.text(), text)
        self.assertIsNone(item._sort_date)

    def test_init_with_invalid_date(self):
        """Проверяет создание элемента с неверной датой."""
        text = "invalid_date"
        item = DeadlineTableWidgetItem(text)
        self.assertEqual(item.text(), text)
        self.assertIsNone(item._sort_date)

    def test_setData_updates_text_and_sort_date(self):
        """Проверяет, что setData обновляет текст и _sort_date."""
        item = DeadlineTableWidgetItem("01.01.2030")
        new_text = "02.02.2031"
        item.setData(Qt.ItemDataRole.EditRole, new_text)
        self.assertEqual(item.text(), new_text)
        self.assertIsNotNone(item._sort_date)
        self.assertEqual(item._sort_date, datetime.strptime(new_text, "%d.%m.%Y").date())

    def test_setData_with_undefined(self):
        """Проверяет, что setData корректно обрабатывает 'Срок не определён'."""
        item = DeadlineTableWidgetItem("01.01.2030")
        new_text = "Срок не определён"
        item.setData(Qt.ItemDataRole.EditRole, new_text)
        self.assertEqual(item.text(), new_text)
        self.assertIsNone(item._sort_date)

    def test_lt_both_dates_valid(self):
        """Проверяет сравнение (__lt__) для двух валидных дат."""
        item1 = DeadlineTableWidgetItem("01.01.2030")
        item2 = DeadlineTableWidgetItem("02.02.2031")
        # item1 (01.01.2030) < item2 (02.02.2031) -> True
        self.assertTrue(item1 < item2)
        # item2 (02.02.2031) < item1 (01.01.2030) -> False
        self.assertFalse(item2 < item1)

    def test_lt_one_date_none(self):
        """Проверяет сравнение (__lt__), когда одна дата None."""
        item1 = DeadlineTableWidgetItem("01.01.2030")
        item2 = DeadlineTableWidgetItem("Срок не определён")
        # item1 (с датой) < item2 (без даты) -> False (item2 "больше")
        self.assertFalse(item1 < item2)
        # item2 (без даты) < item1 (с датой) -> True (item2 "больше", значит item1 < item2 = False)
        # Нет, item2 > item1, значит item1 < item2 = False. item2 < item1 = True.
        self.assertTrue(item2 < item1) # item2 (None) > item1 (date), значит item1 < item2 = False. item2 < item1 = True.

    def test_lt_both_dates_none(self):
        """Проверяет сравнение (__lt__), когда обе даты None."""
        item1 = DeadlineTableWidgetItem("Срок не определён")
        item2 = DeadlineTableWidgetItem("Срок не определён")
        # При равных датах (обе None), сортировка по строке
        # item1.text() < item2.text() -> "Срок не определён" < "Срок не определён" -> False
        self.assertFalse(item1 < item2)
        # Но если строки разные, будет сравнение строк
        item3 = DeadlineTableWidgetItem("Срок не определён")
        item4 = DeadlineTableWidgetItem("Другой текст")
        # "Срок не определён" < "Другой текст" -> True
        self.assertTrue(item3 < item4)


if __name__ == '__main__':
    unittest.main()