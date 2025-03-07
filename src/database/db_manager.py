import sqlite3
import json
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, config):
        self.db_path = config['database']['path']
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database and tables if they don't exist"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
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
    
    def save_detection(self, analysis_results, detections, video_source="unknown"):
        """Save detection and analysis results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        total_count = analysis_results['total_count']
        total_people = analysis_results.get('total_people', 0)
        
        detection_data = json.dumps({
            'counts': analysis_results['counts'],
            'anomalies': analysis_results['anomalies'],
            'detections': [
                {
                    'class_name': d['class_name'],
                    'confidence': d['confidence'],
                    'center': d['center']
                } for d in detections
            ]
        })
        
        cursor.execute(
            'INSERT INTO detections (timestamp, total_count, total_people, video_source, detection_data) VALUES (?, ?, ?, ?, ?)',
            (timestamp, total_count, total_people, video_source, detection_data)
        )
        
        conn.commit()
        conn.close()
    
    def save_alerts(self, alerts, video_source="unknown"):
        """Save triggered alerts to database"""
        if not alerts:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for region, alert in alerts.items():
            cursor.execute(
                'INSERT INTO alerts (timestamp, region, count, max_count, message, video_source) VALUES (?, ?, ?, ?, ?, ?)',
                (alert['timestamp'], alert['region'], alert['count'], alert['max_count'], alert['message'], video_source)
            )
        
        conn.commit()
        conn.close()
    
    def save_video_stats(self, filename, total_frames, duration_seconds, avg_people_count):
        """Save video processing statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        cursor.execute(
            'INSERT INTO videos (filename, processed_timestamp, total_frames, duration_seconds, avg_people_count) VALUES (?, ?, ?, ?, ?)',
            (filename, timestamp, total_frames, duration_seconds, avg_people_count)
        )
        
        conn.commit()
        conn.close()
    
    def get_recent_detections(self, limit=100):
        """Get recent detection records"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM detections ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_recent_alerts(self, limit=100):
        """Get recent alert records"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_processed_videos(self, limit=100):
        """Get processed video statistics"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT * FROM videos ORDER BY processed_timestamp DESC LIMIT ?',
            (limit,)
        )
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
