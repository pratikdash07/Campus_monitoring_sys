import os
import cv2
import numpy as np
from datetime import datetime

from src.utils.config_loader import load_config
from src.detection.detector import ObjectDetector
from src.analysis.analyzer import RegionAnalyzer
from src.alert.alerter import AlertManager
from src.database.db_manager import DatabaseManager

def test_image_detection(image_path):
    """Test detection on a single image"""
    print(f"Testing detection on image: {image_path}")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return False
    
    # Load configuration
    try:
        config = load_config()
        print("Configuration loaded successfully")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False
    
    # Initialize components
    try:
        detector = ObjectDetector(config)
        analyzer = RegionAnalyzer(config)
        alerter = AlertManager(config)
        db_manager = DatabaseManager(config)
        print("All components initialized successfully")
    except Exception as e:
        print(f"Error initializing components: {e}")
        return False
    
    # Read image
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not read image {image_path}")
            return False
        print(f"Image loaded: {image.shape}")
    except Exception as e:
        print(f"Error reading image: {e}")
        return False
    
    # Detect objects
    try:
        detections, detection_frame = detector.detect(image)
        print(f"Detection successful: {len(detections)} objects detected")
        
        # Count people
        people_count = sum(1 for d in detections if d['class_name'] == 'person')
        print(f"People detected: {people_count}")
        
        # Print all detections
        for i, d in enumerate(detections):
            print(f"  {i+1}. {d['class_name']} (confidence: {d['confidence']:.2f})")
    except Exception as e:
        print(f"Error during detection: {e}")
        return False
    
    # Analyze detections
    try:
        analysis_results, analysis_frame = analyzer.analyze(detections, detection_frame)
        print("Analysis successful")
        print(f"Total people: {analysis_results['total_people']}")
        
        # Print region counts
        for region, count in analysis_results['counts'].items():
            status = "ANOMALY" if analysis_results['anomalies'][region] else "normal"
            print(f"  Region '{region}': {count} people ({status})")
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False
    
    # Check for alerts
    try:
        alerts = alerter.check_and_alert(analysis_results)
        if alerts:
            print(f"Alerts triggered: {len(alerts)}")
        else:
            print("No alerts triggered")
    except Exception as e:
        print(f"Error checking alerts: {e}")
        return False
    
    # Save to database
    try:
        db_manager.save_detection(analysis_results, detections, os.path.basename(image_path))
        if alerts:
            db_manager.save_alerts(alerts, os.path.basename(image_path))
        print("Results saved to database")
    except Exception as e:
        print(f"Error saving to database: {e}")
        return False
    
    # Save output image
    try:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"test_result_{os.path.basename(image_path)}")
        cv2.imwrite(output_path, analysis_frame)
        print(f"Result image saved to: {output_path}")
    except Exception as e:
        print(f"Error saving output image: {e}")
        return False
    
    print("Test completed successfully!")
    return True

if __name__ == "__main__":
    # You can replace this with the path to your test image
    test_image_path = "data/images/test_image.jpg"
    
    # Check if the test image exists, if not, inform the user
    if not os.path.exists(test_image_path):
        print(f"Test image not found at {test_image_path}")
        print("Please place a test image at this location or modify the script to use a different path.")
    else:
        test_image_detection(test_image_path)
