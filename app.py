from flask import Flask, jsonify
import requests
import csv
import io

app = Flask(__name__)

# Google Spreadsheet ID
SPREADSHEET_ID = "1byzNoMAdlWto3hUtHqnuh44SSNVmf_QocxqifNjAxgc"
SPREADSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"

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