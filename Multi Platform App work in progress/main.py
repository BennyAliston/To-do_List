import flet as ft
import json
import os
import uuid
from datetime import date, datetime

class Task(ft.Column):
    def __init__(self, app, task_id, task_text, deadline, priority, completed):
        super().__init__()
        self.app = app
        self.task_id = task_id
        self.task_text = task_text
        self.deadline = deadline
        self.priority = priority
        self.completed = completed
        self.edit_mode = False

        # Priority Colors
        priority_colors = {
            "High": ft.Colors.RED_400,
            "Medium": ft.Colors.ORANGE_400,
            "Low": ft.Colors.GREEN_400
        }
        
        self.checkbox = ft.Checkbox(
            value=self.completed, 
            label="", 
            on_change=self.toggle_complete
        )
        
        self.text_view = ft.Text(
            spans=[ft.TextSpan(
                text=self.task_text,
                style=ft.TextStyle(
                    decoration=ft.TextDecoration.LINE_THROUGH if self.completed else ft.TextDecoration.NONE
                )
            )],
            expand=True,
            style=ft.TextThemeStyle.BODY_LARGE
        )
        
        self.deadline_view = ft.Text(
            value=self.deadline,
            width=100,
            color=ft.Colors.GREY_500
        )
        
        self.priority_view = ft.Text(
            value=self.priority,
            width=80,
            color=priority_colors.get(self.priority, ft.Colors.BLACK),
            weight=ft.FontWeight.BOLD
        )

        # Edit Controls
        self.edit_text = ft.TextField(value=self.task_text, expand=True)
        self.edit_deadline = ft.TextField(value=self.deadline, width=100)
        self.edit_priority = ft.Dropdown(
            value=self.priority,
            width=100,
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ]
        )

        # Buttons
        self.edit_button = ft.IconButton(icon=ft.Icons.EDIT, on_click=self.edit_clicked, tooltip="Edit")
        self.delete_button = ft.IconButton(icon=ft.Icons.DELETE, on_click=self.delete_clicked, tooltip="Delete")
        self.save_button = ft.IconButton(icon=ft.Icons.CHECK, on_click=self.save_clicked, tooltip="Save")
        self.cancel_button = ft.IconButton(icon=ft.Icons.CLOSE, on_click=self.cancel_clicked, tooltip="Cancel")

        self.display_view = ft.Row(
            controls=[
                self.checkbox,
                self.text_view,
                self.deadline_view,
                self.priority_view,
                self.edit_button,
                self.delete_button
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.edit_view = ft.Row(
            visible=False,
            controls=[
                self.edit_text,
                self.edit_deadline,
                self.edit_priority,
                self.save_button,
                self.cancel_button
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.controls = [self.display_view, self.edit_view]

    def toggle_complete(self, e):
        self.completed = self.checkbox.value
        self.text_view.spans[0].style.decoration = ft.TextDecoration.LINE_THROUGH if self.completed else ft.TextDecoration.NONE
        self.text_view.update()
        self.app.update_task_data(self.task_id, {'completed': self.completed})

    def edit_clicked(self, e):
        self.edit_mode = True
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.task_text = self.edit_text.value
        self.deadline = self.edit_deadline.value
        self.priority = self.edit_priority.value
        
        self.text_view.spans[0].text = self.task_text
        self.deadline_view.value = self.deadline
        self.priority_view.value = self.priority
        
        # Update Color based on new priority
        priority_colors = {"High": ft.Colors.RED_400, "Medium": ft.Colors.ORANGE_400, "Low": ft.Colors.GREEN_400}
        self.priority_view.color = priority_colors.get(self.priority, ft.Colors.BLACK)

        self.app.update_task_data(self.task_id, {
            'task': self.task_text,
            'deadline': self.deadline,
            'priority': self.priority
        })
        
        self.edit_mode = False
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def cancel_clicked(self, e):
        self.edit_text.value = self.task_text
        self.edit_deadline.value = self.deadline
        self.edit_priority.value = self.priority
        self.edit_mode = False
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def delete_clicked(self, e):
        self.app.delete_task(self)

class TodoApp(ft.Column):
    def __init__(self):
        super().__init__()
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.json')
        self.tasks = []
        self.load_tasks()

        # Header
        self.new_task = ft.TextField(hint_text="What needs to be done?", expand=True)
        self.new_deadline = ft.TextField(hint_text="DD-MM-YYYY", width=120, value=date.today().strftime("%d-%m-%Y"))
        self.new_priority = ft.Dropdown(
            width=100,
            value="Medium",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ]
        )

        self.add_btn = ft.FloatingActionButton(
            icon=ft.Icons.ADD, on_click=self.add_clicked, bgcolor=ft.Colors.BLUE_500
        )

        self.filter_tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[
                ft.Tab(text="All"),
                ft.Tab(text="Active"),
                ft.Tab(text="Completed"),
            ],
        )
        
        # We need a reference to modify items_left later
        self.items_left = ft.Text("0 items left")
        
        self.task_list = ft.ListView(expand=True, spacing=10)

        # Initial Render
        self.update_list()

        # Build the View Controls
        self.controls = [
            ft.Row([ft.Text(value="To-Do List Manager", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(
                controls=[self.new_task, self.new_deadline, self.new_priority, self.add_btn],
            ),
            ft.Column(
                spacing=20,
                controls=[
                    self.filter_tabs,
                    self.task_list,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                text="Clear Completed", on_click=self.clear_clicked
                            ),
                        ],
                    ),
                ],
                expand=True,
            ),
        ]
        self.expand = True

    def add_clicked(self, e):
        if not self.new_task.value:
            return
        
        task_data = {
            'id': str(uuid.uuid4()),
            'task': self.new_task.value,
            'deadline': self.new_deadline.value,
            'priority': self.new_priority.value,
            'completed': False
        }
        self.tasks.append(task_data)
        self.save_tasks()
        self.new_task.value = ""
        self.update_list()
        self.update()

    def update_task_data(self, task_id, updates):
        for task in self.tasks:
            if task['id'] == task_id:
                task.update(updates)
                break
        self.save_tasks()
        self.update_count()

    def delete_task(self, task_control):
        self.tasks = [t for t in self.tasks if t['id'] != task_control.task_id]
        self.save_tasks()
        self.update_list()
        self.update()

    def tabs_changed(self, e):
        self.update_list()
        self.update()

    def clear_clicked(self, e):
        self.tasks = [t for t in self.tasks if not t['completed']]
        self.save_tasks()
        self.update_list()
        self.update()

    def update_list(self):
        status = self.filter_tabs.tabs[self.filter_tabs.selected_index].text
        self.task_list.controls.clear()
        
        for task in self.tasks:
            if status == "All":
                visible = True
            elif status == "Active":
                visible = not task.get('completed', False)
            elif status == "Completed":
                visible = task.get('completed', False)
            else:
                visible = True
            
            if visible:
                t = Task(
                    self,
                    task['id'],
                    task['task'],
                    task.get('deadline', ''),
                    task.get('priority', 'Medium'),
                    task.get('completed', False)
                )
                self.task_list.controls.append(t)
        self.update_count()

    def update_count(self):
        count = sum(1 for t in self.tasks if not t.get('completed', False))
        self.items_left.value = f"{count} items left"
        if hasattr(self.items_left, 'page') and self.items_left.page:
            self.items_left.update()

    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = []
        else:
             self.tasks = []

    def save_tasks(self):
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=4)

def main(page: ft.Page):
    page.title = "To-Do App"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.LIGHT # Default

    # Theme Toggle
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        e.control.icon = ft.Icons.DARK_MODE if page.theme_mode == ft.ThemeMode.LIGHT else ft.Icons.LIGHT_MODE
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        on_click=toggle_theme,
        tooltip="Toggle Theme"
    )
    
    page.appbar = ft.AppBar(
        title=ft.Text("To-Do Manager"),
        center_title=False,

        actions=[theme_btn]
    )

    app = TodoApp()
    page.add(app)

if __name__ == "__main__":
    ft.app(target=main)