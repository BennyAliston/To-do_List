"""Task persistence layer - handles loading and saving tasks to JSON."""

import json
import os
import uuid


class TaskStorage:
    """Manages task data persistence using a JSON file."""

    def __init__(self, filepath):
        """Initialize storage with the given file path.

        Args:
            filepath: Absolute path to the tasks JSON file.
        """
        self.filepath = filepath

    @property
    def exists(self):
        """Check if the storage file already exists."""
        return os.path.exists(self.filepath)

    def load(self):
        """Load tasks from the JSON file.

        Returns:
            tuple: (tasks_list, was_updated) where was_updated indicates
                   if any tasks were assigned new IDs.

        Raises:
            FileNotFoundError: If the storage file doesn't exist.
            json.JSONDecodeError: If the file contains invalid JSON.
        """
        with open(self.filepath, "r") as f:
            loaded_tasks = json.load(f)

        tasks = []
        updated = False

        for item in loaded_tasks:
            if isinstance(item, dict):
                if "id" not in item or not item["id"]:
                    item["id"] = str(uuid.uuid4())
                    updated = True
                tasks.append(item)

        return tasks, updated

    def save(self, tasks):
        """Save tasks to the JSON file.

        Args:
            tasks: List of task dictionaries to persist.

        Raises:
            IOError: If the file cannot be written.
        """
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        # Ensure all tasks have valid IDs
        for task in tasks:
            if "id" not in task or not task["id"]:
                task["id"] = str(uuid.uuid4())

        with open(self.filepath, "w") as f:
            json.dump(tasks, f, indent=4)
