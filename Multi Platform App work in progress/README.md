# Habito-do ✅

**Habito-do** is a stylish, cross-platform To-Do List application built with [Flet](https://flet.dev) (Flutter for Python). It features a distinct **Neubrutal** "cartoon" aesthetic, responsive design, and smooth animations.

![Habito-do Icon](assets/icon.png)

## ✨ Features

- **🎨 Neubrutal Design**: High-contrast, bold outlines, and "pop" colors.
- **🌗 Dynamic Themes**:
  - **Light Mode**: Pastel Pink & White.
  - **Dark Mode**: Deep Grey & White.
- **📱 Fully Responsive**: Adapts gracefully from desktop to mobile screens.
- **⚡ Snappy Interactions**: Toast notifications, fade-out delete animations, and interactive chips.
- **📅 Smart Inputs**: Calendar date picker and color-coded priority levels.

## 🛠️ Installation

1. **Clone the repository** (if you haven't already).
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

Run the application locally:
```bash
flet run main.py
```

## 📱 Building for Android

Habito-do is ready to be compiled into an APK for Android devices.

**Prerequisites**:
- Flutter SDK installed and in `PATH`.
- Android SDK Command-line Tools.

**Build Command**:
```powershell
flet build apk --product-name "Habito-do"
```

> For a detailed step-by-step verification guide, please read [APK_Guide.md](APK_Guide.md).

## 📂 Project Structure

- `main.py`: The core application logic and UI.
- `assets/`: Contains application icons and static resources.
- `tasks.json`: Local storage for your to-do items (auto-generated).
