# 🐍 Snake Game

[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational)](https://docs.python.org/3/library/tkinter.html)
[![Pillow](https://img.shields.io/badge/Image%20Processing-Pillow-yellow)](https://pypi.org/project/Pillow/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Release](https://img.shields.io/github/v/release/HusnainRaza313/Snake-Game-Python?label=Latest%20Release)](https://github.com/HusnainRaza313/Snake-Game-Python/releases/latest)

A modern and feature-rich **Snake Game** built with **Python and Tkinter**.

This desktop game includes custom graphics, background music, sound effects, high-score tracking, pause/resume functionality, persistent settings, and a Windows installer created with **Inno Setup**.

## 📸 Game Preview

<p align="center">
  <img src="game_screenshot.png" alt="Snake Game Screenshot" width="520">
</p>

## 📥 Download

### 🪟 Windows

Download the latest Windows installer from **GitHub Releases**:

<p align="center">
  <a href="https://github.com/HusnainRaza313/Snake-Game-Python/releases/latest">
    <img src="https://img.shields.io/badge/⬇️%20Download%20Snake%20Game-brightgreen?style=for-the-badge" alt="Download Snake Game">
  </a>
</p>

The current release provides the Windows installer **`Snake.Game.Setup.exe`**.

> **Note:** The packaged application is currently available for Windows.

## 🎮 Features

- 🐍 Classic Snake gameplay
- 🎯 Score system
- 🏆 Persistent high-score system
- 💾 Local game-data saving
- 🎵 Background music
- 🔊 Sound effects
- ⏸️ Pause and resume
- 🔄 Restart / Play Again
- 🎨 Custom graphics and modern UI
- 🖼️ Custom buttons and game assets
- 🚧 Wall collision detection
- 💀 Game-over screen
- ⚙️ Saved music and sound settings
- 📦 Windows installer
- 🪟 Standalone Windows application

## 🛠️ Technologies

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Tkinter** | Desktop graphical user interface |
| **Pillow (PIL)** | Image processing and custom graphics |
| **JSON** | Saving settings and high scores |
| **Winsound** | Windows sound effects |
| **PyInstaller** | Packaging the Python application |
| **Inno Setup** | Creating the Windows installer |

## 📂 Project Structure

```text
Snake-Game-Python/
│
├── snake_game.py
├── snake_game.pyproj
├── Snake Game.spec
├── Snake_game.iss
├── requirements.txt
├── .gitignore
│
├── background_music.wav
├── valid_icon.ico
├── game_screenshot.png
│
├── best_badge.png
├── glass_card.png
├── score_badge.png
│
├── pause_btn_hover.png
├── pause_btn_normal.png
├── play_again_btn_hover.png
├── play_again_btn_normal.png
├── resume_btn_hover.png
├── resume_btn_normal.png
│
├── start_background.png
├── start_btn_hover.png
├── start_btn_normal.png
│
├── snake_background.png
├── snake_body.png
├── snake_food.png
└── snake_head.png
```

## ▶️ Run From Source

If you want to run the game from source code:

### 1. Install Python

Install Python 3.x on your Windows computer.

### 2. Clone the Repository

```bash
git clone https://github.com/HusnainRaza313/Snake-Game-Python.git
```

### 3. Open the Project Folder

```bash
cd Snake-Game-Python
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Game

```bash
python snake_game.py
```

## 📦 Build the Application

The repository includes a PyInstaller specification file:

```text
Snake Game.spec
```

Build the application with:

```bash
pyinstaller "Snake Game.spec"
```

The generated application can then be packaged into a Windows installer using **Inno Setup**.

## 💾 Game Data

The game stores user data locally, including:

- High score
- Game settings
- Music preference
- Sound-effect preference

The data is stored in the user's local application-data folder rather than inside the source repository.

## 🎯 Project Goals

This project was created to practice and demonstrate:

- Python programming
- GUI development
- Game logic
- File handling
- Audio integration
- Image processing
- Application packaging
- Windows software distribution

## 🚀 Future Improvements

- Multiple difficulty levels
- Additional game modes
- More food types
- Special power-ups
- Leaderboard system
- More visual effects
- Cross-platform support
- Online high-score system

## 👨‍💻 Developer

**Muhammad Husnain Raza**

ADP Computer Science Student

**Interests:**

`Python` · `C++` · `Flutter` · `Web Development` · `Artificial Intelligence`

## ⭐ Support

If you like this project, consider giving the repository a ⭐ on GitHub.

Feedback and suggestions are welcome.

## 📄 License

This project is shared for **educational and personal use**. No separate open-source license is currently included.

---

<p align="center">
  Built with 🐍 Python &nbsp;•&nbsp; Developed by <strong>Muhammad Husnain Raza</strong>
</p>
