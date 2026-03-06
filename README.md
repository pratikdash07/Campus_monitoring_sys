# Campus Monitoring System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-red)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20Dashboard-ff4b4b)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

A **computer vision–based real-time crowd monitoring and anomaly detection system** designed for campus environments.
The system detects people and vehicles, analyzes crowd density within defined regions, and generates alerts when thresholds are exceeded.

It supports **web-based monitoring dashboards, CLI-based processing, batch analysis, and real-time webcam monitoring**, making it suitable for security, operations, and research use cases.

---

# Table of Contents

* Overview
* Key Features
* Technology Stack
* System Architecture
* Project Structure
* Installation
* Configuration
* Usage
* Web Interface
* Command Line Interface
* Output
* Database Schema
* Performance Notes
* Testing and Validation
* Customization
* Troubleshooting
* Future Enhancements
* Contribution Guidelines
* License

---

# Overview

The **Campus Monitoring System** is an AI-powered surveillance analytics tool that uses **YOLOv8 object detection** and **region-based crowd analysis** to monitor activity in campus environments.

It can detect:

* People
* Bicycles
* Cars
* Motorcycles
* Buses
* Trucks

The system then analyzes **crowd density within defined regions** such as entrances or cafeterias and generates alerts when the number of detected objects exceeds configured limits.

Key capabilities include:

* Real-time monitoring
* Crowd density analysis
* Automatic anomaly alerts
* Video annotation and recording
* Historical data storage

The project supports both **command-line execution and an interactive Streamlit dashboard**.

---

# Key Features

### Real-time People Detection

YOLOv8 detects people and other objects in frames with a **35% confidence threshold**.

### Multi-Class Object Detection

Detects multiple object classes:

* Person
* Bicycle
* Car
* Motorcycle
* Bus
* Truck

### Region-Based Monitoring

Users can define regions such as:

* Entrance
* Cafeteria
* Hallway
* Parking Area

Each region can have **maximum capacity thresholds**.

---

### Anomaly Detection

When the number of objects in a region exceeds its limit, the system triggers alerts.

Example:

```
Entrance threshold: 10 people
Detected: 14 people
→ Alert triggered
```

---

### Alert System

Alerts include:

* Console notifications
* Log file entries

Features:

* Configurable cooldown (default: **60 seconds**)
* Prevents alert spam

---

### Data Persistence

All detections and alerts are stored in an **SQLite database**, including:

* Timestamp
* Region
* Detection count
* Video source

---

### Batch Processing

The system can process:

* Single images
* Video files
* Entire directories

---

### Multiple Input Sources

Supported input types:

* Webcam (index `0`)
* Video files
* Image files
* RTSP camera streams

---

### Web Dashboard

A **Streamlit-based dashboard** provides:

* Upload interface
* Real-time monitoring
* Alert visualization
* Crowd statistics

---

### Video Output

Processed videos include:

* Bounding boxes
* Region overlays
* Object counts

Saved in the `output/` directory.

---

### Flexible Configuration

All settings are managed using a **YAML configuration file**, allowing easy customization without modifying code.

---

# Technology Stack

### Core Machine Learning

* **YOLOv8 (Ultralytics)** – Real-time object detection

### Computer Vision

* **OpenCV 4.7+**

### Data Processing

* **NumPy**
* **Pandas**

### Web Interface

* **Streamlit**

### Database

* **SQLite3**

### Image Processing

* **Pillow**

### Visualization

* **Matplotlib**

### Configuration Management

* **PyYAML**

---

# System Architecture

The monitoring pipeline follows a structured workflow:

```
Input Source
   ↓
Frame Extraction
   ↓
YOLOv8 Object Detection
   ↓
Region-Based Analysis
   ↓
Anomaly Detection
   ↓
Alert Generation
   ↓
Database Storage
   ↓
Visualization (Streamlit Dashboard)
```

Each component is modular, enabling easy extension and testing.

---

# Project Structure

```
├── src/
│   ├── detection/          # YOLOv8 object detection module
│   │   └── detector.py     # ObjectDetector class
│   │
│   ├── analysis/           # Region-based analysis module
│   │   └── analyzer.py     # RegionAnalyzer class
│   │
│   ├── alert/              # Alert management module
│   │   └── alerter.py      # AlertManager class
│   │
│   ├── database/           # Data persistence module
│   │   └── db_manager.py   # DatabaseManager class
│   │
│   ├── interface/          # Streamlit web interface
│   │   └── app.py
│   │
│   └── utils/              # Utility modules
│       └── config_loader.py
│
├── data/
│   ├── config/
│   │   └── config.yaml     # Main configuration file
│   ├── videos/             # Input video storage
│   └── images/             # Input image storage
│
├── output/                 # Processed annotated files
├── logs/                   # Alert logs
│
├── main.py                 # Core processing pipeline
├── run.py                  # Application launcher
├── setup.py                # Project setup
├── requirements.txt        # Dependencies
└── README.md
```

---

# Installation

### 1. Prerequisites

* Python **3.8 or higher**
* pip package manager

---

### 2. Clone Repository

```
git clone <repository-url>
cd campus_monitoring_system
```

---

### 3. Create Virtual Environment

Windows

```
python -m venv venv
venv\Scripts\activate
```

Linux / macOS

```
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install Dependencies

```
pip install -r requirements.txt
```

---

### 5. Run Setup

```
python setup.py
```

This step prepares directories and downloads required resources.

---

# Configuration

Configuration is managed through:

```
data/config/config.yaml
```

Example configuration:

```
detection:
  model: "yolov8m.pt"
  confidence: 0.35
  classes:
    - person
    - bicycle
    - car
    - motorcycle
    - bus
    - truck

analysis:
  regions:
    entrance:
      max: 10
    cafeteria:
      max: 30

alert:
  enabled: true
  cooldown: 60

database:
  path: "data/monitoring.db"
```

---

# Usage

The system supports **two modes**:

1. Web Dashboard
2. Command Line Interface

---

# Web Interface (Recommended)

Run:

```
python run.py --mode ui
```

This launches a **Streamlit dashboard** in your browser.

Features:

* Upload videos or images
* Real-time object detection
* Crowd density analysis
* Alert history
* Visual analytics

---

# Command Line Interface

Run:

```
python run.py --mode cli --source <source>
```

### Examples

Webcam monitoring

```
python run.py --mode cli --source 0
```

Process video

```
python run.py --mode cli --source "path/to/video.mp4"
```

Process image

```
python run.py --mode cli --source "image.jpg" --image
```

Batch process folder

```
python run.py --mode cli --source "data/videos/" --batch
```

---

# Output

### Annotated Videos

Saved to:

```
output/processed_<filename>
```

Includes:

* Bounding boxes
* Region overlays
* Object counts

---

### Database

Stored in:

```
data/monitoring.db
```

Contains detection records and alerts.

---

### Logs

Alert logs stored at:

```
logs/alerts.log
```

---

# Database Schema

The database contains **three tables**.

### detections

Stores detection data.

Fields:

* timestamp
* total_count
* total_people
* video_source
* detection_data (JSON)

---

### alerts

Stores anomaly alerts.

Fields:

* timestamp
* region
* count
* max_count
* message
* video_source

---

### videos

Stores video statistics.

Fields:

* filename
* processed_timestamp
* total_frames
* duration_seconds
* avg_people_count

---

# Performance Notes

Typical system performance:

* ~ **1.2 FPS processing speed**
* ~ **600ms per frame detection**
* GPU acceleration supported
* CPU fallback enabled

Optimization:

Video mode processes **every 5th frame** to maintain near real-time performance.

---

# Testing and Validation

The system has been tested with:

* Campus surveillance footage
* 2162 video frames
* Multiple object classes

Results:

* Accurate people detection
* Correct region-based counting
* Proper alert triggering
* Database records stored successfully
* Annotated output videos generated

---

# Customization

Users can easily customize:

* Detection confidence threshold
* Region coordinates
* Crowd limits per region
* YOLO model version
* Alert cooldown duration
* Alert message format

All customization can be done via **config.yaml**.

---

# Troubleshooting

### YOLO model not found

The model downloads automatically on first run.

If not:

```
pip install ultralytics
```

---

### Webcam not detected

Ensure:

* Camera index is correct
* No other application is using the camera

Try:

```
--source 1
```

---

### Streamlit not launching

Install Streamlit manually:

```
pip install streamlit
```

---

### Slow performance

Possible solutions:

* Use GPU acceleration
* Switch to smaller model

Example:

```
yolov8n.pt
```

---

# Future Enhancements

Planned improvements:

* Multi-camera monitoring
* REST API integration
* Email and SMS alerts
* Crowd density heatmaps
* Historical analytics dashboard
* GPU optimization
* Distributed monitoring architecture

---

# Contribution Guidelines

Contributions are welcome.

Steps:

1. Fork the repository
2. Create a feature branch

```
git checkout -b feature-name
```

3. Commit changes

```
git commit -m "Add new feature"
```

4. Push to branch

```
git push origin feature-name
```

5. Open a Pull Request

Please ensure:

* Code is documented
* Tests pass
* Features are modular

---

# License

This project is licensed under the **MIT License**.

---

# Author

Pratik Dash
KIIT
Built using **Python, YOLOv8, and Streamlit** for real-time intelligent monitoring.
