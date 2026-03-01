# To-Do List Application

A modern, feature-rich To-Do List application built with Python and Tkinter. Stay organized with a clean interface, task prioritization, deadlines, visual statistics, and customizable themes.

## Features

- **Task Management** — Add, edit, delete tasks with priorities, deadlines, categories, and completion tracking
- **Dashboard & Analytics** — Pie chart, real-time stat cards (total / pending / overdue)
- **Three Themes** — *Minimal Light*, *Soothing Dark*, *Matcha Latte* — instant switching
- **Search & Filter** — Full-text search, filter by status or category, sortable columns
- **Keyboard Shortcuts** — Ctrl+N, Ctrl+F, Delete, Ctrl+S, and more
- **Persistent Storage** — Automatic JSON save/load with UUID-based task IDs

## Installation

```bash
git clone https://github.com/BennyAliston/To-do_List.git
cd To-do_List
pip install -r requirements.txt
```

## Requirements

- Python 3.8+
- tkinter (ships with CPython)
- tkcalendar >= 1.6.1
- pillow >= 9.0.0

## Quick Start

```bash
# Option 1 — convenience script
python run.py

# Option 2 — run as a package
python -m todo_app          # requires src/ on PYTHONPATH (or pip install -e .)

# Option 3 — install in editable mode
pip install -e .
todo-app
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+N` | Focus new task input |
| `Ctrl+F` | Focus search box |
| `Delete` | Remove selected task(s) |
| `Ctrl+S` | Save changes |
| `Enter` | Add task (in task field) |
| `Escape` | Clear field / close dialog |
| `Double-click` | Edit task |
| `Right-click` | Context menu |

## Project Structure

```
To-do_List/
├── README.md                   # This file
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
├── pyproject.toml              # Python packaging config (PEP 621)
├── requirements.txt            # Pip dependencies
├── run.py                      # Convenience entry point
│
├── src/
│   └── todo_app/               # Main application package
│       ├── __init__.py         # Package metadata & version
│       ├── __main__.py         # `python -m todo_app` entry point
│       ├── app.py              # TodoApp class (GUI + logic)
│       ├── constants.py        # App-wide constants & config
│       ├── themes.py           # Theme color definitions
│       └── storage.py          # JSON persistence layer
│
├── multiplatform/              # Cross-platform Flet version (WIP)
│   ├── README.md
│   ├── requirements.txt
│   └── main.py
│
├── legacy/                     # Archived old version
│   ├── todo_list.py
│   └── tasks.json
│
├── data/                       # Runtime data (auto-generated)
│   └── tasks.json
│
└── tests/                      # Unit tests
    ├── __init__.py
    └── test_storage.py
```

## Data Storage

Tasks are stored in `data/tasks.json`:

```json
[
  {
    "id": "unique-uuid",
    "task": "Task description",
    "deadline": "DD-MM-YYYY",
    "priority": "Low|Medium|High",
    "category": "Work|Personal|Health|Finance|Other",
    "completed": false
  }
]
```

## Testing

```bash
cd To-do_List
python -m pytest tests/ -v
```

## Future Development

The `multiplatform/` directory contains a work-in-progress version using the **Flet** framework for cross-platform deployment (Windows, macOS, Linux, Web, iOS, Android).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE).

## Author

**Kritagya Kumar (Benny Aliston)**
- GitHub: [@BennyAliston](https://github.com/BennyAliston)
