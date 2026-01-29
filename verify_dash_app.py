import subprocess
import time
import os
import signal
import sys
from playwright.sync_api import sync_playwright

def run_verification():
    # 1. Start Dash App
    print("Starting Dash App...")
    # Set PYTHONPATH so basic_library can be imported
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    # Run the app in a subprocess
    process = subprocess.Popen(
        [sys.executable, "rate_curve_dash/app.py"],
        env=env,
        text=True
    )
    
    # Wait for the app to start
    print("Waiting for app to start on http://127.0.0.1:8050 ...")
    time.sleep(5) # Give it some time to initialize
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to the app
            print("Navigating to http://127.0.0.1:8050 ...")
            page.goto("http://127.0.0.1:8050")
            page.wait_for_load_state("networkidle")
            
            # Take initial screenshot
            page.screenshot(path="verify_initial.png")
            print("Initial screenshot saved to verify_initial.png")
            
            # Select Curve ID
            print("Selecting Curve ID...")
            time.sleep(1)
            
            # Click Load Button
            print("Clicking Data Load...")
            page.click("#load-button")
            
            # Wait for loading to finish and chart to appear
            print("Waiting for chart...")
            time.sleep(5) # Wait for callback and rendering
            page.wait_for_selector("#curve-chart .js-plotly-plot", timeout=30000)
            
            # Additional wait to ensure Plotly has finished drawing
            time.sleep(2)
            
            # Take screenshot after data load
            page.screenshot(path="verify_loaded.png")
            print("Loaded screenshot saved to verify_loaded.png")
            
            # Interact with slider
            print("Interacting with slider...")
            slider_track = page.query_selector(".rc-slider-rail")
            if slider_track:
                box = slider_track.bounding_box()
                # Click 25% through the slider
                page.mouse.click(box['x'] + box['width'] * 0.25, box['y'] + box['height'] / 2)
                time.sleep(1)
                page.screenshot(path="verify_slider_move.png")
                print("Slider move screenshot saved to verify_slider_move.png")
            
            # Click Play
            print("Clicking Play...")
            page.click("#play-button")
            time.sleep(3) # Let it play for a bit
            page.screenshot(path="verify_playback.png")
            print("Playback screenshot saved to verify_playback.png")
            
            browser.close()
            print("Verification complete.")
            
    except Exception as e:
        print(f"Error during verification: {e}")
    finally:
        # Kill the Dash app process
        print("Stopping Dash App...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    run_verification()
