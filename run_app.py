import os
import sys
import subprocess
import streamlit.web.cli as stcli

def main():
    """
    Main entry point for the Streamlit application.
    This script starts the Streamlit server and launches the app.
    """
    # Ensure we're in the right directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # Set the environment variable to prevent Streamlit from opening a browser
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Path to main app file that contains the Streamlit application
    app_path = os.path.join(current_dir, "0_Introduction.py")
    
    # Launch the browser manually
    browser_cmd = f'start "" "http://localhost:8501"'
    subprocess.Popen(browser_cmd, shell=True)
    
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", app_path, "--server.headless", "true", "--server.enableCORS", "false"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main() 