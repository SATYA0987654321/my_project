import uvicorn
import webbrowser
import threading
import time
import os

def open_browser():
    # Wait a moment for the Uvicorn server to spin up
    time.sleep(1.5)
    print("\nOpening Resume Skill Gap Analyzer in your browser...")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Start a background thread to open the browser
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the FastAPI server
    print("Starting Resume Skill Gap Analyzer Web Application...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)