from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter

from app.ui.calendar_view import CalendarView


class MonthView(CalendarView):
    """Full-page month calendar: bigger cells, grid, and task dots."""

    DOT_COLOR = QColor("#60a5fa")

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGridVisible(True)
        self.setMinimumSize(640, 420)

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)

        count = self.task_counts.get(date.toJulianDay(), 0)

        if not count:
            return

        dots = min(count, 3)
        radius = 3
        gap = 5
        total_width = dots * 2 * radius + (dots - 1) * gap

        start_x = rect.center().x() - total_width / 2 + radius
        y = rect.bottom() - 9

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.DOT_COLOR)

        for i in range(dots):
            painter.drawEllipse(
                QPointF(start_x + i * (2 * radius + gap), y),
                radius,
                radius,
            )

        painter.restore()