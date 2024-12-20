import os
import pandas as pd
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
import csv
from datetime import timedelta

def initialize_youtube(api_key):
    return build('youtube', 'v3', developerKey=api_key)

def fetch_video_ids(youtube, genre, max_results=500):
    video_ids = []
    request = youtube.search().list(
        part="id",
        type="video",
        q=genre,
        maxResults=50,
    )
    while request and len(video_ids) < max_results:
        response = request.execute()
        video_ids.extend([item['id']['videoId'] for item in response['items']])
        request = youtube.search().list_next(request, response)
    return video_ids[:max_results]

def fetch_video_details(youtube, video_ids):
    video_data = []
    for i in range(0, len(video_ids), 50):
        ids_chunk = ','.join(video_ids[i:i + 50])
        response = youtube.videos().list(
            part="snippet,contentDetails,statistics,recordingDetails",
            id=ids_chunk
        ).execute()
        for item in response['items']:
            video_data.append({
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "title": item['snippet']['title'],
                "description": item['snippet'].get('description', ''),
                "channel_title": item['snippet']['channelTitle'],
                "tags": item['snippet'].get('tags', []),
                "category": item['snippet'].get('categoryId', ''),
                "topic_details": item['snippet'].get('topicDetails', ''),
                "published_at": item['snippet']['publishedAt'],
                "duration": item['contentDetails']['duration'],
                "view_count": item['statistics'].get('viewCount', 0),
                "comment_count": item['statistics'].get('commentCount', 0),
                "captions_available": check_captions(item['id']),
                "location": item.get('recordingDetails', {}).get('locationDescription', ''),
            })
    return video_data

def check_captions(video_id):
    try:
        YouTubeTranscriptApi.get_transcript(video_id)
        return True
    except:
        return False

def fetch_captions(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([item['text'] for item in transcript])
    except:
        return None

def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def main():
    api_key = "AIzaSyDLSJnUse_1zFO_oIf5g2fLwht75El1B5M"
    genre = input("Enter genre: ")
    youtube = initialize_youtube(api_key)
    
    print("Fetching video IDs...")
    video_ids = fetch_video_ids(youtube, genre)
    
    print("Fetching video details...")
    video_data = fetch_video_details(youtube, video_ids)
    
    print("Saving data to CSV...")
    save_to_csv(video_data, f"{genre}_videos.csv")
    print("Process completed!")

if __name__ == "__main__":
    main()
