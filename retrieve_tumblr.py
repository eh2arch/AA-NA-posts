from apiclient.errors import HttpError
from oauth2client.tools import argparser
from pymongo import MongoClient
import pytumblr
import csv
import random

posts_array = []
header = ["post_url", "date", "tags", "type", "misc", "misc"]
# Fetch mongo collection object
def collection(collection_name):
  db_client = MongoClient()
  db_object = db_client.aasma_development
  return db_object[str(collection_name)]

# Fetch random tumblr api key so that not all keys get exhausted
def fetch_api_key():
  db_api_keys = collection('api_keys')
  num_api_keys = db_api_keys.find({'api': 'tumblr'}).count()
  return db_api_keys.find({'api': 'tumblr'})[random.randrange(num_api_keys)]['api_key']

# Write the result to csv file
def write_to_csv(csv_rows, header):
  with open('tumblr_results.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile, delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL)
    writer.writerow(header)
    for row in csv_rows:
      # Encode the result in utf-8
      writer.writerow(map(lambda x: x.encode('utf-8') if type(x) is unicode else x, row))

def get_search_term():
  return ['aa speaker', 'na speaker', 'alcoholics anonymous', 'narcotics anonymous', '12 step recovery', 'drug addiction recovery']

def tumblr_search(options, search_phrase="aa speaker", paginate_older_attribute=None):
  DEVELOPER_KEY = fetch_api_key()
  client = pytumblr.TumblrRestClient(fetch_api_key())

  if paginate_older_attribute != None:
    paginate_older_attribute = int(paginate_older_attribute)

  # Call the tagged method to retrieve results matching the specified
  # tag.
  posts = client.tagged(search_phrase, before=paginate_older_attribute, limit=options.max_results)

  if len(posts) > 0:
    before = posts[-1]["timestamp"]

    # Iterate over results and add each result to list
    for post in posts:
      post_keys = ["post_url", "date", "tags", "type"]
      if post["type"] == "text":
        post_keys += ["title", "body"]
      elif post["type"] == "photo":
        post_keys += ["photos", "caption"]
      elif post["type"] == "quote":
        post_keys += ["text", "source"]
      elif post["type"] == "link":
        post_keys += ["title", "url"]
      elif post["type"] == "audio":
        post_keys += ["caption", "plays"]
      elif post["type"] == "video":
        post_keys += ["caption", "player"]
      else:
        continue

      posts_array.append([post.get(key) for key in post_keys])

    if before != None:
      tumblr_search(options, search_phrase=search_phrase, paginate_older_attribute=before)

if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default=get_search_term())
  argparser.add_argument("--max-results", help="Max results", default=20)
  args = argparser.parse_args()

  try:
    for search_phrase in get_search_term():
      tumblr_search(args, search_phrase=search_phrase)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
  finally:
    write_to_csv(posts_array, header)