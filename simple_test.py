import os
import cv2
import numpy as np
from src.utils.config_loader import load_config
from src.detection.detector import ObjectDetector

def run_simple_test():
    # Create a simple test image with a solid color
    test_image = np.ones((640, 640, 3), dtype=np.uint8) * 255
    
    # Load configuration
    print("Loading configuration...")
    config = load_config()
    
    # Initialize detector
    print("Initializing detector...")
    detector = ObjectDetector(config)
    
    # Test the detector with the blank image
    print("Testing detector with blank image...")
    detections, _ = detector.detect(test_image)
    
    print(f"Detection test complete. Found {len(detections)} objects.")
    print("If you see this message without errors, your basic setup is working!")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)

if __name__ == "__main__":
    run_simple_test()
