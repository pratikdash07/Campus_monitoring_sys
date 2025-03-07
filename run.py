import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Campus Monitoring System Launcher")
    parser.add_argument('--mode', type=str, default='ui', choices=['ui', 'cli'],
                        help='Launch mode: ui (Streamlit interface) or cli (command line)')
    parser.add_argument('--source', type=str, default='0',
                        help='Source for CLI mode: 0 for webcam, path for file or directory')
    parser.add_argument('--image', action='store_true',
                        help='Process as image instead of video (CLI mode only)')
    parser.add_argument('--batch', action='store_true',
                        help='Process all files in directory (CLI mode only)')
    
    args = parser.parse_args()
    
    if args.mode == 'ui':
        # Launch Streamlit interface with file watcher disabled
        os.environ['STREAMLIT_SERVER_FILE_WATCHER_TYPE'] = 'none'
        os.system('streamlit run src/interface/app.py')
    else:
        # Launch command line interface
        cmd = f'python main.py --source "{args.source}"'
        if args.image:
            cmd += ' --image'
        if args.batch:
            cmd += ' --batch'
        os.system(cmd)

if __name__ == "__main__":
    main()
