# Face Recognition Attendance System

An AI-driven attendance management system that leverages real-time face recognition to automate attendance tracking. The application eliminates manual processes and enhances accuracy using computer vision techniques.

---

## Overview

This project implements a real-time face recognition pipeline integrated with a graphical user interface to provide a seamless attendance experience. The system captures facial data, encodes it, and matches it against registered users to record attendance with timestamps.

The solution is lightweight, efficient, and does not rely on a database, making it easy to deploy and maintain.

---

## Key Features

- Real-time face detection and recognition  
- Automated attendance logging with date and time  
- Employee face registration system  
- GUI-based application for ease of use  
- CSV-based storage (no database dependency)  
- Multi-user support  

---

## Technology Stack

- **Programming Language:** Python  
- **Computer Vision:** OpenCV, face_recognition  
- **GUI Framework:** Kivy  
- **Data Handling:** Pandas, NumPy  

---

## System Architecture

1. Face images are captured and stored locally  
2. Facial encodings are generated using the face_recognition library  
3. Live video feed is processed using OpenCV  
4. Detected faces are compared with stored encodings  
5. Recognized users are marked present in a CSV file with timestamps  

---

## Project Structure
attendance-system/
│── dataset/ # Registered face images
│── main.py # Application entry point
│── *.csv # Daily attendance records
│── README.md # Documentation

### Install dependencies
pip install opencv-python face-recognition numpy pandas kivy matplotlib

## Usage

1. Launch the application:

python main.py


2. Login to access the system  

3. Register employee faces:
   - Enter employee name  
   - Capture face via webcam  

4. Start attendance:
   - Enable camera  
   - System detects and marks attendance automatically  

---

## Output

Attendance is recorded in CSV format with the following structure:

| Name | Date | Time |
|------|------|------|

Files are generated daily using the format:

YYYY-MM-DD.csv

## License

This project is intended for academic and learning purposes.
