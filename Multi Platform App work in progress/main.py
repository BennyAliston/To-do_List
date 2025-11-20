import json
import os
import uuid
from datetime import datetime, date

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty, DictProperty
from kivy.uix.popup import Popup
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.button import Button
# ButtonBehavior is no longer needed for TaskItem
from kivy.uix.behaviors import ButtonBehavior 

# Set window size
Window.size = (1000, 700)
Window.minimum_width = 800
Window.minimum_height = 600

# --- Custom Popup for Editing Tasks ---
class EditTaskPopup(Popup):
    task_id = StringProperty('')
    task_text = StringProperty('')
    deadline_text = StringProperty('')
    priority_text = StringProperty('')
    app = ObjectProperty(None)

    def save_changes(self, new_text, new_deadline, new_priority):
        if not new_text.strip():
            self.ids.error_label.text = "Task description cannot be empty."
            return
        
        try:
            if new_deadline.strip():
                datetime.strptime(new_deadline.strip(), "%d-%m-%Y")
        except ValueError:
            self.ids.error_label.text = "Invalid date format. Use DD-MM-YYYY."
            return

        updates = {
            'task': new_text.strip(),
            'deadline': new_deadline.strip(),
            'priority': new_priority
        }
        self.app.update_task(self.task_id, updates)
        self.dismiss()

# --- Custom Hover Behavior and Button ---
class HoverBehavior(object):
    is_hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if not self.is_hovered:
                self.is_hovered = True
        else:
            if self.is_hovered:
                self.is_hovered = False

class HoverButton(Button, HoverBehavior):
    bg_color = ListProperty([0, 0, 0, 1])
    hover_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]

# --- TaskItem with Corrected Click Handling ---
class TaskItem(RecycleDataViewBehavior, HoverBehavior, BoxLayout): # No more ButtonBehavior
    # --- Properties ---
    task_id = StringProperty('')
    task = StringProperty('')
    deadline = StringProperty('')
    priority = StringProperty('')
    completed = BooleanProperty(False)
    selected = BooleanProperty(False)
    app = ObjectProperty(None)
    index = 0

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        for key, value in data.items():
            setattr(self, key, value)
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        # This method now correctly handles clicks on the TaskItem
        if self.collide_point(*touch.pos):
            # Check if the click is on the "Edit" button or the CheckBox
            # self.children are in reverse visual order. [0] is the right-most widget (Edit)
            # [-1] is the left-most widget (CheckBox)
            if self.children[0].collide_point(*touch.pos) or self.children[-1].collide_point(*touch.pos):
                # If the click is on a child button, let the child handle it and do nothing here.
                return super().on_touch_down(touch)
            
            # If the click is on the main body of the item, process it for selection.
            touch.grab(self)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            # This was a click on the main body, so we toggle selection.
            self.selected = not self.selected
            self.app.update_task(self.task_id, {'selected': self.selected})
            return True
        return super().on_touch_up(touch)

    def toggle_complete(self, active):
        # This is called by the CheckBox's on_active event in the .kv file
        if self.app:
            self.app.update_task(self.task_id, {'completed': active})

    def edit_task(self):
        # This is called by the "Edit" button
        if not self.app: return
        popup = EditTaskPopup(
            app=self.app, task_id=self.task_id, task_text=self.task,
            deadline_text=self.deadline, priority_text=self.priority
        )
        popup.open()


# --- Main Layout ---
class TodoLayout(BoxLayout):
    app = ObjectProperty(None)
    current_filter = StringProperty('All')
    theme = StringProperty('Light')
    theme_colors = DictProperty({
        'Light': {
            'background': [0.96, 0.97, 0.98, 1], 'surface': [1, 1, 1, 1],
            'primary': [0.12, 0.45, 0.67, 1], 'primary_light': [0.4, 0.65, 0.84, 1],
            'text_primary': [0.07, 0.08, 0.09, 1], 'text_secondary': [0.4, 0.4, 0.4, 1],
            'on_primary': [1, 1, 1, 1], 'danger': [0.85, 0.22, 0.22, 1],
            'danger_light': [0.95, 0.35, 0.35, 1], 'selected': [0.9, 0.95, 1, 1]
        },
        'Dark': {
            'background': [0.08, 0.09, 0.11, 1], 'surface': [0.12, 0.14, 0.17, 1],
            'primary': [0.22, 0.55, 0.77, 1], 'primary_light': [0.4, 0.65, 0.84, 1],
            'text_primary': [0.95, 0.95, 0.95, 1], 'text_secondary': [0.6, 0.6, 0.6, 1],
            'on_primary': [1, 1, 1, 1], 'danger': [0.75, 0.2, 0.2, 1],
            'danger_light': [0.85, 0.3, 0.3, 1], 'selected': [0.15, 0.2, 0.3, 1]
        }
    })

    def add_task_ui(self):
        task_text = self.ids.task_input.text.strip()
        deadline_str = self.ids.deadline_input.text.strip()
        priority = self.ids.priority_spinner.text

        if not task_text: return
        
        if not deadline_str:
            deadline_str = date.today().strftime("%d-%m-%Y")
        else:
            try:
                datetime.strptime(deadline_str, "%d-%m-%Y")
            except ValueError:
                print("Invalid date format. Please use DD-MM-YYYY.")
                return

        self.app.add_task(task_text, deadline_str, priority)
        self.ids.task_input.text = ''
        self.ids.deadline_input.text = ''
        self.ids.priority_spinner.text = 'Medium'

    def apply_filter(self, filter_value):
        self.current_filter = filter_value
        self.app.update_ui()

    def search_tasks(self, search_text):
        self.app.update_ui(search_text)

    def remove_selected(self):
        self.app.remove_selected_tasks()

# --- Main App Class ---
class TodoApp(App):
    tasks = ListProperty([])
    tasks_file = StringProperty('tasks.json')

    def build(self):
        self.title = 'To-Do List Manager'
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.json')
        self.load_tasks()
        Builder.load_file('main.kv')
        return TodoLayout(app=self)

    def on_start(self):
        self.update_ui()

    def update_ui(self, search_text=''):
        if not self.root: return

        filtered_tasks = self.tasks
        
        if search_text:
            filtered_tasks = [t for t in filtered_tasks if search_text.lower() in t['task'].lower()]

        filter_val = self.root.current_filter
        if filter_val != 'All':
            if filter_val == 'Completed':
                filtered_tasks = [t for t in filtered_tasks if t.get('completed', False)]
            elif filter_val == 'Pending':
                filtered_tasks = [t for t in filtered_tasks if not t.get('completed', False)]
            elif filter_val in ['High', 'Medium', 'Low']:
                filtered_tasks = [t for t in filtered_tasks if t.get('priority', 'Medium') == filter_val]
        
        self.root.ids.task_list.data = [{**task, 'app': self} for task in filtered_tasks]
        
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.get('completed', False))
        self.root.ids.status_bar.text = f"Total: {total}  |  Completed: {completed}  |  Pending: {total - completed}"

    def load_tasks(self):
        try:
            if os.path.exists(self.tasks_file):
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            if not self.tasks:
                self.tasks.append({
                    'id': str(uuid.uuid4()), 'task': 'This is a sample task!',
                    'deadline': date.today().strftime("%d-%m-%Y"), 'priority': 'High',
                    'completed': False, 'selected': False
                })
        except Exception as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []

    def save_tasks(self):
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                tasks_to_save = [{k: v for k, v in task.items() if k != 'app'} for task in self.tasks]
                json.dump(tasks_to_save, f, indent=4)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, task_text, deadline_str, priority):
        new_task = {
            'id': str(uuid.uuid4()), 'task': task_text, 'deadline': deadline_str,
            'priority': priority, 'completed': False, 'selected': False
        }
        self.tasks.append(new_task)
        self.save_tasks()
        self.update_ui()

    def update_task(self, task_id, updates):
        for task in self.tasks:
            if task.get('id') == task_id:
                task.update(updates)
                break
        self.save_tasks()
        self.update_ui()

    def remove_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.get('id') != task_id]
        self.save_tasks()
        self.update_ui()

    def remove_selected_tasks(self):
        self.tasks = [t for t in self.tasks if not t.get('selected', False)]
        self.save_tasks()
        self.update_ui()

if __name__ == "__main__":
    TodoApp().run()