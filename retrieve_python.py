#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from pymongo import MongoClient
from nltk.corpus import wordnet as wn
import csv
import random

db_client = MongoClient()
db_object = db_client.aasma_development

DEVELOPER_KEY = fetch_api_key()
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Final object containing details of all results
videos = []
header = ['id', 'title', 'description', 'channelId', 'publishedAt', 'tags', 'viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount']

def collection(collection_name):
  return db_object[str(collection_name)]

def fetch_api_key():
  db_api_keys = collection('api_keys')
  num_api_keys = db_api_keys.find({'api': 'google'}).count()
  return db_api_keys.find({'api': 'google'})[random.randrange(num_api_keys)]

def write_to_csv(csv_rows, header):
  with open('youtube_results.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    for row in csv_rows:
      writer.writerow(map(lambda x: x.encode('utf-8') if type(x) is unicode else x, row))

def youtube_search(options, nextPageToken=None):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    type="video",
    part="id",
    maxResults=options.max_results,
    safeSearch='none',
    pageToken=nextPageToken
  ).execute()

  search_videos = []

  nextPageToken = search_response["nextPageToken"]

  # Merge video ids
  for search_result in search_response.get("items", []):
    search_videos.append(search_result["id"]["videoId"])
  video_ids = ",".join(search_videos)

  # Call the videos.list method to retrieve location details for each video.
  video_response = youtube.videos().list(
    id=video_ids,
    part='snippet,statistics',
    maxResults=options.max_results
  ).execute()


  # Add each result to the list, and then display the list of matching videos.
  for video_result in video_response.get("items", []):
    videos.append([video_result.get("id"), video_result["snippet"].get("title"), video_result["snippet"].get("description"), video_result["snippet"]["channelId"], video_result["snippet"]["publishedAt"], video_result["snippet"].get("tags")] + [video_result["statistics"][statistic_key] for statistic_key in video_result["statistics"]])

  if nextPageToken != None:
    youtube_search(options, nextPageToken)

if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="AA Speaker")
  argparser.add_argument("--max-results", help="Max results", default=50)
  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  finally:
    write_to_csv(videos, header)