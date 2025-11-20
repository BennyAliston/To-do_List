# To-Do List Application

A modern, feature-rich To-Do List application built with Python and Tkinter. This application allows users to manage their tasks with features like task prioritization, deadlines, search, filtering, and theme customization.

## Features

- **Task Management**
  - Add, edit, and delete tasks
  - Set task priorities (Low, Medium, High)
  - Set deadlines using a calendar widget
  - Mark tasks as complete/incomplete
  - Sort tasks by different columns
  - Search and filter tasks

- **User Interface**
  - Modern and clean design
  - Multiple themes (Light, Dark, Ocean)
  - Responsive layout
  - Tooltips for better usability
  - Status bar with task statistics
  - Keyboard shortcuts for quick actions

- **Data Management**
  - Automatic saving of tasks
  - JSON file storage
  - Error handling and data validation
  - Unique task IDs for reliable task management

## Installation

1. Clone the repository or download the source code
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Requirements

- Python 3.x
- tkinter (usually comes with Python)
- tkcalendar
- pillow

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

- Use the theme dropdown to switch between Light, Dark, and Ocean themes
- Theme changes are applied immediately

## Code Structure

The application is organized into a single class `TodoApp` with the following main components:

1. **Initialization (`__init__`)**
   - Sets up the main window
   - Defines themes and styles
   - Initializes data structures
   - Creates the user interface

2. **UI Components**
   - Main container with header
   - Task input section
   - Search and filter controls
   - Task list (Treeview)
   - Status bar

3. **Core Functionality**
   - Task management (add, edit, delete)
   - Data persistence (save/load)
   - Search and filtering
   - Sorting
   - Theme management

4. **Helper Methods**
   - Task ID management
   - UI updates
   - Error handling
   - Tooltip creation

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
- File operations
- Data validation
- User input
- UI operations
- Theme changes

## Contributing

Feel free to contribute to this project by:
1. Forking the repository
2. Creating a feature branch
3. Making your changes
4. Submitting a pull request

## License

This project is open source and available under the MIT License.

## Author

Kritagya Kumar (Benny Aliston)

## Acknowledgments

- Tkinter for the GUI framework
- tkcalendar for the date picker widget
- Python community for various resources and inspiration 