#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from pymongo import MongoClient
from nltk.corpus import wordnet as wn
import csv
import random

# Final object containing details of all results
videos = []
header = ['id', 'title', 'description', 'channelId', 'publishedAt', 'tags', 'viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount']

# Fetch mongo collection object
def collection(collection_name):
  db_client = MongoClient()
  db_object = db_client.aasma_development
  return db_object[str(collection_name)]

# Fetch random youtube api key so that not all keys get exhausted
def fetch_api_key():
  db_api_keys = collection('api_keys')
  num_api_keys = db_api_keys.find({'api': 'youtube'}).count()
  return db_api_keys.find({'api': 'youtube'})[random.randrange(num_api_keys)]['api_key']

# Write the result to csv file
def write_to_csv(csv_rows, header):
  with open('youtube_results.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    for row in csv_rows:
      # Encode the result in utf-8
      writer.writerow(map(lambda x: x.encode('utf-8') if type(x) is unicode else x, row))

# Get the semantically equivalent sets of the word or the synonyms from lemmas and build query string
def get_synset_term(words):
  temp_list = []
  for word in words.split(","):
    temp_list += [synset.lemma_names() for synset in wn.synsets(word)]
  return "|".join(set([x.replace("-", "_") for iter in temp_list for x in iter]))

# Build search term according to following format. | is equivalent to OR operator in youtube API
# (aa|na|(alcoholics|narcotics anonymous)) (addiction (12|Twelve|Step) recovery|speaker)
def get_search_term():
  alcoholics_terms = get_synset_term('alcoholic,booze')
  narcotic_terms = get_synset_term('narcotic,drug')
  anonymous_terms = get_synset_term('anonymous')
  addiction_terms = get_synset_term('addiction')
  recovery_terms = get_synset_term('recovery,treatment,rehab')
  speaker_terms = get_synset_term('speaker')
  return '(aa|na|({}|{} {})) ({} (12|twelve|12_step) {}|{}'.format(alcoholics_terms, narcotic_terms, anonymous_terms, addiction_terms, recovery_terms, speaker_terms)


def youtube_search(options, nextPageToken=None):
  DEVELOPER_KEY = fetch_api_key()
  YOUTUBE_API_SERVICE_NAME = "youtube"
  YOUTUBE_API_VERSION = "v3"

  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  # Returns about 500 unique results regardless of totalResults being much much more
  # After that results start duplicating
  # Check https://code.google.com/p/gdata-issues/issues/detail?id=4282 for the issue
  search_response = youtube.search().list(
    q=options.q,
    type="video",
    part="id",
    maxResults=options.max_results,
    safeSearch='none',
    pageToken=nextPageToken
  ).execute()

  search_videos = []

  nextPageToken = search_response.get("nextPageToken")

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


  # Add each result to the list, and then add details of matching videos.
  for video_result in video_response.get("items", []):
    videos.append([video_result.get("id"), video_result["snippet"].get("title"), video_result["snippet"].get("description"), video_result["snippet"]["channelId"], video_result["snippet"]["publishedAt"], video_result["snippet"].get("tags")] + [video_result["statistics"][statistic_key] for statistic_key in video_result["statistics"]])

  if nextPageToken != None:
    youtube_search(options, nextPageToken)

if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default=get_search_term())
  argparser.add_argument("--max-results", help="Max results", default=50)
  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  finally:
    write_to_csv(videos, header)