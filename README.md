# To-Do List Application

A modern, feature-rich To-Do List application built with Python and Tkinter. This application helps you stay organized with a clean interface, task prioritization, deadlines, visual statistics, and customizable themes.

## Features

- **Task Management**
  - Add, edit, and delete tasks with ease
  - Set task priorities (Low, Medium, High) with color coding
  - Set deadlines using an integrated calendar widget
  - Mark tasks as complete/incomplete
  - Task categories (Work, Personal, Health, Finance, Other)
  - Sort tasks by any column (task, deadline, priority, status)
  - Advanced search and filtering capabilities

- **Dashboard & Analytics**
  - Visual pie chart showing task completion statistics
  - Real-time statistics cards (total, completed, pending tasks)
  - Task distribution by priority visualization
  - Auto-updating charts that respond to theme changes

- **User Interface**
  - Modern, minimal design with smooth interactions
  - Three beautiful themes:
    - **Minimal Light** - Clean, airy, white-on-white aesthetic
    - **Soothing Dark** - Soft charcoal, easy on the eyes
    - **Matcha Latte** - Soft pastel aesthetics with green accents
  - Responsive layout that adapts to window size
  - Tooltips for better usability
  - Status bar with live task statistics
  - Comprehensive keyboard shortcuts for power users

- **Data Management**
  - Automatic saving of tasks to JSON file
  - Persistent storage between sessions
  - Comprehensive error handling and data validation
  - Unique UUID-based task IDs for reliable management
  - Safe file operations with error recovery

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BennyAliston/To-do_List.git
   cd To-do_List
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements

- Python 3.7 or higher
- tkinter (usually comes pre-installed with Python)
- tkcalendar >= 1.6.1
- pillow >= 9.0.0

## Usage

### Running the Application

```bash
python To-do.py
```

### Keyboard Shortcuts

- `Ctrl+N`: Focus on new task input
- `Ctrl+F`: Focus on search box
- `Delete`: Remove selected task(s)
- `Ctrl+S`: Save changes
- `Enter`: Add task (in task field)
- `Escape`: Clear task/search field or close edit dialog
- `Double-click`: Edit task
- `Right-click`: Show task options

### Task Management

1. **Adding a Task**
   - Enter task description
   - Select deadline using calendar
   - Choose priority level
   - Press Enter or click "Add Task"

2. **Editing a Task**
   - Double-click on a task
   - Modify task details
   - Click "Save Changes" or press Ctrl+S

3. **Deleting a Task**
   - Select task(s)
   - Press Delete key or use right-click menu
   - Confirm deletion

4. **Marking Tasks Complete**
   - Select task(s)
   - Use right-click menu to toggle completion status

### Search and Filter

- Use the search box to find tasks by text, deadline, or priority
- Use the filter dropdown to show All, Completed, or Pending tasks
- Click column headers to sort tasks

### Themes

Switch between three beautiful themes using the theme dropdown:
- **Minimal Light** - Clean white interface with high contrast elements
- **Soothing Dark** - Soft dark mode with reduced eye strain
- **Matcha Latte** - Warm pastel theme with calming green accents

Theme changes apply instantly to all UI elements including charts and dialogs.

## Code Structure

The application is organized into a single, well-documented `TodoApp` class with the following main components:

1. **Initialization (`__init__`)**
   - Sets up the main window and configuration
   - Defines three color themes with comprehensive styling
   - Initializes data structures for tasks and categories
   - Creates the complete user interface

2. **UI Components**
   - Header with app title and branding
   - Task input section with deadline picker and priority selector
   - Search bar and filter controls
   - Task list (Treeview widget) with sortable columns
   - Dashboard with statistics cards and pie chart
   - Status bar with real-time task counters

3. **Core Functionality**
   - Task management (add, edit, delete, toggle completion)
   - Data persistence (automatic save/load from JSON)
   - Advanced search and filtering capabilities
   - Multi-column sorting with visual indicators
   - Theme management with instant switching
   - Visual analytics with auto-updating pie charts

4. **Helper Methods**
   - UUID-based task ID generation and management
   - Dynamic UI updates and theme application
   - Comprehensive error handling and user feedback
   - Tooltip creation for enhanced UX
   - Statistical calculations for dashboard

## Project Structure

```
To-do_List/
├── To-do.py                          # Main application file
├── tasks.json                         # Task storage (auto-generated)
├── requirements.txt                   # Python dependencies
├── README.md                          # Documentation
├── Multi Platform App work in progress/
│   ├── main.py                       # Flet-based cross-platform version (WIP)
│   └── tasks.json                    # Separate task storage for Flet app
└── Old_version/
    ├── todo_list.py                  # Legacy version
    └── tasks.json                    # Legacy task storage
```

## Data Storage

Tasks are stored in a JSON file (`tasks.json`) with the following structure:
```json
[
  {
    "id": "unique-uuid",
    "task": "Task description",
    "deadline": "DD-MM-YYYY",
    "priority": "Low/Medium/High",
    "completed": false
  }
]
```

## Error Handling

The application includes comprehensive error handling for:
- File I/O operations (reading/writing tasks.json)
- JSON parsing and data validation
- User input validation (dates, priorities, empty fields)
- UI operations and widget interactions
- Theme switching and style application
- Calendar widget initialization and date selection

## Future Development

The `Multi Platform App work in progress/` folder contains an in-development version using **Flet** framework for true cross-platform deployment (Windows, macOS, Linux, Web, iOS, Android).

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

**Kritagya Kumar (Benny Aliston)**
- GitHub: [@BennyAliston](https://github.com/BennyAliston)

## Acknowledgments

- **Tkinter** - Python's standard GUI framework
- **tkcalendar** - Beautiful calendar widget for date selection
- **Pillow** - Python Imaging Library for image handling
- Python community for continuous support and inspiration

---

**Note:** For the latest updates and releases, please visit the [GitHub repository](https://github.com/BennyAliston/To-do_List). 