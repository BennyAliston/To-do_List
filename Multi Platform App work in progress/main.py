import flet as ft
import json
import os
import uuid
import asyncio
from datetime import date, datetime


# Neubrutal Design Constants
NB_BORDER = ft.border.all(2, ft.Colors.BLACK)
NB_SHADOW = ft.BoxShadow(spread_radius=0, blur_radius=0, color=ft.Colors.BLACK, offset=ft.Offset(4, 4))
NB_BG_COLOR = "#F0F0EB"
NB_ITEM_BG = ft.Colors.WHITE
NB_FONT_WEIGHT = ft.FontWeight.BOLD

LIGHT_THEME = {
    "page_bg": "#FFEBEE", # Light Pink/Pastel for a warmer cartoon feel
    "container_bg": "#FFFFFF", # Pure White for inputs
    "item_bg": "#FFFFFF",
    "text_color": ft.Colors.BLACK,
    "border_color": ft.Colors.BLACK,
    "shadow_color": ft.Colors.BLACK
}

DARK_THEME = {
    "page_bg": "#121212", 
    "container_bg": "#1E1E1E",
    "item_bg": "#2D2D2D",
    "text_color": "#FFFFFF",
    "border_color": "#FFFFFF",
    "shadow_color": "#000000" # Black shadow on dark cards looks better/grounded
}

class Task(ft.Container): # Changed from Column to Container for styling
    def __init__(self, app, task_id, task_text, deadline, priority, completed):
        super().__init__()
        self.app = app
        self.task_id = task_id
        self.task_text = task_text
        self.deadline = deadline
        self.priority = priority
        self.completed = completed
        self.edit_mode = False
        
        self.border = NB_BORDER
        self.shadow = NB_SHADOW
        self.bgcolor = NB_ITEM_BG
        self.border_radius = 5
        self.padding = 10
        self.margin = ft.margin.only(bottom=10)
        self.animate_opacity = 300 # Enable fading animation

        # Priority Colors
        self.get_priority_color = lambda p: {
            "High": ft.Colors.RED_ACCENT,
            "Medium": ft.Colors.AMBER,
            "Low": ft.Colors.BLUE
        }.get(p, ft.Colors.BLUE)

        # Affordance: Enlarge checkbox and simple container wrapper not needed if we scale
        self.checkbox = ft.Checkbox(
            value=self.completed, 
            label="", 
            on_change=self.toggle_complete,
            col={"xs": 2, "md": 1},
            fill_color=ft.Colors.BLACK,
            scale=1.5 # Enlarged
        )
        
        self.text_control = ft.Text(
            spans=[ft.TextSpan(text=self.task_text, style=ft.TextStyle(decoration=ft.TextDecoration.LINE_THROUGH if self.completed else ft.TextDecoration.NONE))],
            color=ft.Colors.BLACK,
            size=16,
            weight=ft.FontWeight.BOLD,
            no_wrap=True,
            overflow=ft.TextOverflow.ELLIPSIS
        )
        # Affordance: Clickable text area
        self.text_view = ft.Container(
            content=self.text_control,
            col={"xs": 10, "md": 5},
            on_click=self.toggle_complete
        )
        
        self.deadline_view = ft.Text(
            value=self.deadline,
            # width=100, # Removed fixed width for responsiveness
            color=ft.Colors.GREY_500,
            col={"xs": 4, "md": 2}
        )
        
        # Priority Chip
        self.priority_text = ft.Text(value=self.priority, size=12, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
        self.priority_view = ft.Container(
            content=self.priority_text,
            bgcolor=self.get_priority_color(self.priority),
            border=NB_BORDER,
            border_radius=20,
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            col={"xs": 4, "md": 2},
            alignment=ft.alignment.center
        )

        # Edit Controls
        self.edit_text = ft.TextField(value=self.task_text, col={"xs": 12, "md": 6}) # expand handled by col in ResponsiveRow
        self.edit_deadline = ft.TextField(
            value=self.deadline, 
            col={"xs": 4, "md": 3},
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.app.pick_date(self.edit_deadline)
        )
        self.edit_priority = ft.Dropdown(
            value=self.priority,
            col={"xs": 4, "md": 2},
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ]
        )

        # Buttons
        self.edit_button = ft.IconButton(icon=ft.Icons.EDIT, icon_color=ft.Colors.BLACK, on_click=self.edit_clicked, tooltip="Edit")
        self.delete_button = ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.RED_900, on_click=self.delete_clicked, tooltip="Delete")
        self.save_button = ft.IconButton(icon=ft.Icons.CHECK, icon_color=ft.Colors.GREEN_900, on_click=self.save_clicked, tooltip="Save")
        self.cancel_button = ft.IconButton(icon=ft.Icons.CLOSE, icon_color=ft.Colors.RED_900, on_click=self.cancel_clicked, tooltip="Cancel")
        
        self.display_view = ft.ResponsiveRow(
            controls=[
                self.checkbox,
                self.text_view,
                self.deadline_view,
                self.priority_view,
                ft.Row([self.edit_button, self.delete_button], col={"xs": 4, "md": 1}, alignment=ft.MainAxisAlignment.END, spacing=0)
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.edit_view = ft.ResponsiveRow(
            visible=False,
            controls=[
                self.edit_text,
                self.edit_deadline,
                self.edit_priority,
                ft.Row([self.save_button, self.cancel_button], col={"xs": 4, "md": 1}, alignment=ft.MainAxisAlignment.END, spacing=0)
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.content = ft.Column(controls=[self.display_view, self.edit_view]) # Container content

    def update_theme(self, theme):
        self.bgcolor = theme["item_bg"]
        self.border = ft.border.all(2, theme["border_color"])
        self.shadow.color = theme["shadow_color"]
        self.text_control.color = theme["text_color"]
        self.priority_text.color = ft.Colors.BLACK # Chips stay black text usually? Or should vary? kept black as chips are colored.
        # Checkbox fill
        self.checkbox.fill_color = theme["text_color"]
        
        # update icons
        icon_color = theme["text_color"]
        self.edit_button.icon_color = icon_color
        
        self.update()

    def toggle_complete(self, e):
        self.completed = not self.completed if e.control != self.checkbox else self.checkbox.value
        self.checkbox.value = self.completed
        self.text_control.spans[0].style.decoration = ft.TextDecoration.LINE_THROUGH if self.completed else ft.TextDecoration.NONE
        self.checkbox.update()
        self.text_control.update()
        self.app.update_task_data(self.task_id, {'completed': self.completed})
        
        msg = "Task marked completed!" if self.completed else "Task marked active!"
        if self.page:
            self.page.open(ft.SnackBar(ft.Text(msg), duration=1000))

    def edit_clicked(self, e):
        self.edit_mode = True
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def delete_clicked(self, e):
        self.app.delete_task(self)

    def save_clicked(self, e):
        self.task_text = self.edit_text.value
        self.deadline = self.edit_deadline.value
        self.priority = self.edit_priority.value
        
        self.text_control.spans[0].text = self.task_text
        self.text_control.update()
        self.deadline_view.value = self.deadline
        self.priority_text.value = self.priority
        self.priority_view.bgcolor = self.get_priority_color(self.priority)
        self.priority_view.update()

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
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.json')
        self.tasks = []
        self.load_tasks()
        
        # DatePicker placeholder - will be set by main
        self.date_picker = None
        self.is_dark = False # Track theme state

        # Header
        self.new_task = ft.TextField(
            hint_text="What needs to be done?", 
            col={"xs": 12, "md": 6},
            border_color=ft.Colors.BLACK,
            border_width=2,
            border_radius=0,
            text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
        )
        self.new_deadline = ft.TextField(
            hint_text="DD-MM-YYYY", 
            value=date.today().strftime("%d-%m-%Y"), 
            col={"xs": 5, "md": 3},
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda e: self.pick_date(self.new_deadline),
            border_color=ft.Colors.BLACK,
            border_width=2,
            border_radius=0
        )
        self.new_priority = ft.Dropdown(
            col={"xs": 4, "md": 2},
            value="Medium",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            border_color=ft.Colors.BLACK,
            border_width=2,
            border_radius=0
        )

        self.add_btn = ft.Container(
            content=ft.Icon(name=ft.Icons.ADD, color=ft.Colors.BLACK), # Changed inner content to Icon (not IconButton)
            bgcolor=ft.Colors.CYAN_ACCENT_400,
            border=ft.border.all(2, ft.Colors.BLACK),
            border_radius=0,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=0, color=ft.Colors.BLACK, offset=ft.Offset(4, 4)),
            on_click=self.add_clicked
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
        self.app_title = ft.Text(value="HABITO-DO", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)
        self.input_container = ft.Container(
                content=ft.ResponsiveRow(
                    controls=[
                        self.new_task, 
                        self.new_deadline, 
                        self.new_priority, 
                        ft.Container(content=self.add_btn, col={"xs": 3, "md": 1}, alignment=ft.alignment.center_right)
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                ),
                padding=15, 
                bgcolor=ft.Colors.WHITE,
                border=NB_BORDER,
                shadow=NB_SHADOW,
                margin=ft.margin.only(bottom=40) # Increased margin for breathing room
            )
            
        self.controls = [
            ft.Container(
                content=ft.Row([self.app_title], alignment=ft.MainAxisAlignment.CENTER),
                padding=20
            ),
            self.input_container,
            ft.Column(
                spacing=10, # Reduced spacing as items have margin
                controls=[
                    self.filter_tabs,
                    self.task_list,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self.items_left,
                            ft.OutlinedButton(
                                text="Clear Completed", on_click=self.clear_completed_clicked
                            ),
                        ],
                    ),
                ],
                expand=True,
            ),
        ]
        self.expand = True

    def update_theme_mode(self, is_dark):
        self.is_dark = is_dark # Update state
        theme = DARK_THEME if is_dark else LIGHT_THEME
        
        # Update Page
        if self.page:
            self.page.bgcolor = theme["page_bg"]
            self.page.update()
            
        # Update App Title
        self.app_title.color = theme["text_color"]
        
        # Update Input Container
        self.input_container.bgcolor = theme["container_bg"]
        self.input_container.border = ft.border.all(2, theme["border_color"])
        self.input_container.shadow.color = theme["shadow_color"]
        
        # Update Inputs
        input_border_color = theme["border_color"]
        self.new_task.border_color = input_border_color
        self.new_deadline.border_color = input_border_color
        self.new_priority.border_color = input_border_color
        self.new_task.text_style.color = theme["text_color"]
        self.new_task.update()
        self.new_deadline.update()
        self.new_priority.update()
        
        # Update Add Button
        self.add_btn.border = ft.border.all(2, theme["border_color"])
        self.add_btn.shadow.color = theme["shadow_color"]
        self.add_btn.update()
        
        # Update Tasks
        for control in self.task_list.controls:
            if isinstance(control, Task):
                control.update_theme(theme)
                
        self.update()

    def pick_date(self, target_control):
        if self.date_picker:
            self.current_date_target = target_control
            self.page.open(self.date_picker)

    def on_date_change(self, e):
        if self.current_date_target and self.date_picker:
            self.current_date_target.value = self.date_picker.value.strftime("%d-%m-%Y")
            self.current_date_target.update()
            self.current_date_target = None

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
        if self.page:
            self.page.open(ft.SnackBar(ft.Text("Task deleted!"), duration=1000))
            self.page.update()

    def tabs_changed(self, e):
        self.update_list()
        self.update()

    def clear_completed_clicked(self, e):
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
                if self.is_dark:
                   t.update_theme(DARK_THEME) # Apply dark theme if active
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
    page.title = "Habito-do"
    # horizontal_alignment=STRETCH is crucial for ResponsiveRow to have width inside the implicit Page column
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH 
    # page.scroll = ft.ScrollMode.ADAPTIVE # Removed to allow ListView to expand
    page.theme_mode = ft.ThemeMode.LIGHT # Fast switch
    page.bgcolor = "#E6E6FA" # Lavenderish background mainly
    page.padding = 20
    page.window_icon = "icon.png" # Set App Icon

    # Theme Toggle
    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        is_dark = page.theme_mode == ft.ThemeMode.DARK
        e.control.icon = ft.Icons.DARK_MODE if not is_dark else ft.Icons.LIGHT_MODE
        app.update_theme_mode(is_dark) # Propagate theme change
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.DARK_MODE,
        on_click=toggle_theme,
        tooltip="Toggle Theme"
    )
    
    page.appbar = ft.AppBar(
        title=ft.Text("Habito-do"),
        center_title=False,

        actions=[theme_btn]
    )

    app = TodoApp()
    
    # Initialize DatePicker and attach to app
    date_picker = ft.DatePicker(
        on_change=app.on_date_change,
        first_date=datetime(2020, 1, 1),
        last_date=datetime(2030, 12, 31),
    )
    page.overlay.append(date_picker)
    app.date_picker = date_picker
    
    page.add(app)
    page.update()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")