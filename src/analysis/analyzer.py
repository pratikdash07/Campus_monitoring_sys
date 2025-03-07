import cv2
import numpy as np
from datetime import datetime

class RegionAnalyzer:
    def __init__(self, config):
        self.config = config
        self.regions = config['analysis']['regions']
        self.region_counts = {region: 0 for region in self.regions}
        self.anomalies = {region: False for region in self.regions}
        
    def is_point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def get_pixel_coordinates(self, percentage_coords, frame_width, frame_height):
        """Convert percentage coordinates to pixel coordinates"""
        return [[int(x * frame_width / 100), int(y * frame_height / 100)] 
                for x, y in percentage_coords]
    
    def analyze(self, detections, frame=None):
        """
        Analyze detections to count objects in defined regions
        
        Args:
            detections: List of detection dictionaries
            frame: Optional frame to draw regions on
            
        Returns:
            analysis_results: Dictionary with analysis results
            annotated_frame: Frame with regions and counts drawn
        """
        # Reset counts
        self.region_counts = {region: 0 for region in self.regions}
        
        if frame is None:
            frame_height, frame_width = 1000, 1000  # Default values if no frame
        else:
            frame_height, frame_width = frame.shape[:2]
        
        # Count objects in each region
        for detection in detections:
            center = detection['center']
            for region_name, region_data in self.regions.items():
                # Convert percentage coordinates to pixel coordinates
                pixel_polygon = self.get_pixel_coordinates(
                    region_data['coordinates'], frame_width, frame_height)
                
                if self.is_point_in_polygon(center, pixel_polygon):
                    self.region_counts[region_name] += 1
        
        # Check for anomalies
        for region_name, count in self.region_counts.items():
            max_count = self.regions[region_name]['max_count']
            self.anomalies[region_name] = count > max_count
        
        # Prepare results
        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'counts': self.region_counts.copy(),
            'anomalies': self.anomalies.copy(),
            'total_count': sum(self.region_counts.values()),
            'total_people': sum(1 for d in detections if d['class_name'] == 'person')
        }
        
        # Draw regions on frame if provided
        annotated_frame = None
        if frame is not None:
            annotated_frame = frame.copy()
            for region_name, region_data in self.regions.items():
                # Convert percentage coordinates to pixel coordinates
                pixel_polygon = self.get_pixel_coordinates(
                    region_data['coordinates'], frame_width, frame_height)
                
                polygon = np.array(pixel_polygon, np.int32)
                polygon = polygon.reshape((-1, 1, 2))
                
                # Choose color based on anomaly status
                color = (0, 0, 255) if self.anomalies[region_name] else (0, 255, 0)
                
                cv2.polylines(annotated_frame, [polygon], True, color, 2)
                
                # Add count text
                centroid = np.mean(pixel_polygon, axis=0).astype(int)
                text = f"{region_name}: {self.region_counts[region_name]}"
                cv2.putText(annotated_frame, text, tuple(centroid), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add total count
            total_text = f"Total People: {analysis_results['total_people']}"
            cv2.putText(annotated_frame, total_text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return analysis_results, annotated_frame
