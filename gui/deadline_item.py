from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from datetime import datetime, timedelta

class DeadlineTableWidgetItem(QTableWidgetItem):
    """Кастомный элемент таблицы для дедлайна с автоматическим закрашиванием и корректной сортировкой."""

    def __init__(self, text: str, status: bool = False): # Добавлен аргумент status
        super().__init__(text)
        self.status = status # Сохраняем статус
        self._update_background(text, status)
        # Сохраняем дату для сортировки
        self._sort_date = self._parse_date(text)

    def setData(self, role, value):
        """Переопределяем setData, чтобы обновлять фон и дату для сортировки при изменении текста."""
        super().setData(role, value)
        if role == Qt.ItemDataRole.EditRole or role == Qt.ItemDataRole.DisplayRole:
            self._update_background(value, self.status) # Передаём текущий статус
            self._sort_date = self._parse_date(value) # Обновляем дату для сортировки

    def set_status(self, status: bool):
        """Метод для обновления статуса и фона."""
        self.status = status
        # Обновляем фон на основе текущего текста и нового статуса
        self._update_background(self.text(), status)

    def _parse_date(self, deadline_str: str):
        """Парсит строку даты и возвращает объект date или None."""
        if not deadline_str or deadline_str == "Срок не определён":
            return None
        try:
            return datetime.strptime(deadline_str, "%d.%m.%Y").date()
        except ValueError:
            print(f"Предупреждение: Неверный формат даты дедлайна: {deadline_str}")
            return None

    def _update_background(self, deadline_str: str, status: bool):
        """Обновляет фон в зависимости от даты дедлайна и статуса."""
        # Сброс фона
        self.setBackground(QBrush()) # Сбрасываем на стандартный

        # Если статус "Выполнено", всегда зелёный
        if status:
            self.setBackground(QBrush(QColor(60, 179, 113))) # Светло-зелёный
            return # Выходим, если выполнено

        # Если дедлайн не определён, оставляем без фона (или можно поставить серый)
        if not deadline_str or deadline_str == "Срок не определён":
            return # Фон уже сброшен

        try:
            # Предполагаем формат даты "dd.MM.yyyy" как в QDateEdit
            deadline_date = datetime.strptime(deadline_str, "%d.%m.%Y").date()
            today = datetime.now().date()
            days_until_deadline = (deadline_date - today).days

            if days_until_deadline <= 0:
                # Красный: дедлайн сегодня или просрочен
                self.setBackground(QBrush(QColor(255, 100, 100))) # Светло-красный
            elif days_until_deadline <= 2:
                # Желтый: дедлайн в ближайшие 1-2 дня
                self.setBackground(QBrush(QColor(255, 255, 150))) # Светло-желтый
        except ValueError:
            # Если формат даты неверен, оставляем без фона
            print(f"Предупреждение: Неверный формат даты дедлайна: {deadline_str}")
            pass

    def __lt__(self, other):
        """Метод для корректной сортировки по дате."""
        # Получаем даты для сортировки
        date1 = self._sort_date
        date2 = other._sort_date

        # Если обе даты None, сортируем по строке
        if date1 is None and date2 is None:
            return self.text() < other.text()

        # Если первая дата None, она должна быть "больше" (после всех дат)
        # Значит, self НЕ меньше other -> False
        if date1 is None:
            return False

        # Если вторая дата None, она должна быть "больше"
        # Значит, self меньше other -> True
        if date2 is None:
            return True

        # Сравниваем даты
        return date1 < date2