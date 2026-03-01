"""Main application module - TodoApp Tkinter GUI."""

import math
import tkinter as tk
from datetime import date, datetime
from tkinter import messagebox, ttk

from tkcalendar import DateEntry

from .constants import (
    APP_TITLE,
    BASE_FONT,
    BOLD_FONT,
    CARD_TITLE_FONT,
    CATEGORIES,
    CHART_COMPLETED_COLOR,
    CHART_EMPTY_FONT,
    CHART_LABEL_FONT,
    CHART_PENDING_COLOR,
    COLUMN_ANCHORS,
    COLUMN_WIDTHS,
    DATE_FORMAT,
    DEFAULT_CATEGORY,
    DEFAULT_FILTER,
    DEFAULT_PRIORITY,
    DEFAULT_SORT_COLUMN,
    DEFAULT_THEME,
    DEFAULT_WINDOW_SIZE,
    HEADER_FONT,
    KEYBOARD_SHORTCUTS,
    LABEL_FONT,
    PRIORITY_COLORS,
    PRIORITY_LEVELS,
    PRIORITY_ORDER,
    SMALL_FONT,
    STAT_OVERDUE_COLOR,
    STAT_PENDING_COLOR,
    STAT_TOTAL_COLOR,
    STAT_VALUE_FONT,
    TREEVIEW_COLUMNS,
    WELCOME_FONT,
)
from .storage import TaskStorage
from .themes import THEMES


class TodoApp:
    """Main To-Do List application with Tkinter GUI."""

    def __init__(self, root, data_dir):
        """Initialize the application.

        Args:
            root: The Tkinter root window.
            data_dir: Directory path for storing task data.
        """
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.style = ttk.Style()

        # Initialize storage
        self.storage = TaskStorage(
            filepath=__import__("os").path.join(data_dir, "tasks.json")
        )
        self.is_first_run = not self.storage.exists

        # Theme configuration
        self.themes = THEMES
        self.current_theme = DEFAULT_THEME

        # Core data structures
        self.tasks = []
        self.sort_column = DEFAULT_SORT_COLUMN
        self.sort_order = True  # True = ascending
        self.categories = list(CATEGORIES)

        # Configure base style and build UI
        self.style.theme_use("clam")
        self.create_ui()
        self.configure_styles()
        self.create_context_menu()

        # Load existing tasks
        self.load_tasks()
        self.update_status()
        self.update_dashboard()

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.task_entry.focus())
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus())
        self.root.bind("<Delete>", lambda e: self.remove_task())
        self.root.bind("<Control-s>", lambda e: self.save_tasks())

    # ------------------------------------------------------------------ #
    #  Task Lookup                                                        #
    # ------------------------------------------------------------------ #

    def _find_task_by_id(self, task_id):
        """Find a task by its unique ID."""
        for task in self.tasks:
            if task.get("id") == task_id:
                return task
        return None

    # ------------------------------------------------------------------ #
    #  Context Menu                                                       #
    # ------------------------------------------------------------------ #

    def create_context_menu(self):
        """Create the right-click context menu for tasks."""
        if not hasattr(self, "tree"):
            return

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Mark as Complete/Incomplete", command=self.mark_complete
        )
        self.context_menu.add_command(label="Edit", command=self.edit_task)
        self.context_menu.add_command(label="Delete", command=self.remove_task)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Display the context menu at mouse position."""
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            task = self._find_task_by_id(item_id)
            if task:
                self.context_menu.post(event.x_root, event.y_root)

    # ------------------------------------------------------------------ #
    #  Task Operations                                                    #
    # ------------------------------------------------------------------ #

    def mark_complete(self):
        """Toggle completion status of selected task(s)."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No task selected!")
            return

        updated = False
        for item_id in selected_items:
            task = self._find_task_by_id(item_id)
            if task:
                task["completed"] = not task["completed"]
                updated = True

        if updated:
            self.save_tasks()
            self.update_treeview()
            self.update_status()

    def add_task(self):
        """Add a new task with current input values."""
        import uuid

        task_text = self.task_entry.get().strip()
        deadline_str = self.cal.get_date().strftime(DATE_FORMAT)
        priority = self.priority_combo.get()
        category = self.category_combo.get()

        if not task_text:
            messagebox.showerror("Error", "Task description cannot be empty!")
            return

        try:
            deadline_date = datetime.strptime(deadline_str, DATE_FORMAT).date()
            if deadline_date < date.today():
                if not messagebox.askyesno(
                    "Warning", "The deadline is in the past. Add anyway?"
                ):
                    return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format selected!")
            return

        new_task = {
            "id": str(uuid.uuid4()),
            "task": task_text,
            "deadline": deadline_str,
            "priority": priority,
            "category": category,
            "completed": False,
        }

        self.tasks.append(new_task)
        self.save_tasks()
        self.clear_inputs()
        self.update_treeview()
        self.update_status()
        self.update_dashboard()

    def remove_task(self):
        """Remove selected task(s) after confirmation."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No task selected to remove!")
            return

        confirm_msg = (
            f"Are you sure you want to delete {len(selected_items)} selected task(s)?"
        )
        if not messagebox.askyesno("Confirm Delete", confirm_msg):
            return

        ids_to_remove = list(selected_items)
        original_count = len(self.tasks)
        self.tasks = [
            task for task in self.tasks if task.get("id") not in ids_to_remove
        ]

        if len(self.tasks) < original_count:
            self.save_tasks()
            self.update_treeview()
            self.update_status()
        else:
            messagebox.showerror("Error", "Could not find selected tasks to remove.")

    def clear_inputs(self):
        """Reset all input fields to defaults."""
        self.task_entry.delete(0, tk.END)
        self.cal.set_date(date.today())
        self.priority_combo.set(DEFAULT_PRIORITY)
        if hasattr(self, "category_combo"):
            self.category_combo.set(DEFAULT_CATEGORY)
            if DEFAULT_CATEGORY not in self.categories and self.categories:
                self.category_combo.set(self.categories[0])
        self.update_priority_style()
        self.task_entry.focus()

    # ------------------------------------------------------------------ #
    #  Persistence                                                        #
    # ------------------------------------------------------------------ #

    def save_tasks(self):
        """Save all tasks to disk."""
        try:
            self.storage.save(self.tasks)
        except IOError as e:
            messagebox.showerror(
                "Error", f"Failed to save tasks to {self.storage.filepath}: {e}"
            )
        except Exception as e:
            messagebox.showerror(
                "Error", f"An unexpected error occurred while saving tasks: {e}"
            )

    def load_tasks(self):
        """Load tasks from disk."""
        try:
            tasks, was_updated = self.storage.load()
            self.tasks = tasks
            if was_updated:
                self.save_tasks()
            self.update_treeview()
        except FileNotFoundError:
            self.tasks = []
            self.update_treeview()
        except __import__("json").JSONDecodeError:
            messagebox.showerror(
                "Error",
                "Error reading tasks file. File might be corrupted. Starting fresh.",
            )
            self.tasks = []
            self.update_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")
            self.tasks = []
            self.update_treeview()

    # ------------------------------------------------------------------ #
    #  Sorting                                                            #
    # ------------------------------------------------------------------ #

    def sort_tasks(self, column):
        """Sort tasks by the given column."""
        if self.sort_column == column:
            self.sort_order = not self.sort_order
        else:
            self.sort_column = column
            self.sort_order = True

        reverse = not self.sort_order

        if column == "deadline":
            def deadline_key(task):
                try:
                    return datetime.strptime(task.get("deadline", ""), DATE_FORMAT)
                except (ValueError, TypeError):
                    return datetime.max
            key_func = deadline_key
        elif column == "priority":
            key_func = lambda task: PRIORITY_ORDER.get(
                task.get("priority", DEFAULT_PRIORITY), 2
            )
        elif column == "completed":
            key_func = lambda task: task.get("completed", False)
        else:
            key_func = lambda task: task.get("task", "").lower()

        try:
            self.tasks.sort(key=key_func, reverse=reverse)
        except Exception as e:
            messagebox.showerror("Sort Error", f"Could not sort tasks: {e}")
            return

        for col in self.tree["columns"]:
            indicator = ""
            if col == self.sort_column:
                indicator = " ▲" if self.sort_order else " ▼"
            self.tree.heading(col, text=f"{col.capitalize()}{indicator}")

        self.update_treeview()

    # ------------------------------------------------------------------ #
    #  Treeview Display                                                   #
    # ------------------------------------------------------------------ #

    def update_treeview(self):
        """Refresh the task list based on current filters and search."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        current_filter = self.filter_combo.get()
        search_query = self.search_entry.get().strip().lower()

        for task in self.tasks:
            task_id = task.get("id")
            if not task_id:
                continue

            task_completed = task.get("completed", False)
            task_category = task.get("category", DEFAULT_CATEGORY)

            # Status / category filter
            if current_filter == "Completed" and not task_completed:
                continue
            elif current_filter == "Pending" and task_completed:
                continue
            elif current_filter in self.categories and task_category != current_filter:
                continue

            # Text search filter
            if search_query:
                searchable = " ".join(
                    [
                        task.get("task", ""),
                        task.get("deadline", ""),
                        task.get("priority", ""),
                        task_category,
                    ]
                ).lower()
                if search_query not in searchable:
                    continue

            display_completed = "✓" if task_completed else "✗"
            display_values = (
                task.get("task", ""),
                task_category,
                task.get("deadline", ""),
                task.get("priority", DEFAULT_PRIORITY),
                display_completed,
            )

            try:
                tags = ()
                if not task_completed:
                    try:
                        d = datetime.strptime(
                            task.get("deadline", ""), DATE_FORMAT
                        ).date()
                        if d < date.today():
                            tags = ("overdue",)
                        elif d == date.today():
                            tags = ("due_today",)
                    except (ValueError, TypeError):
                        pass

                self.tree.insert("", "end", iid=task_id, values=display_values, tags=tags)
            except tk.TclError as e:
                print(f"Error inserting task {task_id}: {e}")

        self.tree.tag_configure("overdue", foreground="#EF4444")
        self.tree.tag_configure("due_today", foreground="#F59E0B")

    # ------------------------------------------------------------------ #
    #  Edit Task                                                          #
    # ------------------------------------------------------------------ #

    def edit_task_event(self, event):
        """Handle double-click on the Treeview."""
        selected_item = self.tree.focus()
        if selected_item:
            self.edit_task(task_id=selected_item)

    def edit_task(self, task_id=None):
        """Open the edit dialog for a task."""
        if not task_id:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("Warning", "No task selected to edit!")
                return
            task_id = selected_items[0]

        task_to_edit = self._find_task_by_id(task_id)
        if not task_to_edit:
            messagebox.showerror(
                "Error", "Could not find the selected task to edit."
            )
            return

        # Build edit dialog
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Task")
        edit_dialog.geometry("500x450")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        edit_dialog.resizable(False, False)

        theme = self.themes[self.current_theme]
        edit_dialog.configure(bg=theme["bg"])

        main_frame = ttk.Frame(edit_dialog, style="TFrame", padding=(30, 20))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Task ---
        ttk.Label(
            main_frame, text="Task:", style="TLabel", font=LABEL_FONT
        ).pack(anchor="w", pady=(0, 8))
        task_entry = ttk.Entry(main_frame, style="TEntry", width=60)
        task_entry.pack(fill="x", pady=(0, 25))
        task_entry.insert(0, task_to_edit.get("task", ""))
        task_entry.focus_set()
        task_entry.bind("<Tab>", lambda e: cal.focus_set())
        task_entry.bind("<Return>", lambda e: "break")

        # --- Deadline ---
        ttk.Label(
            main_frame, text="Deadline:", style="TLabel", font=LABEL_FONT
        ).pack(anchor="w", pady=(0, 8))
        cal = DateEntry(main_frame, width=30, date_pattern="dd-mm-yyyy", style="TEntry")
        cal.pack(fill="x", pady=(0, 25))
        try:
            cal.set_date(
                datetime.strptime(task_to_edit.get("deadline", ""), DATE_FORMAT)
            )
        except (ValueError, TypeError):
            cal.set_date(date.today())
        cal.bind("<Return>", lambda e: "break")
        cal.bind("<Tab>", lambda e: category_combo.focus_set())

        # --- Category ---
        ttk.Label(
            main_frame, text="Category:", style="TLabel", font=LABEL_FONT
        ).pack(anchor="w", pady=(0, 8))
        category_combo = ttk.Combobox(
            main_frame,
            values=self.categories,
            state="readonly",
            style="TCombobox",
            width=30,
        )
        category_combo.pack(fill="x", pady=(0, 25))
        category_combo.set(task_to_edit.get("category", DEFAULT_CATEGORY))
        if (
            DEFAULT_CATEGORY not in self.categories
            and not category_combo.get()
            and self.categories
        ):
            category_combo.set(self.categories[0])
        category_combo.bind("<Return>", lambda e: "break")
        category_combo.bind("<Tab>", lambda e: priority_combo.focus_set())

        # --- Priority ---
        ttk.Label(
            main_frame, text="Priority:", style="TLabel", font=LABEL_FONT
        ).pack(anchor="w", pady=(0, 8))
        priority_combo = ttk.Combobox(
            main_frame,
            values=PRIORITY_LEVELS,
            state="readonly",
            style="TCombobox",
            width=30,
        )
        priority_combo.pack(fill="x", pady=(0, 25))
        priority_combo.set(task_to_edit.get("priority", DEFAULT_PRIORITY))
        priority_combo.bind("<Return>", lambda e: "break")
        priority_combo.bind("<Tab>", lambda e: completed_cb.focus_set())

        # --- Completed ---
        completed_var = tk.BooleanVar(value=task_to_edit.get("completed", False))
        completed_cb = ttk.Checkbutton(
            main_frame,
            text="Mark as completed",
            variable=completed_var,
            style="TCheckbutton",
            padding=(0, 5),
        )
        completed_cb.pack(anchor="w", pady=(0, 30))
        completed_cb.bind("<Return>", lambda e: "break")
        completed_cb.bind("<Tab>", lambda e: save_button.focus_set())

        # --- Buttons ---
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill="x", pady=(10, 0))

        def save_edits():
            new_text = task_entry.get().strip()
            new_deadline_str = cal.get_date().strftime(DATE_FORMAT)
            new_priority = priority_combo.get()
            new_completed = completed_var.get()

            if not new_text:
                messagebox.showerror(
                    "Error", "Task cannot be empty!", parent=edit_dialog
                )
                task_entry.focus_set()
                return

            try:
                new_deadline_date = datetime.strptime(new_deadline_str, DATE_FORMAT).date()
                if new_deadline_date < date.today():
                    if not messagebox.askyesno(
                        "Warning",
                        "Deadline is in the past. Save anyway?",
                        parent=edit_dialog,
                    ):
                        cal.focus_set()
                        return
            except ValueError:
                messagebox.showerror(
                    "Error", "Invalid date format!", parent=edit_dialog
                )
                cal.focus_set()
                return

            task_to_update = self._find_task_by_id(task_id)
            if task_to_update:
                task_to_update.update(
                    {
                        "task": new_text,
                        "deadline": new_deadline_str,
                        "priority": new_priority,
                        "category": category_combo.get(),
                        "completed": new_completed,
                    }
                )
                self.save_tasks()
                self.update_treeview()
                self.update_status()
                self.update_dashboard()
                edit_dialog.destroy()
            else:
                messagebox.showerror(
                    "Error",
                    "Task could not be found for saving.",
                    parent=edit_dialog,
                )

        save_button = ttk.Button(
            button_frame,
            text="Save Changes (Ctrl+S)",
            command=save_edits,
            style="TButton",
            padding=(20, 10),
        )
        save_button.pack(side="right", padx=5)

        cancel_button = ttk.Button(
            button_frame,
            text="Cancel (Esc)",
            command=edit_dialog.destroy,
            style="TButton",
            padding=(20, 10),
        )
        cancel_button.pack(side="right", padx=5)

        # Tooltips
        self.create_tooltip(task_entry, "Edit the task description\nTab to move to next field")
        self.create_tooltip(cal, "Change the task deadline\nTab to move to next field")
        self.create_tooltip(category_combo, "Change the task category\nTab to move to next field")
        self.create_tooltip(priority_combo, "Change the task priority\nTab to move to next field")
        self.create_tooltip(completed_cb, "Toggle completion status\nTab to move to next field")
        self.create_tooltip(save_button, "Save changes (Ctrl+S)")
        self.create_tooltip(cancel_button, "Discard changes (Esc)")

        # Dialog shortcuts
        edit_dialog.bind("<Control-s>", lambda e: save_edits())
        edit_dialog.bind("<Escape>", lambda e: edit_dialog.destroy())

        # Center dialog
        edit_dialog.update_idletasks()
        w = edit_dialog.winfo_width()
        h = edit_dialog.winfo_height()
        x = (edit_dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (edit_dialog.winfo_screenheight() // 2) - (h // 2)
        edit_dialog.geometry(f"{w}x{h}+{x}+{y}")
        edit_dialog.wait_window()

    # ------------------------------------------------------------------ #
    #  Status Bar                                                         #
    # ------------------------------------------------------------------ #

    def update_status(self):
        """Refresh the status bar with current statistics."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.get("completed", False))
        pending = total - completed
        pct = (completed / total * 100) if total > 0 else 0
        self.status_bar.config(
            text=f"Total: {total} | Completed: {completed} | Pending: {pending} ({pct:.0f}%)"
        )

    def show_status_tooltip(self, event):
        """Show keyboard-shortcut tooltip near the status bar."""
        self.hide_status_tooltip(None)
        try:
            self.status_tooltip_window = tk.Toplevel(self.root)
            self.status_tooltip_window.wm_overrideredirect(True)
            x = self.root.winfo_pointerx() + 15
            y = self.root.winfo_pointery() + 10
            self.status_tooltip_window.wm_geometry(f"+{x}+{y}")

            theme = self.themes[self.current_theme]
            label = ttk.Label(
                self.status_tooltip_window,
                text="\n".join(KEYBOARD_SHORTCUTS),
                background=theme.get("status_bg", "#333333"),
                foreground=theme.get("status_fg", "#FFFFFF"),
                padding=8,
                justify=tk.LEFT,
                relief="solid",
                borderwidth=1,
            )
            label.pack()
            self.root.bind("<Destroy>", self.hide_status_tooltip, add="+")
        except Exception as e:
            print(f"Error showing status tooltip: {e}")
            self.hide_status_tooltip(None)

    def hide_status_tooltip(self, event):
        """Destroy the status-bar tooltip."""
        try:
            if hasattr(self, "status_tooltip_window") and self.status_tooltip_window:
                self.status_tooltip_window.destroy()
                self.status_tooltip_window = None
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  Theme Management                                                   #
    # ------------------------------------------------------------------ #

    def change_theme(self, event=None):
        """Switch to the theme selected in the combo box."""
        new_theme = self.theme_combo.get()
        if new_theme in self.themes and new_theme != self.current_theme:
            self.current_theme = new_theme
            self.configure_styles()

    def configure_styles(self):
        """Apply the current theme to all ttk styles and widgets."""
        theme = self.themes[self.current_theme]

        # Base styles
        self.style.configure(
            ".", background=theme["bg"], foreground=theme["fg"], font=BASE_FONT
        )
        self.style.configure("TFrame", background=theme["bg"])
        self.style.configure(
            "TLabel", background=theme["bg"], foreground=theme["fg"], font=BASE_FONT
        )

        # Entry
        self.style.configure(
            "TEntry",
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            insertcolor=theme["fg"],
            selectbackground=theme["entry_select_bg"],
            selectforeground=theme["entry_select_fg"],
            borderwidth=1,
            relief="solid",
            bordercolor=theme["border_color"],
            padding=8,
        )
        self.style.map(
            "TEntry",
            bordercolor=[("focus", theme["fg"]), ("!focus", theme["border_color"])],
            lightcolor=[("focus", theme["fg"]), ("!focus", theme["border_color"])],
            darkcolor=[("focus", theme["fg"]), ("!focus", theme["border_color"])],
        )

        # Combobox
        self.style.configure(
            "TCombobox",
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            selectbackground=theme["entry_select_bg"],
            selectforeground=theme["entry_select_fg"],
            background=theme["entry_bg"],
            borderwidth=1,
            relief="solid",
            padding=8,
            arrowcolor=theme["fg"],
        )
        self.style.map(
            "TCombobox",
            fieldbackground=[("readonly", theme["entry_bg"])],
            selectbackground=[("readonly", theme["entry_select_bg"])],
            selectforeground=[("readonly", theme["entry_select_fg"])],
            background=[("readonly", theme["entry_bg"])],
            foreground=[("readonly", theme["entry_fg"])],
            bordercolor=[("focus", theme["fg"]), ("!focus", theme["border_color"])],
        )

        # Priority combobox variants
        for priority, color in PRIORITY_COLORS.items():
            style_name = f"Priority.{priority}.TCombobox"
            try:
                self.style.configure(style_name, foreground=color)
            except tk.TclError:
                pass

        # Filter combobox
        self.style.configure(
            "Filter.TCombobox",
            font=BASE_FONT,
            fieldbackground=theme["entry_bg"],
            foreground=theme["entry_fg"],
            padding=8,
            borderwidth=1,
            relief="solid",
            arrowcolor=theme["fg"],
        )
        self.style.map(
            "Filter.TCombobox",
            bordercolor=[("focus", theme["fg"]), ("!focus", theme["border_color"])],
        )

        # Buttons
        self.style.configure(
            "TButton",
            font=BOLD_FONT,
            padding=(20, 10),
            background=theme["button_bg"],
            foreground=theme["button_fg"],
            borderwidth=0,
            relief="flat",
            focusthickness=0,
        )
        self.style.map(
            "TButton",
            background=[("active", theme["active_bg"]), ("pressed", theme["active_bg"])],
            foreground=[("active", theme["button_fg"]), ("pressed", theme["button_fg"])],
        )

        # Header
        self.style.configure("Header.TFrame", background=theme["header_bg"])
        self.style.configure(
            "Header.TLabel",
            background=theme["header_bg"],
            foreground=theme["header_fg"],
            font=HEADER_FONT,
            padding=(0, 20),
        )

        # Dashboard card title
        self.style.configure(
            "CardTitle.TLabel",
            background=theme["bg"],
            foreground=theme["fg"],
            font=CARD_TITLE_FONT,
        )

        # Treeview
        self.style.configure(
            "Treeview",
            font=BASE_FONT,
            rowheight=45,
            fieldbackground=theme["tree_bg"],
            background=theme["tree_bg"],
            foreground=theme["tree_fg"],
            borderwidth=0,
            relief="flat",
        )
        self.style.configure(
            "Treeview.Heading",
            font=BOLD_FONT,
            background=theme["tree_heading_bg"],
            foreground=theme["tree_heading_fg"],
            relief="flat",
            borderwidth=0,
            padding=10,
        )
        self.style.map(
            "Treeview",
            background=[("selected", theme["tree_selected_bg"])],
            foreground=[("selected", theme["tree_fg"])],
        )

        # Checkbutton
        self.style.configure(
            "TCheckbutton",
            background=theme["bg"],
            foreground=theme["fg"],
            padding=5,
            font=BASE_FONT,
        )
        self.style.map(
            "TCheckbutton",
            background=[("active", theme["bg"])],
            foreground=[("active", theme["fg"])],
        )

        # Status bar
        self.style.configure(
            "Status.TLabel",
            background=theme["status_bg"],
            foreground=theme["status_fg"],
            relief="flat",
            padding=10,
            font=SMALL_FONT,
        )

        # Notebook / tabs
        self.style.configure("TNotebook", background=theme["bg"], borderwidth=0)
        self.style.configure(
            "TNotebook.Tab",
            background=theme["bg"],
            foreground=theme["fg"],
            padding=(20, 10),
            font=BASE_FONT,
            borderwidth=0,
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", theme["button_bg"])],
            foreground=[("selected", theme["button_fg"])],
            expand=[("selected", [0, 0, 0, 0])],
        )

        # Recursively apply to existing widgets
        if hasattr(self, "root"):
            self.root.configure(bg=theme["bg"])
            self._apply_theme_recursive(self.root, theme)

            try:
                if hasattr(self, "header_frame"):
                    self.header_frame.configure(style="Header.TFrame")
                if hasattr(self, "cal"):
                    self.cal.configure(
                        background=theme["calendar_bg"],
                        foreground=theme["calendar_fg"],
                        selectbackground=theme["calendar_select_bg"],
                        selectforeground=theme["calendar_select_fg"],
                        headersbackground=theme["calendar_header_bg"],
                        headersforeground=theme["calendar_header_fg"],
                        bordercolor=theme["border_color"],
                        normalbackground=theme["calendar_bg"],
                        normalforeground=theme["calendar_fg"],
                        weekendbackground=theme["calendar_weekend_bg"],
                        weekendforeground=theme["calendar_weekend_fg"],
                        othermonthbackground=theme["calendar_bg"],
                        othermonthwebackground=theme["calendar_bg"],
                        othermonthforeground=theme["calendar_fg"],
                        othermonthweforeground=theme["calendar_fg"],
                    )
                if hasattr(self, "chart_canvas"):
                    self.chart_canvas.configure(bg=theme["bg"])
                    self.draw_pie_chart()
            except Exception as e:
                print(f"Error applying styles: {e}")

    def _apply_theme_recursive(self, widget, theme):
        """Recursively apply theme colours to all child widgets."""
        try:
            if isinstance(widget, ttk.Frame):
                current_style = widget.cget("style")
                if not current_style or current_style == "TFrame":
                    widget.configure(style="TFrame")
            elif isinstance(widget, tk.Canvas):
                widget.configure(bg=theme["bg"], highlightthickness=0)

            for child in widget.winfo_children():
                self._apply_theme_recursive(child, theme)
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  UI Construction                                                    #
    # ------------------------------------------------------------------ #

    def create_ui(self):
        """Build the main UI with notebook tabs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tasks tab
        self.tasks_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tasks_frame, text="   Tasks   ")
        self.create_tasks_view(self.tasks_frame)

        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.dashboard_frame, text="   Dashboard   ")
        self.create_dashboard_view(self.dashboard_frame)

        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.update_dashboard())

    def create_tasks_view(self, parent):
        """Build the tasks tab: inputs, search, treeview, status bar."""
        main_container = ttk.Frame(parent, style="TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Header
        header_frame = ttk.Frame(main_container, style="Header.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(
            header_frame, text="To-Do List Manager", style="Header.TLabel"
        ).pack(pady=5)

        # First-run welcome
        if self.is_first_run:
            welcome_frame = ttk.Frame(main_container, style="TFrame")
            welcome_frame.pack(fill=tk.X, pady=(0, 10))
            ttk.Label(
                welcome_frame,
                text=(
                    "Welcome! Add tasks below.\n"
                    "Tips: Ctrl+N=New, Ctrl+F=Search, Del=Remove, "
                    "Double-click=Edit, Right-click=Options"
                ),
                justify=tk.CENTER,
                style="TLabel",
                font=WELCOME_FONT,
            ).pack(pady=3)

        # --- Input row ---
        input_frame = ttk.Frame(main_container, style="TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)

        ttk.Label(
            input_frame, text="Task:", style="TLabel", font=LABEL_FONT
        ).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.task_entry = ttk.Entry(input_frame, width=60, style="TEntry")
        self.task_entry.grid(row=0, column=1, columnspan=7, padx=5, pady=5, sticky="ew")
        self.task_entry.bind("<Return>", lambda event: self.add_task())
        self.task_entry.bind("<Escape>", lambda event: self.clear_inputs())
        self.create_tooltip(self.task_entry, "Enter task, press Enter to add")

        # Deadline
        ttk.Label(
            input_frame, text="Deadline:", style="TLabel", font=LABEL_FONT
        ).grid(row=1, column=0, padx=(0, 10), pady=5, sticky="w")
        self.cal = DateEntry(
            input_frame, date_pattern="dd-mm-yyyy", width=12, style="TEntry"
        )
        self.cal.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.cal.set_date(date.today())
        self.create_tooltip(self.cal, "Select task deadline")

        # Category
        ttk.Label(
            input_frame, text="Category:", style="TLabel", font=LABEL_FONT
        ).grid(row=1, column=2, padx=(20, 10), pady=5, sticky="w")
        self.category_combo = ttk.Combobox(
            input_frame, values=self.categories, width=12, state="readonly"
        )
        self.category_combo.grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.category_combo.set(DEFAULT_CATEGORY)
        if DEFAULT_CATEGORY not in self.categories:
            self.category_combo.set(self.categories[0])
        self.create_tooltip(self.category_combo, "Select task category")

        # Priority
        ttk.Label(
            input_frame, text="Priority:", style="TLabel", font=LABEL_FONT
        ).grid(row=1, column=4, padx=(20, 10), pady=5, sticky="w")
        self.priority_combo = ttk.Combobox(
            input_frame, values=PRIORITY_LEVELS, width=12, state="readonly"
        )
        self.priority_combo.grid(row=1, column=5, padx=5, pady=5, sticky="w")
        self.priority_combo.set(DEFAULT_PRIORITY)
        self.update_priority_style()
        self.priority_combo.bind("<<ComboboxSelected>>", self.update_priority_style)
        self.create_tooltip(self.priority_combo, "Set task priority level")

        # Add button
        add_button = ttk.Button(
            input_frame, text="Add Task", command=self.add_task, style="TButton"
        )
        add_button.grid(row=1, column=6, padx=(20, 0), pady=5)
        self.create_tooltip(add_button, "Add new task (Ctrl+N)")

        # --- Search / filter row ---
        controls_frame = ttk.Frame(main_container, style="TFrame")
        controls_frame.pack(fill=tk.X, pady=(10, 15))
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(
            controls_frame, text="Search:", style="TLabel", font=LABEL_FONT
        ).grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")
        self.search_entry = ttk.Entry(controls_frame, style="TEntry")
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.update_treeview())
        self.search_entry.bind(
            "<Escape>",
            lambda e: [self.search_entry.delete(0, tk.END), self.update_treeview()],
        )
        self.create_tooltip(self.search_entry, "Search tasks (Ctrl+F)\nPress Esc to clear")

        ttk.Label(
            controls_frame, text="Filter:", style="TLabel", font=LABEL_FONT
        ).grid(row=0, column=2, padx=(20, 10), pady=5, sticky="w")
        self.filter_combo = ttk.Combobox(
            controls_frame,
            values=[DEFAULT_FILTER, "Completed", "Pending"] + self.categories,
            width=12,
            state="readonly",
            style="Filter.TCombobox",
        )
        self.filter_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.filter_combo.set(DEFAULT_FILTER)
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_treeview())
        self.create_tooltip(self.filter_combo, "Filter tasks by status or category")

        ttk.Label(
            controls_frame, text="Theme:", style="TLabel", font=LABEL_FONT
        ).grid(row=0, column=4, padx=(20, 10), pady=5, sticky="w")
        self.theme_combo = ttk.Combobox(
            controls_frame,
            values=list(self.themes.keys()),
            width=10,
            state="readonly",
            style="Filter.TCombobox",
        )
        self.theme_combo.grid(row=0, column=5, padx=5, pady=5, sticky="w")
        self.theme_combo.set(self.current_theme)
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        self.create_tooltip(self.theme_combo, "Change application theme")

        # Action buttons
        button_frame = ttk.Frame(main_container, style="TFrame")
        button_frame.pack(fill=tk.X, pady=(0, 10))

        remove_button = ttk.Button(
            button_frame,
            text="Remove Selected",
            command=self.remove_task,
            style="TButton",
        )
        remove_button.pack(side=tk.RIGHT, padx=5)
        self.create_tooltip(remove_button, "Delete selected tasks (Delete Key)")

        # --- Treeview ---
        tree_frame = ttk.Frame(main_container)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.tree = ttk.Treeview(
            tree_frame, columns=TREEVIEW_COLUMNS, show="headings", style="Treeview"
        )
        for col in TREEVIEW_COLUMNS:
            self.tree.heading(
                col,
                text=col.capitalize(),
                command=lambda c=col: self.sort_tasks(c),
                anchor="center",
            )
            self.tree.column(
                col,
                width=COLUMN_WIDTHS.get(col, 100),
                anchor=COLUMN_ANCHORS.get(col, "center"),
                stretch=tk.YES if col == "task" else tk.NO,
            )

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", self.edit_task_event)
        self.tree.bind("<Delete>", lambda e: self.remove_task())
        self.create_tooltip(self.tree, "Double-click to edit\nRight-click for options")

        # Status bar
        self.status_bar = ttk.Label(
            main_container, text="Status Bar", style="Status.TLabel", anchor="w"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.status_bar.bind("<Enter>", self.show_status_tooltip)
        self.status_bar.bind("<Leave>", self.hide_status_tooltip)

    # ------------------------------------------------------------------ #
    #  Dashboard                                                          #
    # ------------------------------------------------------------------ #

    def create_dashboard_view(self, parent):
        """Build the dashboard tab with stat cards and pie chart."""
        stats_frame = ttk.Frame(parent, style="TFrame")
        stats_frame.pack(fill=tk.X, padx=20, pady=20)

        def create_card(parent_frame, title, var, color):
            card = ttk.Frame(parent_frame, style="TFrame", relief="solid", borderwidth=1)
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(pady=(10, 5))
            ttk.Label(
                card, textvariable=var, font=STAT_VALUE_FONT, foreground=color
            ).pack(pady=(0, 10))
            return card

        self.stat_total = tk.StringVar(value="0")
        self.stat_pending = tk.StringVar(value="0")
        self.stat_overdue = tk.StringVar(value="0")

        create_card(stats_frame, "Total Tasks", self.stat_total, STAT_TOTAL_COLOR)
        create_card(stats_frame, "Pending", self.stat_pending, STAT_PENDING_COLOR)
        create_card(stats_frame, "Overdue/Today", self.stat_overdue, STAT_OVERDUE_COLOR)

        charts_frame = ttk.Frame(parent, style="TFrame")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.chart_canvas = tk.Canvas(
            charts_frame,
            bg=self.themes[self.current_theme]["bg"],
            highlightthickness=0,
        )
        self.chart_canvas.pack(fill=tk.BOTH, expand=True)
        self.chart_canvas.bind("<Configure>", lambda e: self.draw_pie_chart())

    def update_dashboard(self):
        """Recalculate statistics and refresh the dashboard."""
        if not hasattr(self, "stat_total"):
            return

        total = len(self.tasks)
        pending = sum(1 for t in self.tasks if not t.get("completed", False))

        today = date.today()
        overdue_or_today = 0
        for t in self.tasks:
            if not t.get("completed", False):
                try:
                    d = datetime.strptime(t.get("deadline", ""), DATE_FORMAT).date()
                    if d <= today:
                        overdue_or_today += 1
                except (ValueError, TypeError):
                    pass

        self.stat_total.set(str(total))
        self.stat_pending.set(str(pending))
        self.stat_overdue.set(str(overdue_or_today))

        if self.notebook.select() == str(self.dashboard_frame):
            self.draw_pie_chart()

    def draw_pie_chart(self):
        """Render a simple pie chart of task completion status."""
        if not hasattr(self, "chart_canvas"):
            return

        self.chart_canvas.delete("all")
        width = self.chart_canvas.winfo_width()
        height = self.chart_canvas.winfo_height()

        if width < 50 or height < 50:
            return

        total = len(self.tasks)
        if total == 0:
            self.chart_canvas.create_text(
                width / 2,
                height / 2,
                text="No Tasks Available",
                fill=self.themes[self.current_theme]["fg"],
                font=CHART_EMPTY_FONT,
            )
            return

        completed_count = sum(1 for t in self.tasks if t.get("completed", False))
        pending_count = total - completed_count

        angles = []
        if completed_count > 0:
            angles.append(
                (completed_count / total * 360, CHART_COMPLETED_COLOR, "Completed")
            )
        if pending_count > 0:
            angles.append(
                (pending_count / total * 360, CHART_PENDING_COLOR, "Pending")
            )

        x, y, r = width / 2, height / 2, min(width, height) / 3
        start_angle = 90

        for angle, color, label in angles:
            extent = angle
            self.chart_canvas.create_arc(
                x - r,
                y - r,
                x + r,
                y + r,
                start=start_angle,
                extent=extent,
                fill=color,
                outline=self.themes[self.current_theme]["bg"],
            )

            mid_angle = start_angle + extent / 2
            lab_x = x + (r + 40) * math.cos(math.radians(mid_angle))
            lab_y = y - (r + 40) * math.sin(math.radians(mid_angle))
            text = f"{label} ({int(extent / 360 * 100)}%)"

            anchor = "center"
            if lab_x < x:
                anchor = "e"
            elif lab_x > x:
                anchor = "w"

            self.chart_canvas.create_text(
                lab_x,
                lab_y,
                text=text,
                fill=self.themes[self.current_theme]["fg"],
                font=CHART_LABEL_FONT,
                anchor=anchor,
            )
            start_angle += extent

    # ------------------------------------------------------------------ #
    #  Helpers                                                            #
    # ------------------------------------------------------------------ #

    def create_tooltip(self, widget, text):
        """Attach a hover tooltip to a widget."""
        tooltip = None

        def show_tooltip(event):
            nonlocal tooltip
            if tooltip:
                return
            tooltip = tk.Toplevel(self.root)
            tooltip.wm_overrideredirect(True)
            x = self.root.winfo_pointerx() + 15
            y = self.root.winfo_pointery() + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            theme = self.themes[self.current_theme]
            label = ttk.Label(
                tooltip,
                text=text,
                background=theme.get("status_bg", "#FFFFE0"),
                foreground=theme.get("status_fg", "#000000"),
                padding=5,
                justify=tk.LEFT,
                relief="solid",
                borderwidth=1,
            )
            label.pack()
            widget.tooltip_window = tooltip

        def hide_tooltip(event):
            nonlocal tooltip
            if hasattr(widget, "tooltip_window") and widget.tooltip_window:
                widget.tooltip_window.destroy()
                widget.tooltip_window = None
            tooltip = None

        widget.bind("<Enter>", show_tooltip, add="+")
        widget.bind("<Leave>", hide_tooltip, add="+")
        widget.bind("<Destroy>", hide_tooltip, add="+")

    def update_priority_style(self, event=None):
        """Update the priority combobox colour based on selection."""
        if not hasattr(self, "priority_combo"):
            return

        priority = self.priority_combo.get()
        style_name = f"Priority.{priority}.TCombobox"

        try:
            if priority in PRIORITY_COLORS:
                self.style.configure(style_name, foreground=PRIORITY_COLORS[priority])
            self.priority_combo.configure(style=style_name)
        except Exception:
            self.priority_combo.configure(style="TCombobox")
