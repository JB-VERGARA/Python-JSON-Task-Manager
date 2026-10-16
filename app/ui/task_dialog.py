from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QPlainTextEdit,
    QTimeEdit,
    QDateEdit,
)
from PySide6.QtCore import QDate, QTime


class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None):
        super().__init__(parent)

        self.task = task

        if task:
            self.setWindowTitle("Edit Task")
        else:
            self.setWindowTitle("Add Task")

        self.setMinimumWidth(400)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Task title")

        self.description_input = QPlainTextEdit()
        self.description_input.setPlaceholderText("Optional description")
        self.description_input.setMaximumHeight(100)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)

        self.time_input = QTimeEdit()
        self.time_input.setDisplayFormat("hh:mm AP")

        self.priority_input = QComboBox()
        self.priority_input.addItems([
            "low",
            "medium",
            "high"
        ])

        # ==========================================
        # Default values
        # ==========================================

        if task:
            year, month, day = map(
                int,
                task.date.split("-")
            )

            self.date_input.setDate(
                QDate(year, month, day)
            )

            if task.time:
                hour, minute = map(
                    int,
                    task.time.split(":")
                )

                self.time_input.setTime(
                    QTime(hour, minute)
                )
            else:
                self.time_input.setTime(
                    QTime.currentTime()
                )

            self.title_input.setText(
                task.title
            )

            self.description_input.setPlainText(
                task.description
            )

            self.priority_input.setCurrentText(
                task.priority
            )

        else:
            self.date_input.setDate(
                QDate.currentDate()
            )

            self.time_input.setTime(
                QTime.currentTime()
            )

            self.priority_input.setCurrentText(
                "medium"
            )

        # ==========================================
        # Buttons
        # ==========================================

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout = QFormLayout()

        layout.addRow(
            "Title:",
            self.title_input
        )

        layout.addRow(
            "Description:",
            self.description_input
        )

        layout.addRow(
            "Date:",
            self.date_input
        )

        layout.addRow(
            "Time:",
            self.time_input
        )

        layout.addRow(
            "Priority:",
            self.priority_input
        )

        layout.addRow(buttons)

        self.setLayout(layout)

    def get_task_data(self):
        return {
            "title": self.title_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "time": self.time_input.time().toString("HH:mm"),
            "priority": self.priority_input.currentText(),
        }