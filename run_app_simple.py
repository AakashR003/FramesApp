import os
import sys
import subprocess
import time

def run_streamlit():
    """
    Main entry point for the Streamlit application.
    This script starts the Streamlit server and launches the app.
    """
    # Ensure we're in the right directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # Path to main app file that contains the Streamlit application
    app_path = os.path.join(current_dir, "0_Introduction.py")
    
    # Start Streamlit server as a subprocess
    server_cmd = f"streamlit run {app_path} --server.headless true --server.enableCORS false"
    server_process = subprocess.Popen(server_cmd, shell=True)
    
    # Wait for Streamlit server to start
    print("Starting Streamlit server...")
    time.sleep(3)
    
    # Launch the browser
    browser_cmd = 'start "" "http://localhost:8501"'
    subprocess.Popen(browser_cmd, shell=True)
    
    # Wait for user exit
    try:
        print("Structural Analysis App is running. Close this window to exit.")
        server_process.wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        server_process.terminate()

if __name__ == "__main__":
    run_streamlit() 