# HandFlowHomeMate: Gesture-Controlled Smart Home


A portable AI-based smart home system that lets you control devices using simple hand gestures via webcam. Built with Python, OpenCV, MediaPipe, and Arduino.

## 💡 Features

- 🤘🏻✌🏻🤘🏻 Unlock gesture to activate the system
- 👆 1 Finger: Toggle Light 1  
- ✌️ 2 Fingers: Toggle Light 2  
- 🤟 3 Fingers: TV Toggle  
- ✋ 4 Fingers: Curtains open/close  
- 🖐️ 5 Fingers: Fan toggle (via servo)  
- ✊ Fist: Door lock/unlock  
- 👋 Wave: Master control for all devices

## 🔌 Hardware Used

- Arduino UNO
- Raspberry Pi / PC
- 5V LED lights
- Servo motor for curtains
- Solenoid lock
- 5V fan (Servo simulated)
- Relay modules
- Webcam

## 🔧 Software Stack

- Python 3.12
- OpenCV
- MediaPipe
- PySerial

## 🧠 AI Module

Uses `MediaPipe` hand tracking to count raised fingers and detect wave motion.

## ⚙️ Setup Instructions

1. Clone this repo
2. Install dependencies with:
  pip install -r requirements.txt
3. Upload `Arduino_Code.ino` to your Arduino board
4. Run `app.py` and show gestures!

