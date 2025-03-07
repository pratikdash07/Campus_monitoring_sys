import os
import argparse
from main import process_image, process_video
from src.utils.config_loader import load_config
from src.detection.detector import ObjectDetector
from src.analysis.analyzer import RegionAnalyzer
from src.alert.alerter import AlertManager
from src.database.db_manager import DatabaseManager

def main():
    parser = argparse.ArgumentParser(description="Process local files")
    parser.add_argument('--type', choices=['images', 'videos', 'all'], default='all',
                        help='Type of files to process')
    args = parser.parse_args()
    
    # Load configuration and initialize components
    config = load_config()
    detector = ObjectDetector(config)
    analyzer = RegionAnalyzer(config)
    alerter = AlertManager(config)
    db_manager = DatabaseManager(config)
    
    # Process images
    if args.type in ['images', 'all']:
        images_dir = 'data/images'
        if os.path.exists(images_dir) and os.path.isdir(images_dir):
            image_files = [f for f in os.listdir(images_dir) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            if image_files:
                print(f"Found {len(image_files)} images to process")
                for img_file in image_files:
                    img_path = os.path.join(images_dir, img_file)
                    print(f"Processing image: {img_path}")
                    process_image(img_path, detector, analyzer, alerter, db_manager)
            else:
                print(f"No images found in {images_dir}")
    
    # Process videos
    if args.type in ['videos', 'all']:
        videos_dir = 'data/videos'
        if os.path.exists(videos_dir) and os.path.isdir(videos_dir):
            video_files = [f for f in os.listdir(videos_dir) 
                          if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))]
            
            if video_files:
                print(f"Found {len(video_files)} videos to process")
                for vid_file in video_files:
                    vid_path = os.path.join(videos_dir, vid_file)
                    print(f"Processing video: {vid_path}")
                    process_video(vid_path, detector, analyzer, alerter, db_manager)
            else:
                print(f"No videos found in {videos_dir}")

if __name__ == "__main__":
    main()
