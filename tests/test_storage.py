"""Tests for the TaskStorage class."""

import json
import os
import tempfile
import unittest

from todo_app.storage import TaskStorage


class TestTaskStorage(unittest.TestCase):
    """Unit tests for task persistence."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.filepath = os.path.join(self.tmp_dir, "tasks.json")
        self.storage = TaskStorage(self.filepath)

    def tearDown(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
        os.rmdir(self.tmp_dir)

    def test_exists_false_initially(self):
        self.assertFalse(self.storage.exists)

    def test_save_and_load(self):
        tasks = [
            {
                "id": "abc-123",
                "task": "Test task",
                "deadline": "01-03-2026",
                "priority": "Medium",
                "category": "Work",
                "completed": False,
            }
        ]
        self.storage.save(tasks)
        self.assertTrue(self.storage.exists)

        loaded, updated = self.storage.load()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["task"], "Test task")
        self.assertFalse(updated)

    def test_load_assigns_missing_ids(self):
        # Write a task without an id
        with open(self.filepath, "w") as f:
            json.dump([{"task": "No ID task", "completed": False}], f)

        loaded, updated = self.storage.load()
        self.assertTrue(updated)
        self.assertIn("id", loaded[0])
        self.assertTrue(len(loaded[0]["id"]) > 0)

    def test_save_creates_directory(self):
        nested = os.path.join(self.tmp_dir, "sub", "dir", "tasks.json")
        storage = TaskStorage(nested)
        storage.save([{"id": "x", "task": "nested"}])
        self.assertTrue(os.path.exists(nested))
        # Cleanup
        os.remove(nested)
        os.rmdir(os.path.join(self.tmp_dir, "sub", "dir"))
        os.rmdir(os.path.join(self.tmp_dir, "sub"))

    def test_load_nonexistent_raises(self):
        with self.assertRaises(FileNotFoundError):
            self.storage.load()

    def test_load_corrupt_json_raises(self):
        with open(self.filepath, "w") as f:
            f.write("{invalid json")

        with self.assertRaises(json.JSONDecodeError):
            self.storage.load()


if __name__ == "__main__":
    unittest.main()
