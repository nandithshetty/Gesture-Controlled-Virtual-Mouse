# Gesture Controlled Virtual Mouse &nbsp;[![](https://img.shields.io/badge/python-3.8.5-blue.svg)](https://www.python.org/downloads/) [![platform](https://img.shields.io/badge/platform-windows-green.svg)](https://github.com/nandithshetty/Gesture-Controlled-Virtual-Mouse) 

Gesture Controlled Virtual Mouse makes human-computer interaction simple and touchless by leveraging hand gestures and voice commands. All input/output operations can be virtually controlled using static and dynamic hand gestures along with an integrated, offline-capable voice assistant named **Max**. 

This project makes use of state-of-the-art Computer Vision and machine learning pipelines to track and recognize hand landmarks, working smoothly on standard webcams without any specialized hardware requirements. It leverages the **Google MediaPipe Hands** framework to predict 21 3D hand coordinates in real-time, mapping joint geometry to system events via a multi-threaded Python backend and a sleek, glassmorphic HTML5/CSS front-end built using **Eel**.

---

## Key Features

### 🌟 Hand Gesture Recognition:
* **Neutral Gesture (Palm):** Halts/stops current gesture actions.
* **Move Cursor:** Moves the cursor based on the index and middle fingertip midpoint, optimized using a custom exponential dampening filter to filter **99.6%** of natural micro-tremors for pixel-perfect navigation.
* **Left Click:** Gesture utilizing the middle finger to trigger a mouse click.
* **Right Click:** Gesture utilizing the index finger to trigger a right-click.
* **Double Click:** Quick double-tap gesture mapping.
* **Scrolling:** Dynamic horizontal and vertical scroll control using pinch distance.
* **Drag and Drop:** Clenched fist gesture (`FIST`) to click and drag files.
* **Volume & Brightness Sliders:** Pinch gestures to smoothly adjust volume and display brightness.

### 🚀 Advanced Edge-Triggered Gestures (New):
* **Rock On (`ROCK`):** Mute/Unmute system audio volume.
* **Pinky Open (`PINKY`):** Captures and saves a system screenshot.
* **Ring Open (`RING`):** Instantly triggers native Windows Lock Workstation (`user32.dll` API).
* **Three/Four Fingers (`THREE_FINGERS` / `LAST3`):** Triggers `Alt + Tab` overlay to cycle between active application windows.

> [!NOTE]
> All advanced shortcuts utilize edge-triggered state flags to ensure the action fires **exactly once** per pose transition, preventing accidental continuous triggering.

### 🎙️ Voice Assistant (Max):
* **Offline Processing:** Runs 100% offline using Microsoft's SAPI5 local speech engine, bypassing cloud latency and internet dependencies.
* **Dynamic Audio Calibration:** Employs a noise listener worker thread with active energy damping to auto-calibrate mic sensitivity dynamically.
* **Interactive Commands:**
  * *"Max, open gesture controller"* — Automatically launches webcam tracking.
  * *"Max, close gesture controller"* — Stops the tracking loop.
  * *"Max, search {query}"* — Direct Google search.
  * *"Max, find location"* — Prompts for a location and opens it on Google Maps.
  * *"Max, copy / paste"* — Dynamic clipboard control.
  * *Companion Skills:* Weather updates, coin flips, and programmer jokes.
* **Dynamic Mic Swapping:** Features a glassmorphic GUI dropdown allowing users to hot-swap active recording devices on the fly.

---

## Getting Started

### Prerequisites
* **Operating System:** Windows 10/11
* **Python Version:** 3.8 to 3.10
* **Anaconda Distribution:** Recommended for PyAudio installation.

### Installation & Run Procedure

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/nandithshetty/Gesture-Controlled-Virtual-Mouse.git
   cd Gesture-Controlled-Virtual-Mouse/src
   ```

2. **Create and Activate Environment:**
   ```bash
   conda create --name gest python=3.8.5
   conda activate gest
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r ../requirements.txt
   conda install PyAudio
   conda install pywin32
   ```

4. **Running the Application:**

   * **Run the Voice Assistant & GUI (Max):**
     ```bash
     python Max.py
     ```
     *(Say "Max, open gesture controller" to launch hand tracking)*

   * **Run the Gesture Tracker Standalone:**
     ```bash
     python Gesture_Controller.py
     ```

---

## Developer & Author
* **Nishanth Shetty** — [GitHub](https://github.com/nandithshetty) | [LinkedIn](https://www.linkedin.com/in/nishanth-shetty-435a48291/)
