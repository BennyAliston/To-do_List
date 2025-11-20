import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry
import json


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test To-Do List")
        self.root.geometry("800x600")
        self.style = ttk.Style()

        # Modern theme and color scheme
        self.style.theme_use('clam')
        self.configure_styles()

        self.tasks = []
        self.sort_column = 'deadline'
        self.sort_order = True

        self.create_ui()
        self.create_context_menu()
        self.load_tasks()
        self.update_status()

        # Bind keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.task_entry.focus())
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.bind('<Delete>', lambda e: self.remove_task())
        self.root.bind('<Control-s>', lambda e: self.save_tasks())

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Mark as Complete", command=self.mark_complete)
        self.context_menu.add_command(label="Delete", command=self.remove_task)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            item_values = self.tree.item(item, 'values')
            completed_str = item_values[3]
            is_completed = completed_str == 'Yes'
            if is_completed:
                self.context_menu.entryconfig(0, label="Mark as Incomplete")
            else:
                self.context_menu.entryconfig(0, label="Mark as Complete")
            self.context_menu.post(event.x_root, event.y_root)

    def mark_complete(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        for item in selected_items:
            item_values = self.tree.item(item, 'values')
            task_text = item_values[0]
            deadline = item_values[1]
            priority = item_values[2]
            completed_str = item_values[3]
            completed = completed_str == 'Yes'

            for task_index, task in enumerate(self.tasks):
                if (task['task'] == task_text and
                        task['deadline'] == deadline and
                        task['priority'] == priority and
                        task['completed'] == completed):
                    self.tasks[task_index]['completed'] = not self.tasks[task_index]['completed']
                    break
        self.save_tasks()
        self.update_treeview()
        self.update_status()

    def add_task(self):
        task_text = self.task_entry.get().strip()
        deadline = self.cal.get_date().strftime("%d-%m-%Y")
        priority = self.priority_combo.get()

        if not task_text:
            messagebox.showerror("Error", "Task description cannot be empty!")
            return

        try:
            deadline_date = datetime.strptime(deadline, "%d-%m-%Y")
            if deadline_date.date() < date.today():
                messagebox.showerror("Error", "Deadline cannot be in the past!")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format!")
            return

        new_task = {
            'task': task_text,
            'deadline': deadline,
            'priority': priority,
            'completed': False
        }

        self.tasks.append(new_task)
        self.sort_tasks(self.sort_column)
        self.save_tasks()
        self.clear_inputs()
        self.update_treeview()
        self.update_status()

    def configure_styles(self):
        self.style.configure('.', background='#F5F5F5', foreground='#333333')
        self.style.configure('TFrame', background='#F5F5F5')
        self.style.configure('Custom.TCombobox', font=('Segoe UI', 10), padding=8, relief='flat', borderwidth=2,
                             foreground='#37474F', arrowsize=12)
        self.style.map('Custom.TCombobox', fieldbackground=[('readonly', '#FFFFFF')],
                       background=[('readonly', '#FFFFFF')], bordercolor=[('focus', '#2196F3'), ('!focus', '#BDBDBD')],
                       lightcolor=[('focus', '#2196F3')])
        self.style.configure('Calendar.DateEntry', background='#FFFFFF', bordercolor='#BDBDBD', arrowcolor='#2196F3',
                             selectbackground='#2196F3', selectforeground='#FFFFFF', weekendbackground='#FFFFFF',
                             weekendforeground='#E57373', headersbackground='#F5F5F5')
        self.style.configure('Priority.Low.TCombobox', foreground='#4CAF50')
        self.style.configure('Priority.Medium.TCombobox', foreground='#FF9800')
        self.style.configure('Priority.High.TCombobox', foreground='#F44336')
        self.style.configure('Filter.TCombobox', font=('Segoe UI', 10, 'bold'), foreground='#3F51B5', padding=8)
        self.style.configure('TButton', font=('Segoe UI', 10), padding=6, background='#4CAF50', foreground='white')
        self.style.map('TButton', background=[('active', '#45A049'), ('pressed', '#3D8B40')])
        self.style.configure('Header.TFrame', background='#3F51B5')
        self.style.configure('Header.TLabel', background='#3F51B5', foreground='white', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Treeview', font=('Segoe UI', 10), rowheight=25, fieldbackground='#FFFFFF')
        self.style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), background='#607D8B',
                             foreground='white')
        self.style.map('Treeview', background=[('selected', '#CFD8DC')])

    def create_ui(self):
        header_frame = ttk.Frame(self.root, style='Header.TFrame')
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="To-Do List Manager", style='Header.TLabel').pack(pady=15)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)

        self.task_entry = ttk.Entry(input_frame, width=40, font=('Segoe UI', 10))
        self.task_entry.grid(row=0, column=0, padx=5, sticky='ew')
        self.task_entry.bind('<Return>', lambda event: self.add_task())
        self.task_entry.bind('<Escape>', lambda event: self.clear_inputs())

        self.cal = DateEntry(input_frame, date_pattern='dd-mm-yyyy', font=('Segoe UI', 10), style='Calendar.DateEntry')
        self.cal.grid(row=0, column=1, padx=5)
        self.cal.set_date(date.today())

        self.priority_combo = ttk.Combobox(input_frame, values=["Low", "Medium", "High"], width=12,
                                           font=('Segoe UI', 10), style='Priority.Medium.TCombobox')
        self.priority_combo.grid(row=0, column=2, padx=5)
        self.priority_combo.set("Medium")
        self.priority_combo.bind("<<ComboboxSelected>>", self.update_priority_style)
        self.update_priority_style()

        add_button = ttk.Button(input_frame, text="➕ Add Task", command=self.add_task, style='TButton')
        add_button.grid(row=0, column=3, padx=5)

        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, pady=10)

        self.search_entry = ttk.Entry(controls_frame, width=30, font=('Segoe UI', 10))
        self.search_entry.grid(row=0, column=0, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.update_treeview())
        self.search_entry.bind('<Escape>', lambda e: self.search_entry.delete(0, tk.END))

        self.filter_combo = ttk.Combobox(controls_frame, values=["All", "Completed", "Pending"], width=15,
                                         font=('Segoe UI', 10), style='Filter.TCombobox')
        self.filter_combo.grid(row=0, column=1, padx=5)
        self.filter_combo.set("All")
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_treeview())

        search_button = ttk.Button(controls_frame, text="🔍 Search", command=self.update_treeview, style='TButton')
        search_button.grid(row=0, column=2, padx=5)

        remove_button = ttk.Button(controls_frame, text="🗑️ Remove Selected", command=self.remove_task)
        remove_button.grid(row=0, column=3, padx=5)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('task', 'deadline', 'priority', 'completed')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview')
        col_widths = {'task': 300, 'deadline': 120, 'priority': 100, 'completed': 80}
        for col in columns:
            self.tree.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_tasks(c))
            self.tree.column(col, width=col_widths[col], anchor='center')
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.edit_task)
        self.tree.bind('<Delete>', lambda e: self.remove_task())

        self.status_bar = ttk.Label(self.root, relief=tk.FLAT, background='#CFD8DC', foreground='#37474F',
                                    font=('Segoe UI', 9), padding=5)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.bind('<Enter>', self.show_status_tooltip)
        self.status_bar.bind('<Leave>', self.hide_status_tooltip)

    def update_priority_style(self, event=None):
        priority = self.priority_combo.get()
        style_mapping = {
            'Low': 'Priority.Low.TCombobox',
            'Medium': 'Priority.Medium.TCombobox',
            'High': 'Priority.High.TCombobox'
        }
        self.priority_combo.configure(style=style_mapping[priority])

    def save_tasks(self):
        try:
            with open('tasks.json', 'w') as f:
                json.dump(self.tasks, f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tasks: {str(e)}")

    def load_tasks(self):
        try:
            with open('tasks.json', 'r') as f:
                self.tasks = json.load(f)
            self.sort_tasks(self.sort_column)
            self.update_treeview()
        except FileNotFoundError:
            self.tasks = []
            self.update_treeview()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Corrupted tasks file. Starting with empty tasks.")
            self.tasks = []
            self.update_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
            self.tasks = []
            self.update_treeview()

    # function to sort the tasks according to deadline
    def sort_tasks(self, column):
        if self.sort_column == column:
            self.sort_order = not self.sort_order
        else:
            self.sort_column = column
            self.sort_order = True
        reverse = not self.sort_order

        if column == 'deadline':
            key_func = lambda x: datetime.strptime(x['deadline'], "%d-%m-%Y")
        elif column == 'priority':
            priority_order = {'Low': 1, 'Medium': 2, 'High': 3}
            key_func = lambda x: priority_order[x['priority']]
        elif column == 'completed':
            key_func = lambda x: x['completed']
        else:
            key_func = lambda x: x['task'].lower()

        self.tasks.sort(key=key_func, reverse=reverse)
        self.update_treeview()

    def update_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        current_filter = self.filter_combo.get()
        search_query = self.search_entry.get().strip().lower()

        for task in self.tasks:
            # Apply filter
            if current_filter == "Completed" and not task['completed']:
                continue
            if current_filter == "Pending" and task['completed']:
                continue

            # Apply search
            if search_query:
                # Search in task text, deadline, and priority
                if (search_query not in task['task'].lower() and
                        search_query not in task['deadline'].lower() and
                        search_query not in task['priority'].lower()):
                    continue

            completed = 'Yes' if task['completed'] else 'No'
            self.tree.insert('', 'end', values=(
                task['task'],
                task['deadline'],
                task['priority'],
                completed
            ))

    def clear_inputs(self):
        self.task_entry.delete(0, tk.END)
        self.cal.set_date(date.today())
        self.priority_combo.set("Medium")
        self.update_priority_style()

    # function to remove tasks
    def remove_task(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No task selected!")
            return

        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected task(s)?"):
            return

        tasks_to_remove = []
        for item in selected_items:
            item_values = self.tree.item(item, 'values')
            task_text = item_values[0]
            deadline = item_values[1]
            priority = item_values[2]
            completed_str = item_values[3]
            completed = completed_str == 'Yes'

            for task in self.tasks:
                if (task['task'] == task_text and
                        task['deadline'] == deadline and
                        task['priority'] == priority and
                        task['completed'] == completed):
                    tasks_to_remove.append(task)
                    break

        # Remove the found tasks from the main list
        for task in tasks_to_remove:
            self.tasks.remove(task)

        self.save_tasks()
        self.update_treeview()
        self.update_status()

    def edit_task(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = selected_item[0]
        item_values = self.tree.item(item, 'values')

        task_text = item_values[0]
        deadline = item_values[1]
        priority = item_values[2]
        completed_str = item_values[3]
        completed = completed_str == 'Yes'

        selected_task_index = -1
        for index, task in enumerate(self.tasks):
            if (task['task'] == task_text and
                    task['deadline'] == deadline and
                    task['priority'] == priority and
                    task['completed'] == completed):
                selected_task_index = index
                break

        if selected_task_index == -1:
            return

        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Task")
        edit_dialog.geometry("400x300")
        edit_dialog.transient(self.root)  # Make dialog transient
        edit_dialog.grab_set()  # Make dialog modal

        # Center the dialog
        edit_dialog.update_idletasks()
        width = edit_dialog.winfo_width()
        height = edit_dialog.winfo_height()
        x = (edit_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_dialog.winfo_screenheight() // 2) - (height // 2)
        edit_dialog.geometry(f'{width}x{height}+{x}+{y}')

        ttk.Label(edit_dialog, text="Task:").pack(pady=5)
        task_entry = ttk.Entry(edit_dialog, width=40)
        task_entry.insert(0, self.tasks[selected_task_index]['task'])
        task_entry.pack(pady=5)
        task_entry.focus_set()  # Set focus to task entry

        ttk.Label(edit_dialog, text="Deadline:").pack(pady=5)
        cal = DateEntry(edit_dialog, date_pattern='dd-mm-yyyy')
        cal.set_date(datetime.strptime(self.tasks[selected_task_index]['deadline'], "%d-%m-%Y"))
        cal.pack(pady=5)

        ttk.Label(edit_dialog, text="Priority:").pack(pady=5)
        priority_combo = ttk.Combobox(edit_dialog, values=["Low", "Medium", "High"])
        priority_combo.set(self.tasks[selected_task_index]['priority'])
        priority_combo.pack(pady=5)

        completed_var = tk.BooleanVar(value=self.tasks[selected_task_index]['completed'])
        ttk.Checkbutton(edit_dialog, text="Completed", variable=completed_var).pack(pady=5)

        def save_edits():
            new_task = task_entry.get().strip()
            new_deadline = cal.get_date().strftime("%d-%m-%Y")
            new_priority = priority_combo.get()
            new_completed = completed_var.get()

            if not new_task:
                messagebox.showerror("Error", "Task cannot be empty!")
                return

            self.tasks[selected_task_index].update({
                'task': new_task,
                'deadline': new_deadline,
                'priority': new_priority,
                'completed': new_completed
            })

            self.save_tasks()
            self.update_treeview()
            self.update_status()
            edit_dialog.destroy()

        def on_cancel():
            edit_dialog.destroy()

        button_frame = ttk.Frame(edit_dialog)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Save Changes", command=save_edits).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)

        # Bind Enter key to save
        edit_dialog.bind('<Return>', lambda e: save_edits())
        # Bind Escape key to cancel
        edit_dialog.bind('<Escape>', lambda e: on_cancel())

    def update_status(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task['completed'])
        pending = total - completed
        self.status_bar.config(text=f"Total Tasks: {total} | Completed: {completed} | Pending: {pending}")

    def show_status_tooltip(self, event):
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        label = ttk.Label(self.tooltip,
                          text="Press Ctrl+S to save, Ctrl+N for new task,\nCtrl+F to search, Delete to remove task",
                          background='#333333', foreground='white', padding=5)
        label.pack()

    def hide_status_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            delattr(self, 'tooltip')


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()