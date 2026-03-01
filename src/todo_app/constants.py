"""Application constants and default configuration."""

# Window settings
APP_TITLE = "To-Do List"
DEFAULT_WINDOW_SIZE = "800x600"
MIN_WINDOW_WIDTH = 600
MIN_WINDOW_HEIGHT = 400

# Date format used throughout the application
DATE_FORMAT = "%d-%m-%Y"

# Default task categories
CATEGORIES = ["Work", "Personal", "Health", "Finance", "Other"]

# Priority levels and sort order
PRIORITY_LEVELS = ["Low", "Medium", "High"]
PRIORITY_ORDER = {"Low": 1, "Medium": 2, "High": 3}

# Priority color coding (softer tones for UI)
PRIORITY_COLORS = {
    "Low": "#34D399",
    "Medium": "#FBBF24",
    "High": "#F87171",
}

# Default settings
DEFAULT_THEME = "Minimal Light"
DEFAULT_PRIORITY = "Medium"
DEFAULT_CATEGORY = "General"
DEFAULT_SORT_COLUMN = "deadline"
DEFAULT_FILTER = "All"

# Font definitions
FONT_FAMILY = "Segoe UI"
BASE_FONT = (FONT_FAMILY, 11)
BOLD_FONT = (FONT_FAMILY, 11, "bold")
HEADER_FONT = (FONT_FAMILY, 18, "bold")
SMALL_FONT = (FONT_FAMILY, 9)
LABEL_FONT = (FONT_FAMILY, 10, "bold")
CARD_TITLE_FONT = (FONT_FAMILY, 12)
CHART_LABEL_FONT = (FONT_FAMILY, 10, "bold")
CHART_EMPTY_FONT = (FONT_FAMILY, 14)
STAT_VALUE_FONT = (FONT_FAMILY, 24, "bold")
WELCOME_FONT = (FONT_FAMILY, 10)

# Treeview column configuration
TREEVIEW_COLUMNS = ("task", "category", "deadline", "priority", "completed")
COLUMN_WIDTHS = {"task": 300, "category": 100, "deadline": 100, "priority": 80, "completed": 80}
COLUMN_ANCHORS = {"task": "w", "category": "center", "deadline": "center", "priority": "center", "completed": "center"}

# Dashboard colors
STAT_TOTAL_COLOR = "#3B82F6"
STAT_PENDING_COLOR = "#F59E0B"
STAT_OVERDUE_COLOR = "#EF4444"
CHART_COMPLETED_COLOR = "#10B981"
CHART_PENDING_COLOR = "#F59E0B"

# Keyboard shortcut descriptions
KEYBOARD_SHORTCUTS = [
    "Keyboard Shortcuts:",
    " Ctrl+N : Focus New Task",
    " Ctrl+F : Focus Search",
    " Delete : Remove Selected Task(s)",
    " Ctrl+S : Save (Implicit)",
    " Enter  : Add Task (in Task field)",
    " Escape : Clear Task/Search Field / Close Edit",
    " Double-click / Right-click : Task Options",
]
