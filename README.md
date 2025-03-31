# Campus Monitoring System

A computer vision-based system for monitoring and analyzing crowd density in campus environments. This system uses YOLOv8 object detection to count people in different regions, detect abnormal gatherings, and send alerts when thresholds are exceeded.

## Features

- Real-time people detection and counting
- Region-based monitoring for specific areas
- Anomaly detection for unusual gatherings
- Alert system for security notifications
- Support for images, videos, webcams, and RTSP streams
- Database storage of detection results and alerts
- User-friendly web interface
- Batch processing capabilities


## Requirements

- Python 3.8+
- OpenCV
- YOLOv8 (via Ultralytics)
- NumPy
- Pandas
- Streamlit
- SQLite

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/campus_monitoring_system.git
cd campus_monitoring_system

text

2. Create a virtual environment:
python -m venv venv
venv\Scripts\activate # On Windows
source venv/bin/activate # On macOS/Linux

text

3. Install dependencies:
pip install -r requirements.txt

text

4. Run the setup script:
python setup.py

text

## Usage

### Web Interface

Launch the Streamlit web interface:
python run.py --mode ui

text

### Command Line

Process a video file:
python run.py --mode cli --source path/to/video.mp4

text

Process an image:
python run.py --mode cli --source path/to/image.jpg --image

text

Process all videos in a directory:
python run.py --mode cli --source path/to/directory --batch

text

### Local File Processing

To process all images and videos in the data directories:
python process_local_files.py

text

To process only images:
python process_local_files.py --type images

text

To process only videos:
python process_local_files.py --type videos

text

## Configuration

Edit `data/config/config.yaml` to customize:
- Detection settings (model, confidence threshold, classes)
- Monitoring regions and thresholds
- Alert settings
- Database configuration

Example configuration:
detection:
model: "yolov8m.pt" # Model to use (n=nano, s=small, m=medium, l=large, x=xlarge)
confidence: 0.35 # Confidence threshold
classes: # Classes to detect
person: 0

analysis:
regions: # Monitoring regions (as percentages of frame)
entrance:
coordinates: [,,,]
max_count: 10
cafeteria:
coordinates: [,,,]
max_count: 30

alert:
enabled: true
cooldown: 60 # Seconds between alerts
methods:
console: true # Print to console
log: true # Write to log file

text

## Implementation Details

- Object detection is performed using YOLOv8 from the Ultralytics library
- Region monitoring uses polygon-based area definitions
- Alerts are triggered when the count in a region exceeds the defined threshold
- Results are stored in an SQLite database for historical analysis
- The web interface is built with Streamlit for easy interaction

## License

[MIT License](LICENSE)
