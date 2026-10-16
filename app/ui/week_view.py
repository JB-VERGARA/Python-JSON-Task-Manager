from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class WeekView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)

            widget = item.widget()

            if widget:
                widget.deleteLater()

    def set_week(self, week_days, tasks):
        self.clear()

        for date in week_days:

            date_string = date.strftime("%Y-%m-%d")

            day_tasks = [
                task
                for task in tasks
                if task["date"] == date_string
            ]

            day_frame = QFrame()
            day_frame.setObjectName("weekDay")

            day_layout = QVBoxLayout(day_frame)

            day_layout.setContentsMargins(
                15,
                12,
                15,
                12
            )

            day_layout.setSpacing(5)

            day_title = QLabel(
                date.strftime("%A, %B %d")
            )

            day_title.setObjectName(
                "weekDayTitle"
            )

            day_layout.addWidget(
                day_title
            )

            if not day_tasks:

                empty = QLabel(
                    "No tasks"
                )

                empty.setObjectName(
                    "weekEmpty"
                )

                day_layout.addWidget(
                    empty
                )

            else:

                day_tasks.sort(
                    key=lambda task: task.get(
                        "time",
                        ""
                    )
                )

                for task in day_tasks:

                    task_label = QLabel()

                    time = task.get(
                        "time",
                        ""
                    )

                    title = task.get(
                        "title",
                        ""
                    )

                    priority = task.get(
                        "priority",
                        "medium"
                    )

                    if time:
                        text = (
                            f"{time}  •  "
                            f"{title}  "
                            f"({priority.capitalize()})"
                        )
                    else:
                        text = (
                            f"{title}  "
                            f"({priority.capitalize()})"
                        )

                    task_label.setText(
                        text
                    )

                    if task.get(
                        "completed",
                        False
                    ):
                        task_label.setStyleSheet(
                            "text-decoration: "
                            "line-through;"
                            "color: #9ca3af;"
                        )

                    day_layout.addWidget(
                        task_label
                    )

            self.layout.addWidget(
                day_frame
            )

        self.layout.addStretch()