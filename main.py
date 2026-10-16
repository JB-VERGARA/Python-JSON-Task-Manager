import sys

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from app.storage import ensure_data_file


def main():
    ensure_data_file()

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()