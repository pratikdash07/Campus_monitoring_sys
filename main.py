import cv2
import time
import os
import argparse
import numpy as np
from PIL import Image
from datetime import datetime

from src.utils.config_loader import load_config
from src.detection.detector import ObjectDetector
from src.analysis.analyzer import RegionAnalyzer
from src.alert.alerter import AlertManager
from src.database.db_manager import DatabaseManager

def process_image(image_path, detector, analyzer, alerter, db_manager):
    """Process a single image file"""
    print(f"Processing image: {image_path}")
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image {image_path}")
        return
    
    # Detect objects
    detections, detection_frame = detector.detect(image)
    
    # Analyze detections
    analysis_results, analysis_frame = analyzer.analyze(detections, detection_frame)
    
    # Check for alerts
    alerts = alerter.check_and_alert(analysis_results)
    
    # Save to database
    db_manager.save_detection(analysis_results, detections, os.path.basename(image_path))
    if alerts:
        db_manager.save_alerts(alerts, os.path.basename(image_path))
    
    # Display results
    print(f"Total people detected: {analysis_results['total_people']}")
    for region, count in analysis_results['counts'].items():
        print(f"Region '{region}': {count} people")
    
    # Save output image
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
    cv2.imwrite(output_path, analysis_frame)
    print(f"Processed image saved to: {output_path}")
    
    return analysis_results, analysis_frame

def process_video(video_path, detector, analyzer, alerter, db_manager):
    """Process a video file"""
    print(f"Processing video: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create output video writer
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"processed_{os.path.basename(video_path)}")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Process frames
    frame_count = 0
    people_counts = []
    process_every_n_frames = 5  # Process every 5th frame to speed up
    
    print(f"Total frames: {total_frames}")
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        frame_count += 1
        
        # Process every nth frame
        if frame_count % process_every_n_frames == 0:
            # Detect objects
            detections, detection_frame = detector.detect(frame)
            
            # Analyze detections
            analysis_results, analysis_frame = analyzer.analyze(detections, detection_frame)
            
            # Check for alerts
            alerts = alerter.check_and_alert(analysis_results)
            
            # Save to database (only save every 30th processed frame to avoid database bloat)
            if frame_count % (process_every_n_frames * 30) == 0:
                db_manager.save_detection(analysis_results, detections, os.path.basename(video_path))
                if alerts:
                    db_manager.save_alerts(alerts, os.path.basename(video_path))
            
            # Store people count
            people_counts.append(analysis_results['total_people'])
            
            # Write frame to output video
            out.write(analysis_frame)
            
            # Print progress
            if frame_count % (process_every_n_frames * 20) == 0:
                elapsed_time = time.time() - start_time
                frames_processed = frame_count // process_every_n_frames
                fps_processing = frames_processed / elapsed_time if elapsed_time > 0 else 0
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames}) - Processing speed: {fps_processing:.2f} fps")
        else:
            # Write original frame to output video
            out.write(frame)
    
    # Clean up
    cap.release()
    out.release()
    
    # Save video stats
    if people_counts:
        avg_people = sum(people_counts) / len(people_counts)
        duration = total_frames / fps if fps > 0 else 0
        db_manager.save_video_stats(os.path.basename(video_path), total_frames, duration, avg_people)
    
    # Print summary
    print("\nVideo Processing Summary:")
    print(f"Total frames: {total_frames}")
    print(f"Processed frames: {len(people_counts)}")
    
    if people_counts:
        print(f"Average people count: {sum(people_counts) / len(people_counts):.2f}")
        print(f"Maximum people count: {max(people_counts)}")
    
    print(f"Processed video saved to: {output_path}")
    
    return people_counts

def process_directory(directory, detector, analyzer, alerter, db_manager, file_type="image"):
    """Process all images or videos in a directory"""
    if file_type == "image":
        extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    else:  # video
        extensions = ['.mp4', '.avi', '.mov', '.mkv']
    
    files = [os.path.join(directory, f) for f in os.listdir(directory) 
             if os.path.isfile(os.path.join(directory, f)) and 
             any(f.lower().endswith(ext) for ext in extensions)]
    
    if not files:
        print(f"No {file_type} files found in {directory}")
        return
    
    print(f"Found {len(files)} {file_type} files in {directory}")
    
    for i, file_path in enumerate(files):
        print(f"\nProcessing {i+1}/{len(files)}: {file_path}")
        
        if file_type == "image":
            process_image(file_path, detector, analyzer, alerter, db_manager)
        else:  # video
            process_video(file_path, detector, analyzer, alerter, db_manager)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Campus Monitoring System')
    parser.add_argument('--source', type=str, default='0', help='Source (0 for webcam, path for file or directory)')
    parser.add_argument('--config', type=str, default='data/config/config.yaml', help='Path to configuration file')
    parser.add_argument('--image', action='store_true', help='Process as image instead of video')
    parser.add_argument('--batch', action='store_true', help='Process all files in directory')
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize components
    detector = ObjectDetector(config)
    analyzer = RegionAnalyzer(config)
    alerter = AlertManager(config)
    db_manager = DatabaseManager(config)
    
    # Process based on source type
    source = args.source
    
    # Check if source is a webcam
    if source.isdigit():
        source = int(source)
        print(f"Opening webcam {source}")
        
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"Error: Could not open webcam {source}")
            return
        
        print("Press 'q' to quit")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("Error reading from webcam")
                break
            
            # Detect objects
            detections, detection_frame = detector.detect(frame)
            
            # Analyze detections
            analysis_results, analysis_frame = analyzer.analyze(detections, detection_frame)
            
            # Check for alerts
            alerter.check_and_alert(analysis_results)
            
            # Display results
            cv2.imshow('Campus Monitoring', analysis_frame)
            
            # Break loop on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
    
    # Check if source is a directory and batch processing is enabled
    elif os.path.isdir(source) and args.batch:
        process_directory(source, detector, analyzer, alerter, db_manager, 
                         "image" if args.image else "video")
    
    # Process single file
    elif os.path.isfile(source):
        if args.image or source.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            process_image(source, detector, analyzer, alerter, db_manager)
        else:
            process_video(source, detector, analyzer, alerter, db_manager)
    
    else:
        print(f"Error: Invalid source {source}")

if __name__ == "__main__":
    main()
