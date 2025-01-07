import av
import os
import random
from video_embedding import VideoEmbedding
import numpy as np
from generate import *
from pinecone import Pinecone, ServerlessSpec
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define API key and index parameters
key = "" # insert your Pinecone key here
index_name = "vid-embeddings"
dimension = 768  # Adjust this dimension according to your embedding size if it's different

# Create an instance of the Pinecone class
pc = Pinecone(api_key=key)

if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)

pc.create_index(
    name=index_name,
    dimension=dimension,
    metric="cosine",  # Using cosine similarity for similarity search
    spec=ServerlessSpec(
        cloud="aws",  # Cloud provider
        region="us-east-1"  # Specify the region
    )
)

# Connect to the new index
index = pc.Index(index_name)

# Instantiate the VideoEmbedding class
vid_emb = VideoEmbedding()

# Define the folder containing the videos
video_folder = "videos"
video_paths = vid_emb.get_videos_in_folder(video_folder)
video_info_all = vid_emb.get_videos_info(video_paths)
video_info_all = vid_emb.add_sample_rate(video_info_all, 0.3)  # Sample 30% of frames

# Dictionary to hold file paths and corresponding embeddings
embeddings = {}

# Process each video and get embeddings
for video in video_info_all:
    file_path = video["video_path"]
    max_concurrent = 2  # Number of segments to process concurrently
    sample_size = 5  # Number of embeddings to sample from a batch of 32 frames

    # Sample frame indices
    total_indices = vid_emb.sample_frame_indices(video["frame_count"], video["sample_rate"])
    frame_segments = [list(vid_emb.read_video_pyav(file_path, indices=indices)) for indices in total_indices]
    input_batch = vid_emb.split_batch(frame_segments, max_concurrent)

    # Get raw embeddings and calculate average embedding
    raw_embedding = vid_emb.get_embeddings(input_batch)
    video_embedding_average = vid_emb.average_embeddings(raw_embedding, sample_size)

    # Store the averaged embedding in the dictionary
    embeddings[file_path] = video_embedding_average
    
    # Add the video ID to the Pinecone index and track the video ID in a file
    video_id = os.path.basename(file_path)  # Use the filename as the ID
    embedding_list = video_embedding_average.cpu().numpy().tolist()  # Convert PyTorch tensor to a list

    # Upsert the embedding to Pinecone
    index.upsert([{"id": video_id, "values": embedding_list}])

    # Append the video_id to the file for tracking
    with open("video_ids.txt", "a") as f:
        f.write(video_id + "\n")


# Query the index to verify embeddings were successfully stored
for key in embeddings:
    print("filename:", key)
    result = index.query(vector=embeddings[key].cpu().numpy().tolist(), top_k=5, include_metadata=True)
    print(f"Top similar vectors for {key}:")
    print(result)

# Function to retrieve all video IDs from the file
def retrieve_all_video_ids_from_file():
    # Check if the file exists before trying to read
    if not os.path.exists("video_ids.txt"):
        return []  # Return an empty list if the file does not exist
    with open("video_ids.txt", "r") as f:
        video_ids = f.read().splitlines()
    return video_ids

# Example usage of retrieve_all_video_ids_from_file
all_video_ids = retrieve_all_video_ids_from_file()
print("All video IDs:", all_video_ids)




'''# Create an instance of the Pinecone class
pc = Pinecone(api_key=key)

if index_name in pc.list_indexes().names():
    pc.delete_index(index_name)

pc.create_index(
    name=index_name,
    dimension=dimension,
    metric="cosine",  # Using cosine similarity for similarity search
    spec=ServerlessSpec(
        cloud="aws",  # Cloud provider
        region="us-east-1"  # Specify the region
    )
)

# Connect to the new index
index = pc.Index(index_name)

# Example 3-dimensional vectors (using floats)
data = generate_random_vectors(3, dimension)


upsert_large_dataset(index, data)


test_vector = [5.0, 6.0, 7.0]

# Upsert the test vector with the correct format
index.upsert([("test_vid", test_vector)])


# Query similar vectors
results = index.query(vector=test_vector, top_k=5)

print(results)'''
