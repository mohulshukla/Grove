import os
from pinecone import Pinecone
from similar import find_similar_vectors, get_all_IDs
import random

# API Key definition
key = '4641190a-7251-4ae2-8ecd-b17623ecd3ae'
index_name = "vid-embeddings"
dimension = 768  # for video embeddings

# Set the absolute path for video_ids.txt
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_IDS_FILE = os.path.join(BASE_DIR, 'video_ids.txt')

# Modify get_all_IDs to use the absolute path
def get_all_IDs():
    """
    Gets all video ids from the video_ids.txt file.
    If video_ids.txt does not exist, it creates the file by scanning the videos folder.
    """
    if not os.path.exists(VIDEO_IDS_FILE):
        print("video_ids.txt not found. Please ensure it exists in the correct directory.")
        return []
    
    # Read video IDs from the file using the absolute path
    with open(VIDEO_IDS_FILE, 'r') as f:
        video_ids = f.read().splitlines()
    return video_ids

# Global Variables
GENERATE_BATCH_COUNT = 5
VIDEO_IDS = get_all_IDs()
nature_video_id = "mountain1.mp4"
dance_video_id = "asiandance.mp4"
beast_video_id = "video_013.mp4"

pc = Pinecone(api_key=key)

def retrieve_five_similar(video_id, seen_videos):
    '''
    Input: takes in a string that is the video_id and a list of seen videos
    Output: a list of five video_ids that represent videos that are the most similar, excluding seen videos
    '''
    all_similar_videos = [similar_id for similar_id, _ in find_similar_vectors(video_id, top_k=GENERATE_BATCH_COUNT + len(seen_videos) + 1)]
    
    # Filter out seen videos and the input video_id itself
    new_similar_videos = [vid for vid in all_similar_videos if vid != video_id and vid not in seen_videos]

    # Return up to 5 new similar videos
    return new_similar_videos[:5]
    
print(retrieve_five_similar(beast_video_id, []))

def retrieve_random(video_id):
    '''
    Input: takes in a string that is the video_id
    Output: a list of two video_ids, each randomly selected from all video IDs except the input video_id
    '''
    # Filter out the current video_id from the list of all video IDs
    available_video_ids = [vid for vid in VIDEO_IDS if vid != video_id]

    # If there are fewer than two available video IDs, return as many as possible
    if len(available_video_ids) < 2:
        return available_video_ids

    # Randomly select two different videos from the available video IDs
    random_videos = random.sample(available_video_ids, 2)
    return random_videos

# Example usage
print(retrieve_random(dance_video_id))