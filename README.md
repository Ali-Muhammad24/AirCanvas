# 🎨 AirCanvas - Gesture Controlled Drawing App

AirCanvas is an AI-powered virtual drawing application that allows users to draw in the air using hand gestures. It uses computer vision and hand tracking to create a completely touch-free drawing experience by mapping 21 hand landmarks in real-time.

---

## 🚀 Features

### ✍️ Drawing & AI Tracking
- **AI-Powered:** Uses **MediaPipe** to track the index finger tip (Landmark 8) for real-time drawing.
- **Smooth Strokes:** High-frequency coordinate mapping from normalized (0-1) space to pixel space.

### 🎨 Color Selection
- **Dynamic Palette:** Multiple colors available in an on-screen toolbar.
- **Easy Switch:** Change color by simply touching the color circles with your fingertip.

### 📏 Brush Thickness Control
- **Interactive UI:** Different pen thickness levels selectable via a dedicated bar.
- **Visual Feedback:** Adjustable circles show the selected brush size.

### 🧽 Eraser Mode
- **Smart Toggle:** Activated automatically when **Index + Middle fingers** are raised.
- **Efficient Cleaning:** Uses a thicker stroke for easy erasing with a visual cursor.

### 🗑️ Clear Canvas
- **On-Screen Button:** A dedicated "CLEAR ALL" button at the top-right.
- **Debounce Logic:** Implemented a 1-second time delay (`time.time()`) to prevent accidental double-clears.

### ✋ Palm Detection (Smart Control)
- **Advanced Math:** Drawing only works when your **palm is facing the camera**.
- **Vector Logic:** Uses the **Vector Cross Product** of wrist-to-finger landmarks to calculate the hand's "Normal Vector" ($normal[2] > 0$).

### ✍️ Air Signature (Save Feature)
- **Gesture Trigger:** Show **4 fingers** to automatically trigger the save function.
- **File Management:** Saves drawings as unique image files (e.g., `canvas_1.png`) to prevent overwriting.

---

## 🧠 Technologies Used
- **Python:** Core programming language.
- **OpenCV:** For image processing, UI overlays, and webcam feed.
- **MediaPipe:** For AI-based hand landmark detection.
- **NumPy:** For canvas array manipulation and vector mathematics.

---

## 📂 How to Run

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ali-Muhammad24/AirCanvas.git

2. **Install Dependencies:**
   pip install opencv-python mediapipe numpy

3. **Run the App:**
   python airCanvas.py
