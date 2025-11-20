import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from tkcalendar import DateEntry
import json
import uuid
import os

class TodoApp:
    def __init__(self, root):
        """Initialize the main application window and setup basic configurations"""
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("800x600")  # Set initial window size
        self.style = ttk.Style()  # Create style object for theming

        # Define path for tasks storage file
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.json')
        self.is_first_run = not os.path.exists(self.tasks_file)  # Check if this is first time running

        # Define color themes for the application
        self.themes = {
            # Light Theme - Modern and clean look
            'Light': {
                'bg': '#F8FAFC',
                'fg': '#334155',
                'header_bg': '#1E293B',
                'header_fg': '#F8FAFC',
                'button_bg': '#3B82F6',
                'button_fg': '#FFFFFF',
                'tree_bg': '#FFFFFF',
                'tree_fg': '#334155',
                'tree_heading_bg': '#1E293B',
                'tree_heading_fg': '#F8FAFC',
                'tree_selected_bg': '#BFDBFE',
                'status_bg': '#F1F5F9',
                'status_fg': '#334155',
                'entry_bg': '#FFFFFF',
                'entry_fg': '#334155',
                'entry_select_bg': '#BFDBFE',
                'entry_select_fg': '#334155',
                'border_color': '#E2E8F0',
                'hover_bg': '#EFF6FF',
                'active_bg': '#DBEAFE',
                'calendar_bg': '#FFFFFF',
                'calendar_fg': '#334155',
                'calendar_header_bg': '#1E293B',
                'calendar_header_fg': '#F8FAFC',
                'calendar_select_bg': '#3B82F6',
                'calendar_select_fg': '#FFFFFF',
                'calendar_weekend_bg': '#F1F5F9',
                'calendar_weekend_fg': '#64748B'
            },

            # Dark Theme - Easy on eyes in low light
            'Dark': {
                'bg': '#0F172A',
                'fg': '#E2E8F0',
                'header_bg': '#1E293B',
                'header_fg': '#F8FAFC',
                'button_bg': '#3B82F6',
                'button_fg': '#FFFFFF',
                'tree_bg': '#1E293B',
                'tree_fg': '#E2E8F0',
                'tree_heading_bg': '#334155',
                'tree_heading_fg': '#F8FAFC',
                'tree_selected_bg': '#2563EB',
                'status_bg': '#1E293B',
                'status_fg': '#E2E8F0',
                'entry_bg': '#1E293B',
                'entry_fg': '#E2E8F0',
                'entry_select_bg': '#2563EB',
                'entry_select_fg': '#FFFFFF',
                'border_color': '#334155',
                'hover_bg': '#2563EB',
                'active_bg': '#1D4ED8',
                'calendar_bg': '#1E293B',
                'calendar_fg': '#E2E8F0',
                'calendar_header_bg': '#334155',
                'calendar_header_fg': '#F8FAFC',
                'calendar_select_bg': '#3B82F6',
                'calendar_select_fg': '#FFFFFF',
                'calendar_weekend_bg': '#0F172A',
                'calendar_weekend_fg': '#94A3B8'
            },

            # Ocean Theme - Calming blue-based palette
            'Ocean': {
                'bg': '#F0F9FF',
                'fg': '#0C4A6E',
                'header_bg': '#0369A1',
                'header_fg': '#F0F9FF',
                'button_bg': '#0EA5E9',
                'button_fg': '#FFFFFF',
                'tree_bg': '#FFFFFF',
                'tree_fg': '#0C4A6E',
                'tree_heading_bg': '#0369A1',
                'tree_heading_fg': '#F0F9FF',
                'tree_selected_bg': '#BAE6FD',
                'status_bg': '#E0F2FE',
                'status_fg': '#0C4A6E',
                'entry_bg': '#FFFFFF',
                'entry_fg': '#0C4A6E',
                'entry_select_bg': '#BAE6FD',
                'entry_select_fg': '#0C4A6E',
                'border_color': '#E0F2FE',
                'hover_bg': '#E0F2FE',
                'active_bg': '#BAE6FD',
                'calendar_bg': '#FFFFFF',
                'calendar_fg': '#0C4A6E',
                'calendar_header_bg': '#0369A1',
                'calendar_header_fg': '#F0F9FF',
                'calendar_select_bg': '#0EA5E9',
                'calendar_select_fg': '#FFFFFF',
                'calendar_weekend_bg': '#F0F9FF',
                'calendar_weekend_fg': '#0369A1'
            }
        }

        # Initialize core data structures and settings
        self.tasks = []  # List to store all tasks
        self.sort_column = 'deadline'  # Default sort column
        self.sort_order = True  # True for ascending, False for descending
        self.current_theme = 'Light'  # Default theme
        
        # Configure the base style
        self.style.theme_use('clam')
        
        # Build the user interface
        self.create_ui()
        
        # Apply theme styles
        self.configure_styles()
        
        # Setup right-click menu
        self.create_context_menu()
        
        # Load existing tasks and update display
        self.load_tasks()
        self.update_status()

        # Setup keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.task_entry.focus())  # New task shortcut
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())  # Search shortcut
        self.root.bind('<Delete>', lambda e: self.remove_task())  # Delete task shortcut
        self.root.bind('<Control-s>', lambda e: self.save_tasks())  # Save shortcut

    def _find_task_by_id(self, task_id):
        """Helper method to find a task by its unique ID"""
        for task in self.tasks:
            if task.get('id') == task_id:
                return task
        return None

    def create_context_menu(self):
        """Create and configure the right-click context menu"""
        if not hasattr(self, 'tree'):
            return
            
        # Create popup menu for right-click actions
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Mark as Complete/Incomplete", command=self.mark_complete)
        self.context_menu.add_command(label="Edit", command=self.edit_task)
        self.context_menu.add_command(label="Delete", command=self.remove_task)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Bind right-click event

    def show_context_menu(self, event):
        """Display the context menu at mouse position when right-clicking a task"""
        item_id = self.tree.identify_row(event.y)  # Get clicked item
        if item_id:
            self.tree.selection_set(item_id)  # Select the clicked item
            task = self._find_task_by_id(item_id)
            if task:
                self.context_menu.post(event.x_root, event.y_root)  # Show menu at mouse position

    def mark_complete(self):
        """Toggle the completion status of selected task(s)"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No task selected!")
            return

        updated = False
        for item_id in selected_items:
            task = self._find_task_by_id(item_id)
            if task:
                task['completed'] = not task['completed']  # Toggle completion status
                updated = True

        if updated:
            self.save_tasks()  # Save changes to file
            self.update_treeview()  # Refresh display
            self.update_status()  # Update status bar

    def add_task(self):
        """Add a new task with the specified details"""
        # Get input values
        task_text = self.task_entry.get().strip()
        deadline_str = self.cal.get_date().strftime("%d-%m-%Y")
        priority = self.priority_combo.get()

        # Validate task text
        if not task_text:
            messagebox.showerror("Error", "Task description cannot be empty!")
            return

        # Validate deadline date
        try:
            deadline_date = datetime.strptime(deadline_str, "%d-%m-%Y").date()
            if deadline_date < date.today():
                 if not messagebox.askyesno("Warning", "The deadline is in the past. Add anyway?"):
                     return
        except ValueError:
            messagebox.showerror("Error", "Invalid date format selected!")
            return

        # Create new task object with unique ID
        new_task = {
            'id': str(uuid.uuid4()),
            'task': task_text,
            'deadline': deadline_str,
            'priority': priority,
            'completed': False
        }

        # Add task and update UI
        self.tasks.append(new_task)
        self.save_tasks()
        self.clear_inputs()
        self.update_treeview()
        self.update_status()

    def configure_styles(self):
        """Configure and apply the current theme styles to all widgets"""
        theme = self.themes[self.current_theme]

        # Configure basic widget styles
        self.style.configure('.', background=theme['bg'], foreground=theme['fg'], font=('Segoe UI', 10))
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'], font=('Segoe UI', 10))
        
        # Configure Entry widget styles with focus effects
        self.style.configure('TEntry', 
            fieldbackground=theme['entry_bg'], 
            foreground=theme['entry_fg'], 
            insertcolor=theme['fg'],  # Cursor color
            selectbackground=theme['entry_select_bg'],  # Selection highlight
            selectforeground=theme['entry_select_fg'], 
            borderwidth=1, 
            relief='solid', 
            padding=8
        )
        self.style.map('TEntry', 
            bordercolor=[('focus', theme['button_bg']), ('!focus', theme['border_color'])]
        )

        # Configure Combobox styles with states
        self.style.configure('TCombobox', 
            fieldbackground=theme['entry_bg'],
            foreground=theme['entry_fg'],
            selectbackground=theme['entry_select_bg'],
            selectforeground=theme['entry_select_fg'],
            background=theme['entry_bg'],
            borderwidth=1,
            relief='solid',
            padding=8,
            arrowcolor=theme['fg']
        )
        
        # Map Combobox states (readonly, active, etc.)
        self.style.map('TCombobox',
            fieldbackground=[('readonly', theme['entry_bg'])],
            selectbackground=[('readonly', theme['entry_select_bg'])],
            selectforeground=[('readonly', theme['entry_select_fg'])],
            background=[('readonly', theme['entry_bg']), ('active', theme['hover_bg'])],
            foreground=[('readonly', theme['entry_fg'])],
            bordercolor=[('focus', theme['button_bg']), ('!focus', theme['border_color'])]
        )

        # Configure priority-specific styles with different colors
        priority_colors = {
            'Low': '#10B981',    # Green
            'Medium': '#F59E0B',  # Orange
            'High': '#EF4444'    # Red
        }
        
        # Create styles for each priority level
        for priority, color in priority_colors.items():
            style_name = f'Priority.{priority}.TCombobox'
            try:
                self.style.configure(style_name, foreground=color)
            except tk.TclError:
                # Handle style creation for complex widgets
                base_settings = self.style.layout('TCombobox')
                element_options = self.style.element_options('TCombobox.field')
                self.style.layout(style_name, base_settings)
                self.style.configure(style_name, foreground=color, **element_options)

        # Configure filter combobox style
        self.style.configure('Filter.TCombobox',
            font=('Segoe UI', 10),
            fieldbackground=theme['entry_bg'],
            foreground=theme['entry_fg'],
            padding=8,
            borderwidth=1,
            relief='solid',
            arrowcolor=theme['fg']
        )
        self.style.map('Filter.TCombobox',
            bordercolor=[('focus', theme['button_bg']), ('!focus', theme['border_color'])]
        )

        # Configure button styles with hover effects
        self.style.configure('TButton',
            font=('Segoe UI', 10, 'bold'),
            padding=(15, 8),
            background=theme['button_bg'],
            foreground=theme['button_fg'],
            borderwidth=0,
            relief='flat'
        )
        self.style.map('TButton',
            background=[('active', theme['active_bg']), ('pressed', theme['active_bg'])],
            foreground=[('active', theme['button_fg']), ('pressed', theme['button_fg'])]
        )

        # Configure header styles
        self.style.configure('Header.TFrame', background=theme['header_bg'])
        self.style.configure('Header.TLabel',
            background=theme['header_bg'],
            foreground=theme['header_fg'],
            font=('Segoe UI', 16, 'bold'),
            padding=20
        )

        # Configure Treeview styles for task list
        self.style.configure('Treeview',
            font=('Segoe UI', 10),
            rowheight=35,
            fieldbackground=theme['tree_bg'],
            background=theme['tree_bg'],
            foreground=theme['tree_fg'],
            borderwidth=1,
            relief='solid',
            bordercolor=theme['border_color']
        )
        
        # Configure Treeview header and selection styles
        self.style.configure('Treeview.Heading',
            font=('Segoe UI', 10, 'bold'),
            background=theme['tree_heading_bg'],
            foreground=theme['tree_heading_fg'],
            relief='flat',
            borderwidth=0,
            padding=10
        )
        self.style.map('Treeview',
            background=[('selected', theme['tree_selected_bg'])],
            foreground=[('selected', theme['tree_fg'])],
            bordercolor=[('focus', theme['button_bg']), ('!focus', theme['border_color'])]
        )

        # Configure checkbox style
        self.style.configure('TCheckbutton',
            background=theme['bg'],
            foreground=theme['fg'],
            padding=5,
            font=('Segoe UI', 10)
        )
        self.style.map('TCheckbutton',
            background=[('active', theme['hover_bg'])],
            foreground=[('active', theme['fg'])]
        )

        # Configure status bar style
        self.style.configure('Status.TLabel',
            background=theme['status_bg'],
            foreground=theme['status_fg'],
            relief='flat',
            padding=10,
            font=('Segoe UI', 9)
        )

        # Apply styles to existing widgets if they exist
        if hasattr(self, 'task_entry'):
            self.root.configure(bg=theme['bg'])
            for widget in self.root.winfo_children():
                try:
                    # Update top-level frames first
                    if isinstance(widget, ttk.Frame):
                        widget_style = widget.cget('style')
                        if widget_style:
                            widget.configure(style=widget_style)
                        else:
                            widget.configure(style='TFrame')

                    # Update children recursively
                    for child in widget.winfo_children():
                        try:
                            child_style = child.cget('style')
                            if child_style:
                                child.configure(style=child_style)
                            elif isinstance(child, tk.Canvas):
                                child.configure(bg=theme['bg'], highlightthickness=0)
                        except tk.TclError:
                            pass
                except Exception:
                    continue

            # Re-apply specific styles if widgets exist
            try:
                if hasattr(self, 'task_entry'):
                    self.task_entry.configure(style='TEntry')
                if hasattr(self, 'search_entry'):
                    self.search_entry.configure(style='TEntry')
                if hasattr(self, 'filter_combo'):
                    self.filter_combo.configure(style='Filter.TCombobox')
                if hasattr(self, 'theme_combo'):
                    self.theme_combo.configure(style='Filter.TCombobox')
                if hasattr(self, 'priority_combo'):
                    self.update_priority_style()
                if hasattr(self, 'status_bar'):
                    self.status_bar.configure(style='Status.TLabel')
                if hasattr(self, 'cal'):
                    self.cal.configure(
                        background=theme['calendar_bg'], foreground=theme['calendar_fg'],
                        selectbackground=theme['calendar_select_bg'], selectforeground=theme['calendar_select_fg'],
                        headersbackground=theme['calendar_header_bg'], headersforeground=theme['calendar_header_fg'],
                        bordercolor=theme['border_color'],
                        normalbackground=theme['calendar_bg'], normalforeground=theme['calendar_fg'],
                        weekendbackground=theme['calendar_weekend_bg'], weekendforeground=theme['calendar_weekend_fg'],
                        othermonthbackground=theme['calendar_bg'], othermonthwebackground=theme['calendar_bg'],
                        othermonthforeground=theme['calendar_fg'], othermonthweforeground=theme['calendar_fg'],
                        tooltipforeground=theme['fg'], tooltipbackground=theme['bg'],
                        arrowcolor=theme['calendar_header_fg'],
                        relief='solid', borderwidth=1
                    )
                if hasattr(self, 'tree'):
                    self.tree.configure(style='Treeview')
                    self.tree.heading('#0', text='')
            except Exception as e:
                print(f"Error applying styles: {e}")

    def create_ui(self):
        """Create and configure the main user interface components"""
        # Main container with padding
        main_container = ttk.Frame(self.root, style='TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Header section with app title
        header_frame = ttk.Frame(main_container, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header_frame, text="To-Do List Manager", style='Header.TLabel').pack(pady=5)

        # First-time user welcome message
        if self.is_first_run:
            welcome_frame = ttk.Frame(main_container, style='TFrame')
            welcome_frame.pack(fill=tk.X, pady=(0, 10))
            welcome_text = ("Welcome! Add tasks below.\n"
                          "Tips: Ctrl+N=New, Ctrl+F=Search, Del=Remove, "
                          "Double-click=Edit, Right-click=Options")
            ttk.Label(welcome_frame, text=welcome_text, justify=tk.CENTER, 
                     style='TLabel', font=('Segoe UI', 10)).pack(pady=3)

        # Task input section
        input_frame = ttk.Frame(main_container, style='TFrame')
        input_frame.pack(fill=tk.X, pady=(0, 15))
        input_frame.columnconfigure(1, weight=1)  # Make task entry expandable

        # Task description input
        ttk.Label(input_frame, text="Task:", style='TLabel', 
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=(0, 10), pady=5, sticky='w')
        self.task_entry = ttk.Entry(input_frame, width=60, style='TEntry')
        self.task_entry.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky='ew')
        
        # Bind task entry events
        self.task_entry.bind('<Return>', lambda event: self.add_task())  # Enter to add task
        self.task_entry.bind('<Escape>', lambda event: self.clear_inputs())  # Escape to clear
        self.create_tooltip(self.task_entry, "Enter task, press Enter to add")

        # Deadline input with calendar
        ttk.Label(input_frame, text="Deadline:", style='TLabel', 
                 font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, padx=(0, 10), pady=5, sticky='w')
        self.cal = DateEntry(input_frame, date_pattern='dd-mm-yyyy', width=15, style='TEntry')
        self.cal.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.cal.set_date(date.today())  # Set default to today
        self.create_tooltip(self.cal, "Select task deadline")

        # Priority selection dropdown
        ttk.Label(input_frame, text="Priority:", style='TLabel', 
                 font=('Segoe UI', 10, 'bold')).grid(row=1, column=2, padx=(20, 10), pady=5, sticky='w')
        self.priority_combo = ttk.Combobox(input_frame, values=["Low", "Medium", "High"], 
                                         width=15, state='readonly')
        self.priority_combo.grid(row=1, column=3, padx=5, pady=5, sticky='w')
        self.priority_combo.set("Medium")  # Set default priority
        self.update_priority_style()  # Apply priority-specific styling
        self.priority_combo.bind("<<ComboboxSelected>>", self.update_priority_style)
        self.create_tooltip(self.priority_combo, "Set task priority level")

        # Add task button
        button_row = ttk.Frame(input_frame, style='TFrame')
        button_row.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        add_button = ttk.Button(button_row, text="Add Task", command=self.add_task, style='TButton')
        add_button.pack()
        self.create_tooltip(add_button, "Add new task (Ctrl+N)")

        # Search and filter controls section
        controls_frame = ttk.Frame(main_container, style='TFrame')
        controls_frame.pack(fill=tk.X, pady=(10, 15))
        controls_frame.columnconfigure(1, weight=1)  # Make search entry expandable

        # Search box
        ttk.Label(controls_frame, text="Search:", style='TLabel', 
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, padx=(0, 10), pady=5, sticky='w')
        self.search_entry = ttk.Entry(controls_frame, style='TEntry')
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        # Bind search events
        self.search_entry.bind('<KeyRelease>', lambda e: self.update_treeview())  # Live search
        self.search_entry.bind('<Escape>', lambda e: [self.search_entry.delete(0, tk.END), 
                                                    self.update_treeview()])  # Clear search
        self.create_tooltip(self.search_entry, "Search tasks (Ctrl+F)\nPress Esc to clear")

        # Filter dropdown
        ttk.Label(controls_frame, text="Filter:", style='TLabel', 
                 font=('Segoe UI', 10, 'bold')).grid(row=0, column=2, padx=(20, 10), pady=5, sticky='w')
        self.filter_combo = ttk.Combobox(controls_frame, values=["All", "Completed", "Pending"], 
                                       width=12, state='readonly', style='Filter.TCombobox')
        self.filter_combo.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        self.filter_combo.set("All")  # Default to showing all tasks
        self.filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_treeview())
        self.create_tooltip(self.filter_combo, "Filter tasks by status")

        # Theme section
        ttk.Label(controls_frame, text="Theme:", style='TLabel', font=('Segoe UI', 10, 'bold')).grid(row=0, column=4, padx=(20, 10), pady=5, sticky='w')
        self.theme_combo = ttk.Combobox(controls_frame, values=list(self.themes.keys()), width=10, state='readonly', style='Filter.TCombobox')
        self.theme_combo.grid(row=0, column=5, padx=5, pady=5, sticky='w')
        self.theme_combo.set(self.current_theme)
        self.theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        self.create_tooltip(self.theme_combo, "Change application theme")

        # Action buttons Frame (Remove Button Only Now)
        button_frame = ttk.Frame(main_container, style='TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 10)) # Place below controls

        # FIX: Removed redundant Search button
        remove_button = ttk.Button(button_frame, text="Remove Selected", command=self.remove_task, style='TButton')
        remove_button.pack(side=tk.RIGHT, padx=5) # Align right
        self.create_tooltip(remove_button, "Delete selected tasks (Delete Key)")


        # Treeview section
        tree_frame = ttk.Frame(main_container) # No specific style needed, will contain treeview+scrollbar
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        columns = ('task', 'deadline', 'priority', 'completed')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', style='Treeview')

        # Set column widths and headings
        col_widths = {'task': 350, 'deadline': 100, 'priority': 80, 'completed': 80} # Adjusted widths
        col_anchors = {'task': 'w', 'deadline': 'center', 'priority': 'center', 'completed': 'center'} # Anchor task left
        for col in columns:
            self.tree.heading(col, text=col.capitalize(), command=lambda c=col: self.sort_tasks(c), anchor='center') # Keep heading centered
            self.tree.column(col, width=col_widths.get(col, 100), anchor=col_anchors.get(col, 'center'), stretch=tk.YES if col=='task' else tk.NO) # Allow task column to stretch

        # Add scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.edit_task_event) # MODIFIED: Renamed event handler
        self.tree.bind('<Delete>', lambda e: self.remove_task()) # Already bound globally, but keep for explicitness
        self.create_tooltip(self.tree, "Double-click to edit\nRight-click for options\nDelete key to remove")


        # Status bar
        self.status_bar = ttk.Label(main_container, text="Status Bar", style='Status.TLabel', anchor='w') # Apply style, anchor left
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        self.status_bar.bind('<Enter>', self.show_status_tooltip)
        self.status_bar.bind('<Leave>', self.hide_status_tooltip)

    # Tooltip creation helper (remains mostly the same)
    def create_tooltip(self, widget, text):
        tooltip = None
        # Use a more robust tooltip implementation if available, or keep simple Toplevel
        def show_tooltip(event):
            nonlocal tooltip
            if tooltip: return # Prevent multiple tooltips
            tooltip = tk.Toplevel(self.root)
            tooltip.wm_overrideredirect(True)
            # Position near cursor, slightly offset
            x = self.root.winfo_pointerx() + 15
            y = self.root.winfo_pointery() + 10
            tooltip.wm_geometry(f"+{x}+{y}")
            # Use themed label for tooltip
            theme = self.themes[self.current_theme]
            bg_color = theme.get('status_bg', '#FFFFE0') # Use status bg or default light yellow
            fg_color = theme.get('status_fg', '#000000') # Use status fg or default black
            label = ttk.Label(tooltip, text=text, background=bg_color, foreground=fg_color, padding=5, justify=tk.LEFT, relief='solid', borderwidth=1)
            label.pack()
            widget.tooltip_window = tooltip # Store reference on widget

        def hide_tooltip(event):
            nonlocal tooltip
            if hasattr(widget, 'tooltip_window') and widget.tooltip_window:
                widget.tooltip_window.destroy()
                widget.tooltip_window = None
            tooltip = None # Reset tooltip variable

        # Bind events
        widget.bind('<Enter>', show_tooltip, add='+')
        widget.bind('<Leave>', hide_tooltip, add='+')
        # Also hide if the widget is destroyed
        widget.bind('<Destroy>', hide_tooltip, add='+')


    def update_priority_style(self, event=None):
        if not hasattr(self, 'priority_combo'):
            return
            
        priority = self.priority_combo.get()
        style_name = f'Priority.{priority}.TCombobox'
        
        try:
            # Try to configure the style if it doesn't exist
            if style_name not in self.style.theme_names():
                priority_colors = {'Low': '#10B981', 'Medium': '#F59E0B', 'High': '#EF4444'}
                if priority in priority_colors:
                    self.style.configure(style_name, foreground=priority_colors[priority])
            
            # Apply the style if it exists
            if style_name in self.style.theme_names():
                self.priority_combo.configure(style=style_name)
            else:
                self.priority_combo.configure(style='TCombobox')
        except Exception as e:
            print(f"Error updating priority style: {e}")
            self.priority_combo.configure(style='TCombobox')


    def save_tasks(self):
        """Save tasks to JSON file with error handling"""
        try:
            # Ensure all tasks have valid IDs
            for task in self.tasks:
                if 'id' not in task or not task['id']:
                    task['id'] = str(uuid.uuid4())

            # Write tasks to file with pretty formatting
            with open(self.tasks_file, 'w') as f:
                json.dump(self.tasks, f, indent=4)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save tasks to {self.tasks_file}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while saving tasks: {e}")

    def load_tasks(self):
        """Load tasks from JSON file with error handling and validation"""
        try:
            # Read tasks from file
            with open(self.tasks_file, 'r') as f:
                loaded_tasks = json.load(f)

            self.tasks = []
            tasks_updated = False

            # Validate and process each task
            for task in loaded_tasks:
                if isinstance(task, dict):
                    # Ensure each task has a unique ID
                    if 'id' not in task or not task['id']:
                        task['id'] = str(uuid.uuid4())
                        tasks_updated = True
                    self.tasks.append(task)
                else:
                    print(f"Warning: Skipping invalid item in tasks.json: {task}")

            # Save if we added any missing IDs
            if tasks_updated:
                self.save_tasks()

            self.update_treeview()

        except FileNotFoundError:
            self.tasks = []  # Start with empty task list
            self.update_treeview()
        except json.JSONDecodeError:
            messagebox.showerror("Error", 
                               f"Error reading '{os.path.basename(self.tasks_file)}'. "
                               "File might be corrupted. Starting fresh.")
            self.tasks = []
            self.update_treeview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")
            self.tasks = []
            self.update_treeview()

    def sort_tasks(self, column):
        """Sort tasks by the specified column"""
        # Toggle sort order if clicking same column
        if self.sort_column == column:
            self.sort_order = not self.sort_order
        else:
            self.sort_column = column
            self.sort_order = True

        reverse = not self.sort_order

        # Define sort keys for different columns
        if column == 'deadline':
            # Sort by date, handling invalid dates
            def deadline_key(task):
                try:
                    return datetime.strptime(task.get('deadline', ''), "%d-%m-%Y")
                except (ValueError, TypeError):
                    return datetime.max  # Put invalid dates last
            key_func = deadline_key
        elif column == 'priority':
            # Sort by priority level
            priority_order = {'Low': 1, 'Medium': 2, 'High': 3}
            key_func = lambda task: priority_order.get(task.get('priority', 'Medium'), 2)
        elif column == 'completed':
            key_func = lambda task: task.get('completed', False)
        else:  # Sort by task text
            key_func = lambda task: task.get('task', '').lower()

        # Perform the sort
        try:
            self.tasks.sort(key=key_func, reverse=reverse)
        except Exception as e:
            messagebox.showerror("Sort Error", f"Could not sort tasks: {e}")
            return

        # Update column headers to show sort direction
        for col in self.tree['columns']:
            indicator = ''
            if col == self.sort_column:
                indicator = ' ▲' if self.sort_order else ' ▼'
            self.tree.heading(col, text=f"{col.capitalize()}{indicator}")

        # Refresh the display
        self.update_treeview()

    def update_treeview(self):
        """Update the task list display based on current filters and search criteria"""
        # Clear existing items from the tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get current filter and search settings
        current_filter = self.filter_combo.get()
        search_query = self.search_entry.get().strip().lower()

        # Iterate through tasks and apply filters
        for task in self.tasks:
            # Ensure task has an ID
            task_id = task.get('id')
            if not task_id:
                print(f"Warning: Task missing ID during Treeview update: {task.get('task')}")
                continue

            task_completed = task.get('completed', False)

            # Apply status filter (All, Completed, Pending)
            if (current_filter == "Completed" and not task_completed) or \
               (current_filter == "Pending" and task_completed):
                continue

            # Apply search filter across all fields
            if search_query:
                task_text = task.get('task', '').lower()
                task_deadline = task.get('deadline', '').lower()
                task_priority = task.get('priority', '').lower()
                if not (search_query in task_text or
                        search_query in task_deadline or
                        search_query in task_priority):
                    continue

            # Prepare values for display
            display_completed = '✓' if task_completed else '✗'
            display_values = (
                task.get('task', ''),
                task.get('deadline', ''),
                task.get('priority', 'Medium'),
                display_completed
            )

            # Add task to tree with appropriate styling
            try:
                self.tree.insert('', 'end', iid=task_id, values=display_values)
            except tk.TclError as e:
                print(f"Error inserting task {task_id} into treeview: {e}")

    def clear_inputs(self):
        self.task_entry.delete(0, tk.END)
        self.cal.set_date(date.today())
        self.priority_combo.set("Medium")
        self.update_priority_style()
        self.task_entry.focus() # Set focus back to task entry


    def remove_task(self):
        selected_items = self.tree.selection() # Get selected item IDs (task UUIDs)
        if not selected_items:
            messagebox.showwarning("Warning", "No task selected to remove!")
            return

        confirm_msg = f"Are you sure you want to delete {len(selected_items)} selected task(s)?"
        if not messagebox.askyesno("Confirm Delete", confirm_msg):
            return

        # Create a list of task IDs to remove
        ids_to_remove = list(selected_items)
        original_task_count = len(self.tasks)

        # Filter tasks, keeping only those whose IDs are NOT in the removal list
        self.tasks = [task for task in self.tasks if task.get('id') not in ids_to_remove]

        removed_count = original_task_count - len(self.tasks)

        if removed_count > 0:
            self.save_tasks()
            self.update_treeview()
            self.update_status()
        else:
             # This shouldn't happen if selection IDs are valid task IDs
             messagebox.showerror("Error", "Could not find selected tasks to remove.")


    def edit_task_event(self, event):
        """Handles the double-click event on the Treeview."""
        selected_item = self.tree.focus() # Get the item that has focus (double-clicked item)
        if selected_item:
            self.edit_task(task_id=selected_item) # Call edit logic with the task ID

    def edit_task(self, task_id=None):
        """Opens the edit dialog for the task with the given ID."""
        if not task_id:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("Warning", "No task selected to edit!")
                return
            task_id = selected_items[0]

        task_to_edit = self._find_task_by_id(task_id)
        if not task_to_edit:
            messagebox.showerror("Error", "Could not find the selected task to edit.")
            return

        # Create and configure edit dialog
        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Task")
        edit_dialog.geometry("500x450")  # Increased size
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()
        edit_dialog.resizable(False, False)

        # Apply theme
        theme = self.themes[self.current_theme]
        edit_dialog.configure(bg=theme['bg'])

        # Main content frame with more padding
        main_frame = ttk.Frame(edit_dialog, style='TFrame', padding=(30, 20))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Task input with more space
        task_label = ttk.Label(main_frame, text="Task:", style='TLabel', font=('Segoe UI', 11, 'bold'))
        task_label.pack(anchor='w', pady=(0, 8))
        
        task_entry = ttk.Entry(main_frame, style='TEntry', width=60)
        task_entry.pack(fill='x', pady=(0, 25))
        task_entry.insert(0, task_to_edit.get('task', ''))
        task_entry.focus_set()
        # Add Tab key binding to move to next field
        task_entry.bind('<Tab>', lambda e: cal.focus_set())
        # Prevent Enter from triggering save
        task_entry.bind('<Return>', lambda e: 'break')

        # Deadline input with more space
        deadline_label = ttk.Label(main_frame, text="Deadline:", style='TLabel', font=('Segoe UI', 11, 'bold'))
        deadline_label.pack(anchor='w', pady=(0, 8))
        
        cal = DateEntry(main_frame, width=30, date_pattern='dd-mm-yyyy', style='TEntry')
        cal.pack(fill='x', pady=(0, 25))
        try:
            current_deadline = datetime.strptime(task_to_edit.get('deadline', ''), "%d-%m-%Y")
            cal.set_date(current_deadline)
        except (ValueError, TypeError):
            cal.set_date(date.today())
        # Prevent Enter from triggering save
        cal.bind('<Return>', lambda e: 'break')
        # Add Tab key binding to move to next field
        cal.bind('<Tab>', lambda e: priority_combo.focus_set())

        # Priority input with more space
        priority_label = ttk.Label(main_frame, text="Priority:", style='TLabel', font=('Segoe UI', 11, 'bold'))
        priority_label.pack(anchor='w', pady=(0, 8))
        
        priority_combo = ttk.Combobox(main_frame, values=["Low", "Medium", "High"], 
                                    state='readonly', style='TCombobox', width=30)
        priority_combo.pack(fill='x', pady=(0, 25))
        priority_combo.set(task_to_edit.get('priority', 'Medium'))
        # Prevent Enter from triggering save
        priority_combo.bind('<Return>', lambda e: 'break')
        # Add Tab key binding to move to next field
        priority_combo.bind('<Tab>', lambda e: completed_cb.focus_set())

        # Completed checkbox with more space
        completed_var = tk.BooleanVar(value=task_to_edit.get('completed', False))
        completed_cb = ttk.Checkbutton(main_frame, text="Mark as completed", 
                                     variable=completed_var, style='TCheckbutton',
                                     padding=(0, 5))
        completed_cb.pack(anchor='w', pady=(0, 30))
        # Prevent Enter from triggering save
        completed_cb.bind('<Return>', lambda e: 'break')
        # Add Tab key binding to move to save button
        completed_cb.bind('<Tab>', lambda e: save_button.focus_set())

        # Button frame with more padding
        button_frame = ttk.Frame(main_frame, style='TFrame')
        button_frame.pack(fill='x', pady=(10, 0))

        def save_edits():
            new_task_text = task_entry.get().strip()
            new_deadline_str = cal.get_date().strftime("%d-%m-%Y")
            new_priority = priority_combo.get()
            new_completed = completed_var.get()

            if not new_task_text:
                messagebox.showerror("Error", "Task cannot be empty!", parent=edit_dialog)
                task_entry.focus_set()
                return

            try:
                new_deadline_date = datetime.strptime(new_deadline_str, "%d-%m-%Y").date()
                if new_deadline_date < date.today():
                    if not messagebox.askyesno("Warning", "Deadline is in the past. Save anyway?", parent=edit_dialog):
                        cal.focus_set()
                        return
            except ValueError:
                messagebox.showerror("Error", "Invalid date format!", parent=edit_dialog)
                cal.focus_set()
                return

            task_to_update = self._find_task_by_id(task_id)
            if task_to_update:
                task_to_update.update({
                    'task': new_task_text,
                    'deadline': new_deadline_str,
                    'priority': new_priority,
                    'completed': new_completed
                })
                self.save_tasks()
                self.update_treeview()
                self.update_status()
                edit_dialog.destroy()
            else:
                messagebox.showerror("Error", "Task could not be found for saving.", parent=edit_dialog)

        # Larger buttons with more padding
        save_button = ttk.Button(button_frame, text="Save Changes (Ctrl+S)", command=save_edits, 
                               style='TButton', padding=(20, 10))
        save_button.pack(side='right', padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel (Esc)", command=edit_dialog.destroy, 
                                 style='TButton', padding=(20, 10))
        cancel_button.pack(side='right', padx=5)

        # Update tooltips to show new shortcuts
        self.create_tooltip(task_entry, "Edit the task description\nTab to move to next field")
        self.create_tooltip(cal, "Change the task deadline\nTab to move to next field")
        self.create_tooltip(priority_combo, "Change the task priority\nTab to move to next field")
        self.create_tooltip(completed_cb, "Toggle completion status\nTab to move to next field")
        self.create_tooltip(save_button, "Save changes (Ctrl+S)")
        self.create_tooltip(cancel_button, "Discard changes (Esc)")

        # Update keyboard shortcuts
        edit_dialog.bind('<Control-s>', lambda e: save_edits())
        edit_dialog.bind('<Escape>', lambda e: edit_dialog.destroy())
        # Remove the Return binding that was causing the issue
        edit_dialog.unbind('<Return>')

        # Center the dialog
        edit_dialog.update_idletasks()
        width = edit_dialog.winfo_width()
        height = edit_dialog.winfo_height()
        x = (edit_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_dialog.winfo_screenheight() // 2) - (height // 2)
        edit_dialog.geometry(f'{width}x{height}+{x}+{y}')

        edit_dialog.wait_window()

    def update_status(self):
        """Update the status bar with current task statistics"""
        # Calculate task statistics
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.get('completed', False))
        pending = total - completed
        percentage = (completed / total * 100) if total > 0 else 0

        # Update status bar text
        status_text = f"Total: {total} | Completed: {completed} | Pending: {pending} ({percentage:.0f}%)"
        self.status_bar.config(text=status_text)

    def show_status_tooltip(self, event):
        # Clean up any existing tooltip
        self.hide_status_tooltip(None)
        
        try:
            self.status_tooltip_window = tk.Toplevel(self.root)
            self.status_tooltip_window.wm_overrideredirect(True)
            x = self.root.winfo_pointerx() + 15
            y = self.root.winfo_pointery() + 10
            self.status_tooltip_window.wm_geometry(f"+{x}+{y}")

            shortcuts = [
                "Keyboard Shortcuts:",
                " Ctrl+N : Focus New Task",
                " Ctrl+F : Focus Search",
                " Delete : Remove Selected Task(s)",
                " Ctrl+S : Save (Implicit)",
                " Enter  : Add Task (in Task field)",
                " Escape : Clear Task/Search Field / Close Edit",
                " Double-click / Right-click : Task Options"
            ]
            theme = self.themes[self.current_theme]
            bg_color = theme.get('status_bg', '#333333')
            fg_color = theme.get('status_fg', '#FFFFFF')

            label = ttk.Label(self.status_tooltip_window,
                            text='\n'.join(shortcuts),
                            background=bg_color, foreground=fg_color,
                            padding=8, justify=tk.LEFT,
                            relief='solid', borderwidth=1)
            label.pack()
            
            # Ensure tooltip is destroyed when main window is closed
            self.root.bind('<Destroy>', self.hide_status_tooltip, add='+')
        except Exception as e:
            print(f"Error showing status tooltip: {e}")
            self.hide_status_tooltip(None)

    def hide_status_tooltip(self, event):
        try:
            if hasattr(self, 'status_tooltip_window') and self.status_tooltip_window:
                self.status_tooltip_window.destroy()
                self.status_tooltip_window = None
        except Exception as e:
            print(f"Error hiding status tooltip: {e}")

    def change_theme(self, event=None):
        new_theme = self.theme_combo.get()
        if new_theme in self.themes and new_theme != self.current_theme:
            self.current_theme = new_theme
            self.configure_styles() # Apply new theme styles to all widgets


if __name__ == "__main__":
    root = tk.Tk()
    # Set minimum size for the main window
    root.minsize(600, 400)
    app = TodoApp(root)
    # Apply initial theme configuration fully
    app.change_theme()
    root.mainloop()