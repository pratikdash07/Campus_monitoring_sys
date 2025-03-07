import cv2
import numpy as np
from ultralytics import YOLO

class ObjectDetector:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.confidence = config['detection']['confidence']
        self.classes = config['detection']['classes']
        self.class_ids = list(self.classes.values())
        self._load_model(config['detection']['model'])
        
    def _load_model(self, model_name):
        """Load the YOLO model"""
        try:
            self.model = YOLO(model_name)
            print(f"Successfully loaded model: {model_name}")
        except Exception as e:
            print(f"Error loading model {model_name}: {e}")
            print("Falling back to yolov8n.pt")
            self.model = YOLO("yolov8n.pt")
        
    def detect(self, frame):
        """
        Detect objects in a frame
        
        Args:
            frame: Image as numpy array (BGR format)
            
        Returns:
            detections: List of dictionaries with detection results
            annotated_frame: Frame with bounding boxes drawn
        """
        if frame is None or frame.size == 0:
            return [], frame
            
        results = self.model(frame, conf=self.confidence, classes=self.class_ids)
        
        # Process results
        detections = []
        for result in results:
            boxes = result.boxes.cpu().numpy()
            for i, box in enumerate(boxes):
                x1, y1, x2, y2 = box.xyxy[0].astype(int)
                confidence = box.conf[0]
                class_id = int(box.cls[0])
                
                # Get class name from class id
                class_name = None
                for name, id in self.classes.items():
                    if id == class_id:
                        class_name = name
                        break
                
                detection = {
                    'class_id': class_id,
                    'class_name': class_name,
                    'confidence': float(confidence),
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                }
                detections.append(detection)
        
        # Get annotated frame
        annotated_frame = results[0].plot() if results and len(results) > 0 else frame
        
        return detections, annotated_frame
