"""Entry point for `python -m todo_app`."""

import os
import sys
import tkinter as tk

from .app import TodoApp
from .constants import MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH


def main():
    """Launch the To-Do List application."""
    # Determine data directory (project_root/data/)
    package_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(package_dir))
    data_dir = os.path.join(project_root, "data")
    os.makedirs(data_dir, exist_ok=True)

    root = tk.Tk()
    root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

    app = TodoApp(root, data_dir=data_dir)
    app.change_theme()  # Apply initial theme fully

    root.mainloop()


if __name__ == "__main__":
    main()
