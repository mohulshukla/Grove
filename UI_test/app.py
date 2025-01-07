from flask import Flask, render_template, jsonify, request, send_from_directory
import sys
import os
import random


# Add the path to the `mohul_local` directory to access retrieve.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from retrieve import retrieve_five_similar, retrieve_random, get_all_IDs

app = Flask(__name__)

# Define paths and initial video
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_FOLDER = os.path.join(BASE_DIR, '..', 'videos')

# Get all video IDs and select a random one for the initial video
all_video_ids = get_all_IDs()
initial_video_id = random.choice(all_video_ids)
from retrieve import retrieve_five_similar, retrieve_random

app = Flask(__name__)

# Define paths and initial video
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEOS_FOLDER = os.path.join(BASE_DIR, '..', 'videos')
# initial_video_id = "asiandance.mp4"
initial_video_id = random.choice(all_video_ids)
seen_videos = [initial_video_id]

@app.route('/')
def index():
    return render_template('index.html', initial_video=initial_video_id)

@app.route('/video/<filename>')
def video(filename):
    return send_from_directory(VIDEOS_FOLDER, filename)

@app.route('/get_similar_videos', methods=['POST'])
def get_similar_videos():
    video_id = request.json.get("video_id")
    similar_videos = retrieve_five_similar(video_id, seen_videos)
    seen_videos.extend(similar_videos)  # Add new similar videos to seen list
    return jsonify(similar_videos)

@app.route('/get_random_videos', methods=['POST'])
def get_random_videos():
    video_id = request.json.get("video_id")
    random_videos = retrieve_random(video_id)
    return jsonify(random_videos)

if __name__ == "__main__":
    app.run(debug=True)