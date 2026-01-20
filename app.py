from flask import Flask, jsonify, request
import requests
import csv
import io
import time
from util.redis_util import RedisClient

app = Flask(__name__)

# Google Spreadsheet ID
SPREADSHEET_ID = "1byzNoMAdlWto3hUtHqnuh44SSNVmf_QocxqifNjAxgc"
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"

# Initialize Redis client
redis_client = RedisClient()

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/songs/all', methods=['GET'])
def get_all_songs():
    """
    API endpoint to fetch all songs from the public Google Spreadsheet.
    Returns JSON response with list of songs.
    """
    try:
        # Fetch the CSV data from Google Sheets
        response = requests.get(SPREADSHEET_URL, timeout=10)
        response.raise_for_status()
        
        # Parse CSV data
        csv_content = response.content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Convert to list of dictionaries
        songs = []
        for row in csv_reader:
            # Filter out empty rows (where song_title is empty)
            if row.get('song_title', '').strip():
                song = {
                    'main_theme_title': row.get('main_theme_title', '').strip(),
                    'theme_title': row.get('theme_title', '').strip(),
                    'theme_image': row.get('theme_image', '').strip(),
                    'theme_share': row.get('theme_share', '').strip(),
                    'song_title': row.get('song_title', '').strip(),
                    'song_artist': row.get('song_artist', '').strip(),
                    'song_url': row.get('song_url', '').strip(),
                    'song_art': row.get('song_art', '').strip()
                }
                songs.append(song)
        
        return jsonify({
            'success': True,
            'count': len(songs),
            'songs': songs
        }), 200
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'success': False,
            'error': f'Failed to fetch data from Google Sheets: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/add-to-favorites', methods=['POST'])
def add_to_favorites():
    """
    API endpoint to add a song to user's favorites.
    Accepts user_id and song_id, stores in Redis with timestamp.
    Supports multiple favorite songs per user.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON'
            }), 400
        
        user_id = data.get('user_id')
        song_id = data.get('song_id')
        
        # Validate required fields
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        if not song_id:
            return jsonify({
                'success': False,
                'error': 'song_id is required'
            }), 400
        
        # Get current timestamp
        timestamp = time.time()
        
        # Redis key structure: favorites:{user_id}
        # Using hash to store multiple songs per user
        # Each song_id is a field, timestamp is the value
        redis_key = f"favorites:{user_id}"
        
        # Check if song is already in favorites
        existing_timestamp = redis_client.hget(redis_key, song_id)
        is_new_favorite = existing_timestamp is None
        
        # Store song_id with timestamp in hash
        # This allows multiple songs per user (each song_id is a separate field)
        redis_client.hset(redis_key, song_id, timestamp)
        
        # Get total count of favorites for this user
        total_favorites = redis_client.hlen(redis_key)
        
        message = 'Song added to favorites' if is_new_favorite else 'Song favorite updated'
        
        return jsonify({
            'success': True,
            'message': message,
            'user_id': user_id,
            'song_id': song_id,
            'timestamp': timestamp,
            'is_new_favorite': is_new_favorite,
            'total_favorites': total_favorites
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/remove-from-favorites', methods=['POST'])
def remove_from_favorites():
    """
    API endpoint to remove a song from user's favorites.
    Accepts user_id and song_id, removes from Redis.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON'
            }), 400
        
        user_id = data.get('user_id')
        song_id = data.get('song_id')
        
        # Validate required fields
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        if not song_id:
            return jsonify({
                'success': False,
                'error': 'song_id is required'
            }), 400
        
        # Redis key structure: favorites:{user_id}
        redis_key = f"favorites:{user_id}"
        
        # Check if song exists in favorites
        existing_timestamp = redis_client.hget(redis_key, song_id)
        
        if existing_timestamp is None:
            return jsonify({
                'success': False,
                'error': 'Song is not in favorites',
                'user_id': user_id,
                'song_id': song_id
            }), 404
        
        # Remove song_id from hash
        deleted_count = redis_client.hdel(redis_key, song_id)
        
        # Get total count of favorites for this user after removal
        total_favorites = redis_client.hlen(redis_key)
        
        return jsonify({
            'success': True,
            'message': 'Song removed from favorites',
            'user_id': user_id,
            'song_id': song_id,
            'total_favorites': total_favorites
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500