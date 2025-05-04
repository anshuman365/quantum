import asyncio
from telethon.sync import TelegramClient
from telethon.tl.types import UserStatusOnline, UserStatusOffline
from datetime import datetime, timedelta
import json
import os

api_id = 26128347       
api_hash = 'a0abc4a9e96d0d1ecd3e87890858a41d'   
usernames = ['@Archu_35', '@raj12344323'] 

client = TelegramClient('session_name', api_id, api_hash)
log_file = 'status_log.json'

# Initialize JSON structure
if os.path.exists(log_file):
    with open(log_file, 'r') as f:
        status_data = json.load(f)
else:
    status_data = {
        user: {
            'current_status': 'unknown',
            'history': [],
            'last_seen': None
        } for user in usernames
    }

def utc_to_ist(utc_dt):
    if utc_dt is None:
        return None
    return (utc_dt + timedelta(hours=5, minutes=30)).isoformat()

async def track_user(username):
    user = await client.get_entity(username)
    prev_status = None

    while True:
        try:
            user_info = await client.get_entity(user.id)
            status = user_info.status
            now = datetime.now().isoformat()
            
            status_change = {}
            
            if isinstance(status, UserStatusOnline):
                status_change = {
                    'timestamp': now,
                    'status': 'online',
                    'last_seen': None
                }
            elif isinstance(status, UserStatusOffline):
                last_seen = utc_to_ist(status.was_online)
                status_change = {
                    'timestamp': now,
                    'status': 'offline',
                    'last_seen': last_seen
                }
            
            if status_change:
                status_data[username]['history'].append(status_change)
                status_data[username]['history'] = status_data[username]['history'][-100:]
                status_data[username]['current_status'] = status_change['status']
                status_data[username]['last_seen'] = status_change['last_seen']
                
                with open(log_file, 'w') as f:
                    json.dump(status_data, f, indent=2)

            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Error tracking {username}: {str(e)}")
            await asyncio.sleep(10)

async def start_all():
    """Start tracking for all users"""
    try:
        if not client.is_connected():
            await client.start()
            
        tasks = [track_user(username) for username in usernames]
        await asyncio.gather(*tasks)
        
    except Exception as e:
        print(f"Tracking error: {str(e)}")
        await client.disconnect()

# Add this at the end of track.py to ensure clean shutdown
async def shutdown():
    await client.disconnect()

def stop_tracking():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(shutdown())