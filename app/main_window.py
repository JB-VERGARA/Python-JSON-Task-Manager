import json
from datetime import datetime, timedelta

from PySide6.QtCore import QDate, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.models.task import Task
from app.storage import load_data, save_data, validate_data
from app.ui.calendar_view import CalendarView
from app.ui.month_view import MonthView
from app.ui.task_dialog import TaskDialog
from app.ui.week_view import WeekView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bryan To Do List")
        self.setMinimumSize(1000, 680)
        self.resize(1280, 800)

        self.data = load_data()
        self.selected_date = datetime.now().date()

        # "today", "week", "month" or "settings"
        self.current_view = "today"
        self.previous_view = "today"

        self.build_ui()
        self.show_view("today")

    # ==========================================
    # UI construction
    # ==========================================

    def build_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------- Sidebar ----------
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 25, 12, 20)
        sidebar_layout.setSpacing(10)

        logo = QLabel("📝 To Do List")
        logo.setObjectName("logo")
        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(25)

        self.today_button = QPushButton("☀  Today")
        self.week_button = QPushButton("📆  Week")
        self.month_button = QPushButton("🗓  Month")
        self.settings_button = QPushButton("⚙  Settings")

        self.nav_buttons = {
            "today": self.today_button,
            "week": self.week_button,
            "month": self.month_button,
            "settings": self.settings_button,
        }

        for button in self.nav_buttons.values():
            button.setObjectName("navButton")

        sidebar_layout.addWidget(self.today_button)
        sidebar_layout.addWidget(self.week_button)
        sidebar_layout.addWidget(self.month_button)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(self.settings_button)

        self.today_button.clicked.connect(self.go_to_today)
        self.week_button.clicked.connect(lambda: self.show_view("week"))
        self.month_button.clicked.connect(lambda: self.show_view("month"))
        self.settings_button.clicked.connect(self.toggle_settings)

        # ---------- Content ----------
        content = QWidget()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        self.page_title = QLabel()
        self.page_title.setObjectName("pageTitle")
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()

        import_button = QPushButton("📥 Import")
        export_button = QPushButton("📤 Export")
        import_button.setObjectName("headerButton")
        export_button.setObjectName("headerButton")
        import_button.clicked.connect(self.import_data)
        export_button.clicked.connect(self.export_data)

        header_layout.addWidget(import_button)
        header_layout.addWidget(export_button)
        content_layout.addLayout(header_layout)

        self.date_label = QLabel()
        self.date_label.setObjectName("dateLabel")
        content_layout.addWidget(self.date_label)

        # Settings page
        self.settings_frame = self.build_settings_frame()
        content_layout.addWidget(self.settings_frame, 1)

        # Today page: calendar on the left, tasks on the right
        self.today_page = QWidget()
        today_layout = QHBoxLayout(self.today_page)
        today_layout.setContentsMargins(0, 0, 0, 0)
        today_layout.setSpacing(16)

        self.calendar_frame = QFrame()
        self.calendar_frame.setObjectName("calendarFrame")
        self.calendar_frame.setFixedWidth(440)

        calendar_layout = QVBoxLayout(self.calendar_frame)
        calendar_layout.setContentsMargins(12, 12, 12, 12)

        self.calendar = CalendarView()
        self.calendar.clicked.connect(self.date_selected)
        calendar_layout.addWidget(self.calendar)

        self.task_frame = QFrame()
        self.task_frame.setObjectName("taskFrame")

        self.task_layout = QVBoxLayout(self.task_frame)
        self.task_layout.setContentsMargins(20, 18, 20, 18)
        self.task_layout.setSpacing(12)

        self.task_title = QLabel()
        self.task_title.setObjectName("sectionTitle")
        self.task_layout.addWidget(self.task_title)

        # Scrollable task list so many tasks never overlap other widgets
        self.task_scroll = QScrollArea()
        self.task_scroll.setObjectName("taskScroll")
        self.task_scroll.setWidgetResizable(True)
        self.task_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.task_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        task_list = QWidget()
        task_list.setObjectName("taskList")

        self.task_container = QVBoxLayout(task_list)
        self.task_container.setContentsMargins(0, 0, 8, 0)
        self.task_container.setSpacing(8)

        self.task_scroll.setWidget(task_list)
        self.task_layout.addWidget(self.task_scroll, 1)

        today_layout.addWidget(self.calendar_frame)
        today_layout.addWidget(self.task_frame, 1)

        content_layout.addWidget(self.today_page, 1)

        # Month view
        self.month_view = MonthView()
        self.month_view.setObjectName("monthView")
        self.month_view.clicked.connect(self.month_date_selected)
        content_layout.addWidget(self.month_view, 1)

        # Week navigation
        self.week_navigation_widget = QWidget()
        week_navigation = QHBoxLayout(self.week_navigation_widget)
        week_navigation.setContentsMargins(0, 0, 0, 0)

        self.previous_week_button = QPushButton("← Previous Week")
        self.week_today_button = QPushButton("Today")
        self.next_week_button = QPushButton("Next Week →")

        week_navigation.addWidget(self.previous_week_button)
        week_navigation.addStretch()
        week_navigation.addWidget(self.week_today_button)
        week_navigation.addStretch()
        week_navigation.addWidget(self.next_week_button)

        self.previous_week_button.clicked.connect(self.previous_week)
        self.week_today_button.clicked.connect(self.week_today)
        self.next_week_button.clicked.connect(self.next_week)

        content_layout.addWidget(self.week_navigation_widget)

        # Week view
        self.week_view = WeekView()
        self.week_view.setObjectName("weekView")
        content_layout.addWidget(self.week_view, 1)

        # Add task button
        self.add_task_button = QPushButton("＋  Add Task")
        self.add_task_button.setObjectName("addTaskButton")
        self.add_task_button.setMinimumHeight(50)
        self.add_task_button.clicked.connect(self.add_task)
        content_layout.addWidget(self.add_task_button)

        # ---------- Assemble ----------
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)
        self.setCentralWidget(central_widget)

        self.apply_styles()

    def build_settings_frame(self):
        frame = QFrame()
        frame.setObjectName("settingsFrame")

        layout = QVBoxLayout(frame)

        title = QLabel("Settings")
        title.setObjectName("settingsTitle")
        layout.addWidget(title)

        info = QLabel(
            "Bryan To Do List stores your data locally on this computer."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        data_location = QLabel("Data file:\ndata/tasks.json")
        data_location.setObjectName("settingsInfo")
        layout.addWidget(data_location)

        backup_location = QLabel("Automatic backups:\ndata/backups/")
        backup_location.setObjectName("settingsInfo")
        layout.addWidget(backup_location)

        open_data_button = QPushButton("📁 Open Data Folder")
        open_backup_button = QPushButton("💾 Open Backup Folder")
        open_data_button.clicked.connect(self.open_data_folder)
        open_backup_button.clicked.connect(self.open_backup_folder)

        layout.addWidget(open_data_button)
        layout.addWidget(open_backup_button)
        layout.addStretch()

        return frame

    # ==========================================
    # View management
    # ==========================================

    def show_view(self, view):
        """Show exactly one page and update the header + sidebar."""
        self.current_view = view

        is_today = view == "today"
        is_week = view == "week"
        is_month = view == "month"
        is_settings = view == "settings"

        self.today_page.setVisible(is_today)

        self.week_view.setVisible(is_week)
        self.week_navigation_widget.setVisible(is_week)

        self.month_view.setVisible(is_month)
        self.settings_frame.setVisible(is_settings)

        self.add_task_button.setVisible(not is_settings)
        self.date_label.setVisible(True)

        for name, button in self.nav_buttons.items():
            button.setProperty("active", name == view)
            button.style().unpolish(button)
            button.style().polish(button)

        self.refresh_all()

    def toggle_settings(self):
        if self.current_view == "settings":
            self.show_view(self.previous_view)
        else:
            self.previous_view = self.current_view
            self.show_view("settings")

    def go_to_today(self):
        self.selected_date = datetime.now().date()
        self.show_view("today")

    def refresh_all(self):
        """Refresh every view so they never show stale data."""
        self.refresh_tasks()
        self.update_calendar()
        self.update_week_view()
        self.update_month_view()
        self.update_header()

    def update_header(self):
        selected = self.selected_date

        if self.current_view == "today":
            self.page_title.setText(selected.strftime("%B %d, %Y"))
            self.date_label.setText(selected.strftime("%A"))
            self.task_title.setText(f"Tasks for {selected.strftime('%B %d')}")

        elif self.current_view == "week":
            self.page_title.setText("Week")
            self.date_label.setText(self.get_week_range_text())

        elif self.current_view == "month":
            self.page_title.setText("Month")
            self.date_label.setText(selected.strftime("%B %Y"))

        elif self.current_view == "settings":
            self.page_title.setText("Settings")
            self.date_label.setText("Application Settings")

    # ==========================================
    # Calendar / Week / Month
    # ==========================================

    def to_qdate(self, value):
        return QDate(value.year, value.month, value.day)

    def update_calendar(self):
        self.calendar.setSelectedDate(self.to_qdate(self.selected_date))
        self.calendar.mark_task_dates(self.data["tasks"])

    def date_selected(self, qdate):
        self.selected_date = qdate.toPython()
        self.refresh_tasks()
        self.update_header()

    def month_date_selected(self, qdate):
        """A day was clicked in the month view -> open it in Today view."""
        self.selected_date = qdate.toPython()
        self.show_view("today")

    def get_week_days(self):
        monday = self.selected_date - timedelta(
            days=self.selected_date.weekday()
        )
        return [monday + timedelta(days=i) for i in range(7)]

    def get_week_range_text(self):
        week_days = self.get_week_days()
        start = week_days[0]
        end = week_days[-1]
        return (
            f"{start.strftime('%B %d')} – "
            f"{end.strftime('%B %d, %Y')}"
        )

    def update_week_view(self):
        self.week_view.set_week(self.get_week_days(), self.data["tasks"])

    def update_month_view(self):
        self.month_view.setSelectedDate(self.to_qdate(self.selected_date))
        self.month_view.mark_task_dates(self.data["tasks"])

    def previous_week(self):
        self.selected_date -= timedelta(days=7)
        self.update_week_view()
        self.update_header()

    def next_week(self):
        self.selected_date += timedelta(days=7)
        self.update_week_view()
        self.update_header()

    def week_today(self):
        self.selected_date = datetime.now().date()
        self.update_week_view()
        self.update_header()

    # ==========================================
    # Tasks
    # ==========================================

    def add_task(self):
        dialog = TaskDialog(self)
        dialog.date_input.setDate(self.to_qdate(self.selected_date))

        if not dialog.exec():
            return

        task_data = dialog.get_task_data()

        if not task_data["title"]:
            QMessageBox.warning(
                self, "Missing Title", "Please enter a task title."
            )
            return

        task = Task.create(**task_data)
        self.data["tasks"].append(task.to_dict())

        save_data(self.data)
        self.refresh_all()

    def refresh_tasks(self):
        while self.task_container.count():
            item = self.task_container.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        selected_date = self.selected_date.strftime("%Y-%m-%d")

        tasks = [
            Task.from_dict(task)
            for task in self.data["tasks"]
            if task["date"] == selected_date
        ]

        tasks.sort(key=lambda task: task.time or "")

        if not tasks:
            empty_label = QLabel("No tasks for this day")
            empty_label.setObjectName("emptyLabel")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.task_container.addWidget(empty_label)
            self.task_container.addStretch()
            return

        for task in tasks:
            self.add_task_widget(task)

        self.task_container.addStretch()

    def add_task_widget(self, task):
        frame = QFrame()
        frame.setObjectName("taskItem")
        frame.setMinimumHeight(64)

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(14, 10, 12, 10)
        layout.setSpacing(12)

        checkbox = QCheckBox()
        checkbox.setChecked(task.completed)
        checkbox.stateChanged.connect(
            lambda state, task_id=task.id: self.toggle_task(task_id, state)
        )

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        title = QLabel(task.title)
        title.setObjectName("taskTitle")
        title.setWordWrap(True)

        if task.completed:
            title.setStyleSheet(
                "text-decoration: line-through; color: #9ca3af;"
            )

        detail_label = QLabel(task.time if task.time else "No time set")
        detail_label.setObjectName("taskDetails")

        info_layout.addWidget(title)
        info_layout.addWidget(detail_label)

        priority = (task.priority or "medium").lower()
        badge = QLabel(priority.capitalize())
        badge.setObjectName("priorityBadge")
        badge.setProperty("priority", priority)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setFixedHeight(22)

        edit_button = QPushButton("✏")
        edit_button.setObjectName("taskAction")
        edit_button.setFixedSize(36, 36)
        edit_button.clicked.connect(
            lambda checked=False, task_id=task.id: self.edit_task(task_id)
        )

        delete_button = QPushButton("🗑")
        delete_button.setObjectName("deleteAction")
        delete_button.setFixedSize(36, 36)
        delete_button.clicked.connect(
            lambda checked=False, task_id=task.id: self.delete_task(task_id)
        )

        layout.addWidget(checkbox, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addLayout(info_layout, 1)
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)

        self.task_container.addWidget(frame)

    def toggle_task(self, task_id, state):
        for task in self.data["tasks"]:
            if task["id"] == task_id:
                task["completed"] = state == Qt.CheckState.Checked.value
                task["updated_at"] = datetime.now().astimezone().isoformat()
                break

        save_data(self.data)
        self.refresh_all()

    def edit_task(self, task_id):
        task = None

        for task_data in self.data["tasks"]:
            if task_data["id"] == task_id:
                task = Task.from_dict(task_data)
                break

        if task is None:
            return

        dialog = TaskDialog(self, task)

        if not dialog.exec():
            return

        task_data = dialog.get_task_data()

        if not task_data["title"]:
            QMessageBox.warning(
                self, "Missing Title", "Please enter a task title."
            )
            return

        for existing_task in self.data["tasks"]:
            if existing_task["id"] == task_id:
                existing_task.update(task_data)
                existing_task["updated_at"] = (
                    datetime.now().astimezone().isoformat()
                )
                break

        save_data(self.data)
        self.refresh_all()

    def delete_task(self, task_id):
        result = QMessageBox.question(
            self,
            "Delete Task",
            "Are you sure you want to delete this task?",
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        self.data["tasks"] = [
            task for task in self.data["tasks"] if task["id"] != task_id
        ]

        save_data(self.data)
        self.refresh_all()

    # ==========================================
    # Import / Export
    # ==========================================

    def export_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Tasks",
            "bryan-to-do-list.json",
            "JSON Files (*.json)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4, ensure_ascii=False)

            QMessageBox.information(
                self,
                "Export Successful",
                "Your tasks were exported successfully.",
            )

        except OSError as error:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Could not export your tasks.\n\n{error}",
            )

    def import_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Tasks",
            "",
            "JSON Files (*.json)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                imported_data = json.load(file)

        except (json.JSONDecodeError, OSError) as error:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Could not read the selected file.\n\n{error}",
            )
            return

        if not validate_data(imported_data):
            QMessageBox.warning(
                self,
                "Invalid File",
                "This file is not a valid Bryan To Do List JSON file.",
            )
            return

        result = QMessageBox.question(
            self,
            "Import Tasks",
            "Importing this file will replace your current task data.\n\n"
            "Do you want to continue?",
        )

        if result != QMessageBox.StandardButton.Yes:
            return

        self.data = imported_data
        save_data(self.data)
        self.refresh_all()

        QMessageBox.information(
            self,
            "Import Successful",
            "Your tasks were imported successfully.",
        )

    # ==========================================
    # Settings helpers
    # ==========================================

    def open_data_folder(self):
        from app.storage import DATA_DIR

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(DATA_DIR)))

    def open_backup_folder(self):
        from app.storage import BACKUP_DIR

        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(BACKUP_DIR)))

    # ==========================================
    # Styling
    # ==========================================

    def apply_styles(self):
        self.setStyleSheet("""
            /* ===== GLOBAL ===== */

            QMainWindow {
                background-color: #0b0f14;
                color: #ffffff;
            }

            QWidget {
                font-family: "Segoe UI";
                font-size: 12px;
                color: #e5e7eb;
            }

            QFrame {
                border: none;
            }

            QLabel {
                color: #f9fafb;
            }

            /* ===== SIDEBAR ===== */

            QFrame#sidebar {
                background-color: #090d12;
                border-right: 1px solid #1c2430;
            }

            #logo {
                color: #f8fafc;
                font-size: 20px;
                font-weight: 800;
            }

            QPushButton#navButton {
                background-color: transparent;
                color: #9ca3af;
                text-align: left;
                border: none;
                border-radius: 6px;
                padding: 8px 10px;
                font-size: 12px;
            }

            QPushButton#navButton:hover {
                background-color: #151b23;
                color: #ffffff;
            }

            QPushButton#navButton[active="true"] {
                background-color: #1e293b;
                color: #ffffff;
                font-weight: bold;
            }

            /* ===== HEADER ===== */

            #content {
                background: #0b0f14;
            }

            QLabel#pageTitle {
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
            }

            QLabel#dateLabel {
                color: #6b7280;
                font-size: 11px;
            }

            /* ===== BUTTONS ===== */

            QPushButton {
                color: #cbd5e1;
                background: #111821;
                border: 1px solid #26313d;
                border-radius: 8px;
                padding: 8px 13px;
            }

            QPushButton:hover {
                background: #17212c;
                border-color: #344454;
                color: #f8fafc;
            }

            QPushButton:pressed {
                background: #0d141c;
            }

            /* ===== CARDS ===== */

            QFrame#calendarFrame,
            QFrame#taskFrame {
                background: #10161e;
                border: 1px solid #1d2935;
                border-radius: 12px;
            }

            #taskScroll,
            #taskScroll > QWidget > QWidget,
            #taskList {
                background: transparent;
                border: none;
            }

            /* ===== CALENDAR ===== */

            QCalendarWidget {
                background-color: #10161e;
                color: #e5e7eb;
                border: none;
            }

            QCalendarWidget QWidget {
                color: #e5e7eb;
            }

            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #10161e;
                min-height: 40px;
                max-height: 40px;
                border-bottom: 1px solid #1d2935;
            }

            QCalendarWidget QToolButton {
                background-color: transparent;
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 4px 10px;
                min-height: 28px;
            }

            QCalendarWidget QToolButton:hover {
                background-color: #1e293b;
            }

            QCalendarWidget QToolButton::menu-indicator {
                image: none;
            }

            QCalendarWidget QMenu {
                background-color: #151b23;
                color: #ffffff;
                border: 1px solid #26313d;
            }

            QCalendarWidget QMenu::item:selected {
                background-color: #2563eb;
            }

            QCalendarWidget QSpinBox {
                color: #ffffff;
                background-color: transparent;
                font-weight: bold;
                border: none;
                padding: 2px 6px;
            }

            QCalendarWidget QAbstractItemView {
                background-color: #10161e;
                alternate-background-color: #151b23;
                color: #e5e7eb;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                outline: none;
            }

            QCalendarWidget QAbstractItemView:disabled {
                color: #4b5563;
            }

            QCalendarWidget QHeaderView::section {
                background-color: #10161e;
                color: #94a3b8;
                font-size: 11px;
                font-weight: bold;
                border: none;
                padding: 6px;
            }

            /* ===== TASKS ===== */

            #sectionTitle {
                color: #f1f5f9;
                font-size: 17px;
                font-weight: 700;
            }

            #emptyLabel {
                color: #64748b;
                padding: 22px;
                font-size: 14px;
            }

            #taskItem {
                background: #0d141c;
                border: 1px solid #1e2a36;
                border-radius: 9px;
            }

            #taskItem:hover {
                background: #111a24;
                border-color: #2d3d4d;
            }

            QLabel#taskTitle {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
            }

            #taskDetails {
                color: #64748b;
                font-size: 12px;
            }

            QLabel#taskDescription {
                color: #9ca3af;
                font-size: 11px;
            }

            /* ===== HEADER / ACTION BUTTONS ===== */

            QPushButton#headerButton {
                min-height: 20px;
                padding: 7px 14px;
            }

            QPushButton#taskAction,
            QPushButton#deleteAction {
                background: #151e28;
                border: 1px solid #263442;
                border-radius: 8px;
                color: #94a3b8;
                padding: 0;
                font-size: 14px;
            }

            QPushButton#taskAction:hover {
                background: #1b2937;
                color: #f8fafc;
            }

            QPushButton#deleteAction:hover {
                background: #29191d;
                border-color: #5b2a30;
                color: #fca5a5;
            }

            QLabel#priorityBadge {
                border-radius: 11px;
                padding: 0 12px;
                font-size: 11px;
                font-weight: bold;
                background: #1e293b;
                color: #cbd5e1;
            }

            QLabel#priorityBadge[priority="high"] {
                background: #3b1219;
                color: #fca5a5;
            }

            QLabel#priorityBadge[priority="medium"] {
                background: #3a2a0e;
                color: #fcd34d;
            }

            QLabel#priorityBadge[priority="low"] {
                background: #0f2f22;
                color: #86efac;
            }

            /* ===== ADD TASK ===== */

            #addTaskButton {
                background: #e2e8f0;
                color: #0b0f14;
                border: none;
                border-radius: 9px;
                font-size: 15px;
                font-weight: 750;
            }

            #addTaskButton:hover {
                background: #ffffff;
            }

            #addTaskButton:pressed {
                background: #cbd5e1;
            }

            /* ===== WEEK VIEW ===== */

            #weekView {
                background: transparent;
                border: none;
            }

            QFrame#weekDay {
                background-color: #11161d;
                border: 1px solid #252d38;
                border-radius: 8px;
            }

            QLabel#weekDayTitle {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }

            #weekEmpty {
                color: #64748b;
                font-size: 13px;
            }

            /* ===== MONTH VIEW ===== */

            QCalendarWidget#monthView QAbstractItemView {
                font-size: 16px;
            }

            QCalendarWidget#monthView QWidget#qt_calendar_navigationbar {
                min-height: 48px;
                max-height: 48px;
            }

            QCalendarWidget#monthView QToolButton {
                font-size: 15px;
            }

            QCalendarWidget#monthView QHeaderView::section {
                font-size: 12px;
                padding: 8px;
            }

            #monthView {
                background: #10161e;
                border: 1px solid #1d2935;
                border-radius: 12px;
            }

            /* ===== SETTINGS ===== */

            #settingsFrame {
                background: #10161e;
                border: 1px solid #1d2935;
                border-radius: 12px;
            }

            #settingsTitle {
                color: #f8fafc;
                font-size: 24px;
                font-weight: 750;
            }

            #settingsInfo {
                color: #a8b4c3;
                font-size: 13px;
            }

            /* ===== CHECKBOX ===== */

            QCheckBox {
                spacing: 5px;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid #3b4a59;
                background: #0b1118;
            }

            QCheckBox::indicator:hover {
                border-color: #64748b;
            }

            QCheckBox::indicator:checked {
                background: #cbd5e1;
                border-color: #cbd5e1;
            }

            /* ===== SCROLLBAR ===== */

            QScrollBar:vertical {
                background: #0b0f14;
                width: 10px;
                margin: 2px;
            }

            QScrollBar::handle:vertical {
                background: #26313d;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #344454;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            /* ===== DIALOGS ===== */

            QDialog,
            QMessageBox {
                background-color: #10161e;
                color: #e5e7eb;
            }

            QDialog QLabel,
            QMessageBox QLabel {
                color: #e5e7eb;
                background: transparent;
            }

            QMessageBox QLabel {
                font-size: 13px;
            }

            QDialog QPushButton,
            QMessageBox QPushButton {
                min-width: 80px;
            }

            QDialog QCheckBox {
                color: #e5e7eb;
            }

            QToolTip {
                background-color: #151b23;
                color: #ffffff;
                border: 1px solid #26313d;
                padding: 4px 6px;
            }

            /* ===== INPUTS ===== */

            QLineEdit,
            QTextEdit,
            QPlainTextEdit,
            QComboBox,
            QDateEdit,
            QTimeEdit,
            QSpinBox {
                background-color: #0d141c;
                color: #e5e7eb;
                border: 1px solid #26313d;
                border-radius: 8px;
                padding: 8px 10px;
                min-height: 20px;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }

            QLineEdit:hover,
            QTextEdit:hover,
            QPlainTextEdit:hover,
            QComboBox:hover,
            QDateEdit:hover,
            QTimeEdit:hover {
                border-color: #344454;
            }

            QLineEdit:focus,
            QTextEdit:focus,
            QPlainTextEdit:focus,
            QComboBox:focus,
            QDateEdit:focus,
            QTimeEdit:focus {
                border: 1px solid #2563eb;
            }

            QComboBox::drop-down,
            QDateEdit::drop-down {
                border: none;
                width: 26px;
            }

            QComboBox QAbstractItemView {
                background-color: #151b23;
                color: #e5e7eb;
                border: 1px solid #26313d;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
                outline: none;
            }

            QFormLayout QLabel {
                color: #e5e7eb;
            }
        """)