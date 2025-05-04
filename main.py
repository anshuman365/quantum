from flask import Flask, render_template, jsonify
from threading import Thread
import time
import requests
import json
import track
import asyncio
import sys

app = Flask(__name__)

def self_pinger():
    while True:
        try:
            time.sleep(300)
            requests.get("http://localhost:10000/ping")
        except:
            pass

async def initialize_telegram():
    print("\n=== Telegram Authentication Required ===")
    await track.client.start()
    print("=== Login Successful! Starting Server ===")

def start_tracking():
    """Start tracking in a dedicated event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(track.start_all())
    except Exception as e:
        print(f"Tracking failed: {str(e)}")
    finally:
        loop.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return 'pong', 200

@app.route('/status')
def status():
    try:
        with open('status_log.json', 'r') as f:
            data = json.load(f)
            data['users'] = list(data.keys())
        return jsonify(data)
    except:
        return jsonify({'error': 'No data available'})

# Replace the existing __main__ block and thread management with:

if __name__ == "__main__":
    # Create a single dedicated event loop for Telegram operations
    telegram_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(telegram_loop)
    
    try:
        # Run authentication in the dedicated loop
        telegram_loop.run_until_complete(initialize_telegram())
        
        # Start tracking in the SAME loop
        Thread(target=telegram_loop.run_forever, daemon=True).start()
        telegram_loop.call_soon_threadsafe(
            telegram_loop.create_task, 
            track.start_all()
        )
        
        # Start web server
        Thread(target=self_pinger).start()
        app.run(host="0.0.0.0", port=10000)
        
    except KeyboardInterrupt:
        print("\nServer shutdown requested...")
        telegram_loop.stop()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)