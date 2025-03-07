import streamlit as st
import cv2
import numpy as np
import time
import os
import sys
from PIL import Image
import pandas as pd
from datetime import datetime
import tempfile

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config_loader import load_config
from detection.detector import ObjectDetector
from analysis.analyzer import RegionAnalyzer
from alert.alerter import AlertManager
from database.db_manager import DatabaseManager

def run_streamlit_app():
    st.set_page_config(
        page_title="Campus Monitoring System",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("Campus Monitoring System")
    
    # Load configuration
    config = load_config()
    
    # Initialize components
    detector = ObjectDetector(config)
    analyzer = RegionAnalyzer(config)
    alerter = AlertManager(config)
    db_manager = DatabaseManager(config)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Input source selection
        st.subheader("Input Source")
        source_type = st.radio("Select Input Type", ["Image", "Video", "Webcam", "RTSP Stream"])
        
        if source_type == "Image":
            uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
            process_batch = st.checkbox("Process multiple images")
            
            if process_batch:
                uploaded_files = st.file_uploader("Upload Multiple Images", 
                                                 type=["jpg", "jpeg", "png"], 
                                                 accept_multiple_files=True)
        
        elif source_type == "Video":
            uploaded_file = st.file_uploader("Upload Video", type=["mp4", "avi", "mov"])
            
        elif source_type == "Webcam":
            camera_id = st.number_input("Camera ID", min_value=0, value=0, step=1)
            
        else:  # RTSP Stream
            rtsp_url = st.text_input("RTSP URL", "rtsp://username:password@ip_address:port/stream")
        
        # Detection settings
        st.subheader("Detection Settings")
        confidence = st.slider("Confidence Threshold", 0.1, 1.0, float(config['detection']['confidence']), 0.05)
        detector.confidence = confidence
        
        # Class selection
        st.subheader("Classes to Detect")
        selected_classes = {}
        for name, class_id in config['detection']['classes'].items():
            if st.checkbox(f"{name.capitalize()} (ID: {class_id})", value=True if name == 'person' else False):
                selected_classes[name] = class_id
        
        if selected_classes:
            detector.classes = selected_classes
            detector.class_ids = list(selected_classes.values())
        
        # Process button
        st.subheader("Actions")
        process_button = st.button("Process Input")
        stop_button = st.button("Stop Processing")
    
    # Main content area
    if source_type == "Image" and process_button:
        if uploaded_file:
            # Process single image
            image = Image.open(uploaded_file)
            image_np = np.array(image)
            
            # Convert RGB to BGR (OpenCV format)
            if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            # Detect objects
            detections, detection_frame = detector.detect(image_np)
            
            # Analyze detections
            analysis_results, analysis_frame = analyzer.analyze(detections, detection_frame)
            
            # Check for alerts
            alerts = alerter.check_and_alert(analysis_results)
            
            # Save to database
            db_manager.save_detection(analysis_results, detections, uploaded_file.name)
            if alerts:
                db_manager.save_alerts(alerts, uploaded_file.name)
            
            # Convert BGR back to RGB for display
            display_frame = cv2.cvtColor(analysis_frame, cv2.COLOR_BGR2RGB)
            
            # Display results
            st.image(display_frame, caption="Processed Image", use_container_width=True)
            
            # Display counts
            st.subheader("Detection Results")
            st.write(f"Total People: {analysis_results['total_people']}")
            
            for region, count in analysis_results['counts'].items():
                max_count = config['analysis']['regions'][region]['max_count']
                is_anomaly = analysis_results['anomalies'][region]
                
                if is_anomaly:
                    st.error(f"Region '{region}': {count} people (Exceeds maximum of {max_count})")
                else:
                    st.success(f"Region '{region}': {count} people (Maximum: {max_count})")
        
        elif process_batch and uploaded_files:
            # Process multiple images
            st.subheader("Batch Processing Results")
            
            progress_bar = st.progress(0)
            batch_results = []
            
            for i, file in enumerate(uploaded_files):
                # Process image
                image = Image.open(file)
                image_np = np.array(image)
                
                # Convert RGB to BGR (OpenCV format)
                if len(image_np.shape) == 3 and image_np.shape[2] == 3:
                    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                
                # Detect objects
                detections, _ = detector.detect(image_np)
                
                # Analyze detections
                analysis_results, _ = analyzer.analyze(detections, image_np)
                
                # Save results
                batch_results.append({
                    'filename': file.name,
                    'total_people': analysis_results['total_people'],
                    'regions': analysis_results['counts'],
                    'anomalies': any(analysis_results['anomalies'].values())
                })
                
                # Update progress
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            # Display batch results
            results_df = pd.DataFrame(batch_results)
            st.dataframe(results_df)
            
            # Show summary
            st.subheader("Batch Summary")
            st.write(f"Total images processed: {len(batch_results)}")
            st.write(f"Images with anomalies: {sum(1 for r in batch_results if r['anomalies'])}")
            st.write(f"Average people count: {sum(r['total_people'] for r in batch_results) / len(batch_results):.2f}")
    
    elif source_type == "Video" and process_button and uploaded_file:
        # Save uploaded video to a temporary file
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())
        video_path = tfile.name
        tfile.close()
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            st.error("Error opening video file")
        else:
            # Get video properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create a placeholder for the video
            video_placeholder = st.empty()
            
            # Create a progress bar
            progress_bar = st.progress(0)
            
            # Process video frames
            frame_count = 0
            people_counts = []
            
            # Process every 5th frame to speed up processing
            process_every_n_frames = 5
            
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
                        db_manager.save_detection(analysis_results, detections, uploaded_file.name)
                        if alerts:
                            db_manager.save_alerts(alerts, uploaded_file.name)
                    
                    # Convert BGR to RGB for display
                    display_frame = cv2.cvtColor(analysis_frame, cv2.COLOR_BGR2RGB)
                    
                    # Update video display
                    video_placeholder.image(display_frame, caption=f"Frame {frame_count}/{total_frames}", use_column_width=True)
                    
                    # Update progress bar
                    progress_bar.progress(frame_count / total_frames)
                    
                    # Store people count
                    people_counts.append(analysis_results['total_people'])
            
            # Clean up
            cap.release()
            os.unlink(video_path)
            
            # Save video stats
            if people_counts:
                avg_people = sum(people_counts) / len(people_counts)
                duration = total_frames / fps if fps > 0 else 0
                db_manager.save_video_stats(uploaded_file.name, total_frames, duration, avg_people)
            
            # Display summary
            st.subheader("Video Processing Summary")
            st.write(f"Total frames: {total_frames}")
            st.write(f"Processed frames: {len(people_counts)}")
            
            if people_counts:
                st.write(f"Average people count: {avg_people:.2f}")
                st.write(f"Maximum people count: {max(people_counts)}")
                
                # Plot people count over time
                st.subheader("People Count Over Time")
                chart_data = pd.DataFrame({
                    'Frame': range(0, len(people_counts) * process_every_n_frames, process_every_n_frames),
                    'People Count': people_counts
                })
                st.line_chart(chart_data.set_index('Frame'))
    
    elif source_type == "Webcam" and process_button:
        # Open webcam
        cap = cv2.VideoCapture(int(camera_id))
        
        if not cap.isOpened():
            st.error(f"Error opening webcam (ID: {camera_id})")
        else:
            # Create a placeholder for the video
            video_placeholder = st.empty()
            
            # Create stop button
            stop_webcam = st.button("Stop Webcam")
            
            while not stop_webcam and not stop_button:
                ret, frame = cap.read()
                
                if not ret:
                    st.error("Error reading from webcam")
                    break
                
                # Detect objects
                detections, detection_frame = detector.detect(frame)
                
                # Analyze detections
                analysis_results, analysis_frame = analyzer.analyze(detections, detection_frame)
                
                # Check for alerts
                alerts = alerter.check_and_alert(analysis_results)
                
                # Convert BGR to RGB for display
                display_frame = cv2.cvtColor(analysis_frame, cv2.COLOR_BGR2RGB)
                
                # Update video display
                video_placeholder.image(display_frame, caption="Live Feed", use_column_width=True)
                
                # Add a small delay
                time.sleep(0.1)
            
            # Clean up
            cap.release()
    
    elif source_type == "RTSP Stream" and process_button and rtsp_url.startswith("rtsp://"):
        # Open RTSP stream
        cap = cv2.VideoCapture(rtsp_url)
        
        if not cap.isOpened():
            st.error(f"Error opening RTSP stream: {rtsp_url}")
        else:
            # Create a placeholder for the video
            video_placeholder = st.empty()
            
            # Create stop button
            stop_stream = st.button("Stop Stream")
            
            while not stop_stream and not stop_button:
                ret, frame = cap.read()
                
                if not ret:
                    st.error("Error reading from RTSP stream")
                    break
                
                # Detect objects
                detections, detection_frame = detector.detect(frame)
                
                # Analyze detections
                analysis_results, analysis_frame = analyzer.analyze(detections, detection_frame)
                
                # Check for alerts
                alerts = alerter.check_and_alert(analysis_results)
                
                # Convert BGR to RGB for display
                display_frame = cv2.cvtColor(analysis_frame, cv2.COLOR_BGR2RGB)
                
                # Update video display
                video_placeholder.image(display_frame, caption="RTSP Stream", use_column_width=True)
                
                # Add a small delay
                time.sleep(0.1)
            
            # Clean up
            cap.release()

if __name__ == "__main__":
    run_streamlit_app()
