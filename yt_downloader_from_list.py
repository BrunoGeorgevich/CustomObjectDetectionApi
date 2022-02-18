import subprocess
import argparse
import os

# Usage:
# python3 yt_downloader_from_list.py --source data_links.txt
#
# The list must be in the following format (respecting the spaces):
# KWS0dPAZkm4;[1:38,1:46];[2:32,3:10];[5:06,5:08] 
# wUQB_TTnFys;[3:24,4:23];[4:50,5:01] 

def download_from_list(youtube_list):
    '''Download every subvideo from a list of YouTube videos and timestamps

    This program uses youtube-dl and ffmpeg. So make sure to install these programs before.
    It downloads the best quality available, up to 1080p, and stores the subvideos in a 
    subfolder 'youtube_videos'.

    Parameters
    ----------
    youtube_list: str
        The path for the txt file with your YouTube links and timestamps
    '''

    with open(youtube_list) as f:
        lines = f.read().splitlines()

    # Drop lines with comments
    for line in lines:
        if line.startswith('#'):
            lines.remove(line)
    
    for line in lines:
        line_list = line.split(';')
        
        yt_url = line_list[0].strip()
        timestamps = line_list[1:]

        # Download full video locally to make the extractions faster
        ret = subprocess.run(["youtube-dl", "-w",  "-f", "(mp4)bestvideo[height<=?1080]", yt_url, "-o", "vid.mp4"])

        # Create the subfolder to store the videos if it doesn't exist
        os.makedirs("youtube_videos", exist_ok=True)

        # Crop a subvideo for every timestamp in the list
        for i, ts in enumerate(timestamps):

            n_subvid = i

            ts = ts.strip()[1:-1]  # Remove spaces and brackets
            start_time, end_time = ts.split(',') 

            desired_file_path = os.path.join('youtube_videos', f'vid_{yt_url}_{n_subvid}.mp4')

            if os.path.exists(os.path.join('youtube_videos', f'vid_{yt_url}_{n_subvid}.mp4')):
                continue

            # Uses FFMPEG to crop the video
            subprocess.run(['ffmpeg', '-i', 'vid.mp4', '-ss', start_time, '-to', end_time, '-c:v', 'copy', '-c:a', 'copy', desired_file_path])

        # Delete the temporary video
        if os.path.exists("vid.mp4"):
            os.remove("vid.mp4")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=str, required=True, help="Filepath for list of videos to download."
    )
    args = parser.parse_args()
    #print(args.source)

    download_from_list(args.source)