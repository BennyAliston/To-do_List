# How to Build an APK for Habito-do

Building an Android APK from a Flet app requires setting up the Flutter SDK and Android Build Tools. Since `flutter` is not currently installed on your system, please follow these steps:

## 1. Install Flutter SDK
1. Download the Flutter SDK for Windows from the [official website](https://docs.flutter.dev/get-started/install/windows).
2. Extract the zip file to a location like `C:\src\flutter`.
3. Add `C:\src\flutter\bin` to your **Path environment variable**.
   - Search for "Edit the system environment variables" in Windows Search.
   - Click "Environment Variables".
   - Under "User variables", find `Path` and edit it.
   - Add `C:\src\flutter\bin`.

## 2. Install Android SDK Tools
You will need the Android SDK Command-line Tools.
1. Download [Android Studio](https://developer.android.com/studio) (recommended as it installs the SDKs for you).
2. During installation, ensure **Android SDK Build-Tools** and **Android SDK Command-line Tools** are selected.

## 3. Verify Installation
Open a new terminal (Powershell or CMD) and run:
```powershell
flutter doctor
```
Follow any instructions it gives to resolve missing dependencies (like accepting licenses).

## 4. Build the APK
Once `flutter doctor` gives all green checks, navigate to your project folder:
```powershell
cd "c:\Projects\To-do_List\Multi Platform App work in progress"
```
And run the build command with the product name:
```powershell
flet build apk --product-name "Habito-do"
```
This will generate the APK file in the `build/apk` folder, using `icon.png` from the root as the app icon and "Habito-do" as the app name.

> **Note**: The first build can take several minutes as it downloads necessary dependencies.
