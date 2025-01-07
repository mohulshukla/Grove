import yt_dlp
import os
import json
import re

import ffmpeg

class TikTokScaper:
    def __init__(self, output_dir):
        self.output_dir = output_dir 
        os.makedirs(self.output_dir, exist_ok=True)

    def download_videos(self, video_url_list, meta_data_path):
        output_filename = "%(title)s.mp4" 
        ydl_opts = {
            'format': 'mp4',  # Prioritize MP4 format
            'outtmpl': os.path.join(self.output_dir, output_filename),  # Define the output path with .mp4 extension
            'quiet': False,
            'no_warnings': True,
        }
        metadata_videos = []
        for video_url in video_url_list:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    print(f"Downloading TikTok video from {video_url}")
                    metadata = ydl.extract_info(video_url, download=True)
                    print("Video saved at:", os.path.join(self.output_dir, f"{metadata['title']}.mp4"))
                    metadata.update({"video_file": os.path.join(self.output_dir, f"{metadata['title']}.mp4")})
                    metadata_videos.append(metadata)

            except Exception as e:
                print("Error downloading video:", str(e))

        json_file_path = os.path.join(self.output_dir, meta_data_path)

        with open(json_file_path, "w") as json_file:
            json.dump(video_urls, json_file, indent=4)
        return json_file_path
            
    def download_profile(self, profile_url, username, num_videos=None):
            profile_output_dir = os.path.join(self.output_dir, username)
            os.makedirs(profile_output_dir, exist_ok=True)
            ydl_opts = {
                'quiet': False,
                'outtmpl': os.path.join(profile_output_dir, 'videobella_%(autonumber)03d.mp4'),  # Outputs as video_001.mp4, video_002.mp4, etc.
                'no_warnings': True,
                'playlistend': num_videos,
            }
            
            metadata_videos = []
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"Checking videos from profile {profile_url}")
                profile_metadata = ydl.extract_info(profile_url, download=False)
                index = 0
                for metadata in profile_metadata.get("entries", []):
                    if "ext" in metadata["formats"][0]:

                        video_path_name = f"{username}{index}.mp4"
                        ydl_opts = {
                            'outtmpl': os.path.join(profile_output_dir, video_path_name),
                            'quiet': False,
                            'no_warnings': True
                        }

                        video_info = ydl.extract_info(metadata['url'], download=True)
                        video_path = os.path.join(profile_output_dir, video_path_name)
                        video_info.update({"video_file": video_path})
                        metadata_videos.append(video_info)

            json_file_path = os.path.join(self.output_dir, f"{username}.json")

            with open(json_file_path, "w") as json_file:
                json.dump(metadata_videos, json_file, indent=4)
            return metadata_videos


    def delete_audio_only_mp4_files(self, folder_path):
        # Check if the folder exists
        if not os.path.isdir(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
            return

        # Iterate over each file in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if it's an .mp4 file
            if os.path.isfile(file_path) and filename.lower().endswith(".mp4"):
                try:
                    # Get the stream information
                    probe = ffmpeg.probe(file_path)
                    
                    # Check if there's only an audio stream and no video stream
                    has_video = any(stream['codec_type'] == 'video' for stream in probe['streams'])
                    has_audio = any(stream['codec_type'] == 'audio' for stream in probe['streams'])
                    
                    if has_audio and not has_video:
                        os.remove(file_path)
                        print(f"Deleted audio-only MP4 file: {file_path}")
                    else:
                        print(f"Skipped: {file_path} (contains video)")
                
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")
    def extract_different(self, lines_list):
        cut_prefix = ""
        cut_suffix = ""
        
        # find different prefix
        for i in range(1, len(lines_list)):
            line_list_cut = []
            for line in lines_list:
                line_list_cut.append(line[:i])
            if len(set(line_list_cut)) != 1:
                cut_prefix = line[:i-1]
                break

        # find different suffix
        for i in range(1, len(lines_list)):
            line_list_cut = []
            for line in lines_list:
                line_list_cut.append(line[len(line)-i:])
            if len(set(line_list_cut)) != 1:
                cut_suffix = line[len(line)-i+1:]
                break
        #print("cutting prefix:", cut_prefix)
        #print("cutting suffix:", cut_suffix)

        trimmed_lines = []
        for line in lines_list:
            trimmed_lines.append(line[len(cut_prefix):len(line) - len(cut_suffix)])
        
        return trimmed_lines



if __name__ == "__main__":
    folder_path = "downloads"
    scraper_obj = TikTokScaper(folder_path)

    profile_url_list = [
        "https://www.tiktok.com/@bellapoarch?lang=en"
    ]
    usernames_list = scraper_obj.extract_different(profile_url_list)

    for profile_url, username in zip(profile_url_list, usernames_list):

        video_urls = scraper_obj.download_profile(profile_url, username, 15)
        scraper_obj.delete_audio_only_mp4_files(os.path.join(folder_path, username))



    #scraper_obj.download_videos(username, video_urls)
