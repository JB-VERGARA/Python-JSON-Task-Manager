import json
import shutil
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
BACKUP_DIR = DATA_DIR / "backups"


DEFAULT_DATA = {
    "schema_version": 1,
    "app": {
        "name": "Bryan To Do List",
        "last_updated": None
    },
    "tasks": []
}


def ensure_data_file():
    """Create the data directory and tasks.json if they don't exist."""

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not TASKS_FILE.exists():
        save_data(
            DEFAULT_DATA.copy(),
            create_backup=False
        )


def load_data():
    """Load task data from tasks.json."""

    ensure_data_file()

    try:
        with TASKS_FILE.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return DEFAULT_DATA.copy()


def create_daily_backup():
    """Create one backup of the current data per day."""

    if not TASKS_FILE.exists():
        return

    BACKUP_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    today = datetime.now().strftime(
        "%Y-%m-%d"
    )

    backup_file = (
        BACKUP_DIR
        / f"tasks_{today}.json"
    )

    # Only create one automatic backup per day
    if backup_file.exists():
        return

    shutil.copy2(
        TASKS_FILE,
        backup_file
    )


def save_data(
    data,
    create_backup=True
):
    """Save task data to tasks.json."""

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if create_backup:
        create_daily_backup()

    data["app"]["last_updated"] = (
        datetime.now()
        .astimezone()
        .isoformat()
    )

    with TASKS_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def validate_data(data):
    """Validate imported task data."""

    if not isinstance(data, dict):
        return False

    if "schema_version" not in data:
        return False

    if "app" not in data:
        return False

    if "tasks" not in data:
        return False

    if not isinstance(
        data["tasks"],
        list
    ):
        return False

    for task in data["tasks"]:

        if not isinstance(
            task,
            dict
        ):
            return False

        required_fields = [
            "id",
            "title",
            "date",
            "time",
            "priority",
            "completed",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:

            if field not in task:
                return False

    return True