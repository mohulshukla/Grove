import av
import numpy as np
import torch
from transformers import VivitImageProcessor, VivitModel
from huggingface_hub import hf_hub_download
import ffmpeg
import os
import math
np.random.seed(0)




class VideoEmbedding:
    def __init__(self):
        self.image_processor = VivitImageProcessor.from_pretrained("google/vivit-b-16x2", device_map = "auto")
        self.model = VivitModel.from_pretrained("google/vivit-b-16x2", device_map = "auto")
        self.model.eval()

    def get_videos_info(self, video_list): # video_list = list
        '''
        Input: 
            list of video paths ["videopath1", "videopath2", "videopath3"]

        Output: 
            list of dictionaries 
                each dict contains 
                {
                    'video_path': video_path,
                    'frame_count': frame_count,
                    'fps': fps,
                    'length': length
                } 
                for each video
        '''
        video_info_list = []
        
        for video_path in video_list:
            container = av.open(video_path)
            video_stream = container.streams.video[0]
            frame_count = video_stream.frames
            fps = float(video_stream.average_rate)
            length = frame_count / fps
            video_info_list.append({
                'video_path': video_path,
                'frame_count': frame_count,
                'fps': fps,
                'length': length
            })
        return video_info_list


    def get_videos_in_folder(self, folder_path):
        '''
        returns file path of all mp4 files
        '''
        return [f"{folder_path}/{f}" for f in os.listdir(folder_path) if f.endswith(('.mp4'))]


    def add_sample_rate(self, video_infos, sample_percentage): 

        '''
        Input: list of dictaries containing 
            video_infos[i][fps]: int
                frames per second
            sample_percentage: float
                float from 0 to 1
                signifies percentage of frames to sample persecond
                ex: 0.5 would sample have the frames in every second
        Output: 
            the number of frames to sample per second, rounded up
        '''
        for video in video_infos:
            sample_rate = math.ceil(video["fps"] * sample_percentage)
            video.update({"sample_rate": sample_rate})
        return video_infos



    def read_video_pyav(self, container_path, indices):
        frames = []
        start_index = indices[0]
        end_index = indices[-1]

        # Open the container with the appropriate hardware acceleration
        container = av.open(container_path, options={'hwaccel': 'cuda', 'hwaccel_device': '0'})

        stream = container.streams.video[0]
        stream.thread_type = 'AUTO'

        for i, frame in enumerate(container.decode(stream)):
            if i > end_index:
                break
            if i >= start_index and i in indices:
                # Convert the frame to RGB numpy array
                frames.append(frame.to_ndarray(format='rgb24'))

        return np.stack(frames)

    def sample_frame_indices(self, total_frames, frame_sample_rate):
        '''
        total_frames : int
        frame_sample_rate: float (between 0 and 1)

        Samples range(0, total_frames) evenly based on frame_sample_rate (signifies percentage of total_frames to sample)
        returns the samples in batches of 32 trucrating the remainder
        '''
        def split_frames(frames, chunk_size):
            #splits list of values into chunks of 32, truacates remainder
            return [frames[i: i + chunk_size] for i in range(0, len(frames), chunk_size) if len(frames[i: i + chunk_size]) == chunk_size]
        base_chunk_size = 32
        indexes = list(range(0, total_frames, frame_sample_rate))
        split_index = split_frames(indexes, base_chunk_size)
        return split_index

    def get_embeddings(self, input_batch):

        embeddings_batch_results = []
        for i in range(0, len(input_batch)): # if u iterate though the list (for batch in input_batch) it has a wierd error
            inputs = vid_emb.image_processor(input_batch[i], return_tensors="pt")
            # forward pass
            with torch.no_grad():  
                outputs = self.model(**inputs)
                last_hidden_states = outputs.last_hidden_state
            print(list(last_hidden_states.shape))
            embeddings_batch_results.append(last_hidden_states.cpu()) # stores in RAM

        unbatched_embeddings = []
        for batch in embeddings_batch_results:
            for embedding in batch:
                unbatched_embeddings.append(embedding)

        return unbatched_embeddings


    def average_embeddings(self, unbatched, sample_size):
        video_embedding_average_list = []

        for segment in unbatched:
            last_sample_size = segment[len(segment)-sample_size:]
            last_sample_size_average = torch.mean(last_sample_size, dim=0)
            video_embedding_average_list.append(last_sample_size_average)

        video_embedding_average = torch.mean(torch.stack(video_embedding_average_list), dim=0)
        return video_embedding_average

    def split_batch(self, frames, chunk_size):
        #splits list of values into chunks of 32, does NOT truncate remainder
        return [frames[i: i + chunk_size] for i in range(0, len(frames), chunk_size)]




vid_emb = VideoEmbedding()

video_folder = "videos"
video_paths = vid_emb.get_videos_in_folder("videos")
video_info_all =  vid_emb.get_videos_info(video_paths)
video_info_all = vid_emb.add_sample_rate(video_info_all, 0.3) # sample 30% of frames


embeddings = {} #file_path : embedding

for video in video_info_all:
    try:
        file_path = video["video_path"]
        print("Processing", video["video_path"])
        max_concurrent = 4 # 2 segments can be process concurrently on 2x3090
        sample_size = 5 #number pf embeddings to sample from result of processign batch of 32 frames

        total_indices = vid_emb.sample_frame_indices(video["frame_count"], video["sample_rate"])
        frame_segments = [list(vid_emb.read_video_pyav(file_path, indices=indices)) for indices in total_indices]
        input_batch = vid_emb.split_batch(frame_segments, max_concurrent) 
        raw_embedding = vid_emb.get_embeddings(input_batch)
        video_embedding_average = vid_emb.average_embeddings(raw_embedding, sample_size)
        embeddings.update({file_path:video_embedding_average})
    except:
        print("holy freaking fuck you silly goose")

for key in embeddings:
    print("filename", key)
    print("Embeddings shape", embeddings[key].shape)

    






'''


video_paths = get_videos_in_folder("videos")
video_infos =  get_videos_info(video_paths)
video_infos = add_sample_rate(video_infos, 0.3) #adjusted sample rate based on framerate



'''