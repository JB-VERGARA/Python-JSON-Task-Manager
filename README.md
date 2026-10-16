# Python JSON Task Manager

A simple offline desktop task manager built with **Python, PySide6, and JSON**.

Designed for personal use with a focus on simplicity, portability, and local data storage.

## ✨ Features

- 📅 Calendar-based task management
- ✅ Add, edit, complete, and delete tasks
- 📝 Task descriptions
- 🕐 Task dates and times
- 🚦 Task priorities
- 📆 Week and month views
- 💾 Local JSON data storage
- 🔄 Automatic daily backups
- 📦 Portable JSON format
- 📴 Works completely offline
- 🎨 Custom desktop interface

## 🛠️ Built With

- **Python 3.13**
- **PySide6**
- **JSON**
- **UUID**

## 🚀 Getting Started
1. Clone the repository
git clone https://github.com/JB-VERGARA/Python-JSON-Task-Manager.git
cd Python-JSON-Task-Manager

2. Create a virtual environment
py -3.13 -m venv .venv

3. Activate the virtual environment
Windows PowerShell:
.\.venv\Scripts\Activate.ps1

4. Install dependencies
pip install -r requirements.txt

5. Run the application
python main.py

## 💾 Data Storage
Tasks are stored locally in:
data/tasks.json

The application does not require:
- An account
- A hosted database
- Internet access
- Cloud storage
Daily backups are automatically stored in:
data/backups/

The JSON structure is versioned using schema_version, allowing the data format to evolve and potentially be reused by a future web version of the application.

## 🔄 Portable JSON
Task data is intentionally stored in a structured JSON format instead of a proprietary database.
This makes it possible to:
- Back up tasks easily
- Move tasks between computers
- Inspect the data manually
- Reuse the data structure for future projects
- Build a future web/PWA version around the same data format

## 🖥️ Screenshots

<img width="1278" height="796" alt="image" src="https://github.com/user-attachments/assets/1e6d8a16-361a-4265-bc5e-83fe57624ab6" />
<br>


<img width="1275" height="822" alt="image" src="https://github.com/user-attachments/assets/81bba904-899e-471d-8210-7a4230e236a2" />
<br>


<img width="1279" height="836" alt="image" src="https://github.com/user-attachments/assets/30467d4a-3dc1-4581-84e8-7af4027f3b50" />
<br>



