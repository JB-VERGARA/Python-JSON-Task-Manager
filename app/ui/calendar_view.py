from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QFont, QPalette, QTextCharFormat
from PySide6.QtWidgets import QCalendarWidget, QSizePolicy


class CalendarView(QCalendarWidget):
    TASK_BG = QColor("#1e3a5f")
    TASK_FG = QColor("#ffffff")
    TODAY_FG = QColor("#60a5fa")
    WEEKEND_FG = QColor("#fca5a5")
    NORMAL_FG = QColor("#e5e7eb")

    def __init__(self, parent=None):
        super().__init__(parent)

        # Julian day -> number of tasks on that date
        self.task_counts = {}

        self.setGridVisible(False)
        self.setNavigationBarVisible(True)

        self.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        self.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.ShortDayNames
        )
        self.setFirstDayOfWeek(Qt.DayOfWeek.Monday)

        self.setMinimumSize(360, 270)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self._apply_palette()
        self._style_weekdays()
        self.setSelectedDate(QDate.currentDate())

    def _apply_palette(self):
        """The weekday header row is painted with the palette's
        AlternateBase colour (not a stylesheet background), so it must be
        set here or it shows up white."""
        palette = self.palette()

        palette.setColor(QPalette.ColorRole.Base, QColor("#10161e"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#151b23"))
        palette.setColor(QPalette.ColorRole.Window, QColor("#10161e"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#e5e7eb"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#e5e7eb"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#2563eb"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))

        # Days from the previous/next month
        palette.setColor(
            QPalette.ColorGroup.Disabled,
            QPalette.ColorRole.Text,
            QColor("#4b5563"),
        )

        self.setPalette(palette)

        header = QTextCharFormat()
        header.setForeground(QColor("#94a3b8"))
        header.setFontWeight(QFont.Weight.Bold)
        self.setHeaderTextFormat(header)

    def _style_weekdays(self):
        normal = QTextCharFormat()
        normal.setForeground(self.NORMAL_FG)

        weekend = QTextCharFormat()
        weekend.setForeground(self.WEEKEND_FG)

        for day in (
            Qt.DayOfWeek.Monday,
            Qt.DayOfWeek.Tuesday,
            Qt.DayOfWeek.Wednesday,
            Qt.DayOfWeek.Thursday,
            Qt.DayOfWeek.Friday,
        ):
            self.setWeekdayTextFormat(day, normal)

        self.setWeekdayTextFormat(Qt.DayOfWeek.Saturday, weekend)
        self.setWeekdayTextFormat(Qt.DayOfWeek.Sunday, weekend)

    def mark_task_dates(self, tasks):
        """Tint dates that have tasks and accent today's date."""

        # Clear existing per-date formatting
        self.setDateTextFormat(QDate(), QTextCharFormat())

        self.task_counts = {}
        dates = {}

        for task in tasks:
            try:
                year, month, day = map(int, task["date"].split("-"))
                date = QDate(year, month, day)
            except (ValueError, KeyError, AttributeError):
                continue

            if not date.isValid():
                continue

            key = date.toJulianDay()
            dates[key] = date
            self.task_counts[key] = self.task_counts.get(key, 0) + 1

        today = QDate.currentDate()
        dates[today.toJulianDay()] = today

        for key, date in dates.items():
            fmt = QTextCharFormat()
            fmt.setFontWeight(QFont.Weight.Bold)

            if key in self.task_counts:
                fmt.setBackground(self.TASK_BG)
                fmt.setForeground(self.TASK_FG)

            if date == today:
                fmt.setForeground(self.TODAY_FG)
                fmt.setFontUnderline(True)

            self.setDateTextFormat(date, fmt)

        self.updateCells()