# Add this at the top of your setup.py
import sys
print(f"Python path: {sys.executable}")
print(f"sys.path: {sys.path}")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'ultralytics',
        'opencv-python',
        'numpy',
        'pandas',
        'streamlit',
        'pillow',
        'matplotlib',
        'pyyaml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
                print(f"✓ opencv-python is installed (cv2.__version__: {cv2.__version__})")
            elif package == 'pillow':
                from PIL import Image
                import PIL
                print(f"✓ pillow is installed (PIL.__version__: {PIL.__version__})")
            elif package == 'pyyaml':
                import yaml
                print(f"✓ pyyaml is installed (yaml.__version__: {yaml.__version__ if hasattr(yaml, '__version__') else 'unknown'})")
            else:
                __import__(package)
                print(f"✓ {package} is installed")
        except ImportError as e:
            missing_packages.append(package)
            print(f"✗ {package} is NOT installed - Error: {e}")
    
    if missing_packages:
        print("\nSome required packages are missing. Install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

import os
import sys
import subprocess
import sqlite3

def check_dependencies():
    """Check if all required packages are installed"""
    required_imports = {
        'ultralytics': 'ultralytics',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'pandas': 'pandas',
        'streamlit': 'streamlit',
        'PIL': 'pillow',
        'matplotlib': 'matplotlib',
        'yaml': 'pyyaml'
    }
    
    missing_packages = []
    
    for import_name, package_name in required_imports.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name} is installed")
        except ImportError:
            missing_packages.append(package_name)
            print(f"✗ {package_name} is NOT installed")
    
    if missing_packages:
        print("\nSome required packages are missing. Install them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def initialize_database():
    """Initialize the SQLite database"""
    db_path = 'data/monitoring.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        total_count INTEGER,
        total_people INTEGER,
        video_source TEXT,
        detection_data TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        region TEXT,
        count INTEGER,
        max_count INTEGER,
        message TEXT,
        video_source TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        processed_timestamp TEXT,
        total_frames INTEGER,
        duration_seconds REAL,
        avg_people_count REAL
    )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def test_yolo_model():
    """Test if YOLO model can be loaded"""
    try:
        from ultralytics import YOLO
        model_name = 'yolov8n.pt'  # Use nano model for quick testing
        model = YOLO(model_name)
        print(f"Successfully loaded YOLO model: {model_name}")
        return True
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        return False

def main():
    print("Setting up Campus Monitoring System...")
    
    # Check dependencies
    print("\nChecking dependencies:")
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\nPlease install missing dependencies before continuing.")
        return
    
    # Initialize database
    print("\nInitializing database:")
    initialize_database()
    
    # Test YOLO model
    print("\nTesting YOLO model:")
    model_ok = test_yolo_model()
    
    if not model_ok:
        print("\nThere was an issue with the YOLO model. Please check your installation.")
        return
    
    print("\nSetup completed successfully! You can now run the application with:")
    print("- Command line: python main.py")
    print("- Web interface: streamlit run src/interface/app.py")

if __name__ == "__main__":
    main()
