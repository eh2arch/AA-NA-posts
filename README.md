AA-NA posts
===========

0. It contains python scripts to fetch AA and NA related posts for Youtube and Tumblr OSNs:
0. Contains csv files for youtube and tumblr results
0. Tumblr and Youtube sets contain dictionaries of the tags taken from the existing results.
0. The `word_cloud.html` file uses d3 cloud layout to display the top 100 tags to get a better understanding of how to search for terms when querying the API

Salient Points
--------------

* Youtube search is conducted through the | (OR) approach specified in its API. The search terms have been found out by finding synsets for some terms like recovery|rehab etc. from the wordnet corpus through the nltk package and then using a OR structure to find better results. This enabled to eliminate the number of separate searches needed and the redundant matching video links

* Tumblr doesn't support such a query structure and hence uses a `Tagged` search in its API with numerous query terms to search for a variety of supported content like Text, Photo, Quote, Link, Video, Audio

* Both OSNs paginate to retrieve further results

* For Youtube the following results have been saved for a video: `'id', 'title', 'description', 'channelId', 'publishedAt', 'tags', 'viewCount', 'likeCount', 'dislikeCount', 'favoriteCount', 'commentCount'`

* For Tumblr the following results have been saved for a post: `"post_url", "date", "tags", "type", "misc", "misc"` where misc depends on the type of the post

Issues
------

* Youtube returns about 500 unique results regardless of `totalResults` being much much more. After that results start duplicating. Issue better described [here](https://code.google.com/p/gdata-issues/issues/detail?id=4282)
* The Tumblr csv doesn't contain all the results from all the query terms specified as the number of results are huge.
* Word Cloud html currently shows only one word cloud. This can easily be changed and is just for purposes of seeking out better results

Dependencies
------------

* `MongoDB`
* `NLTK`
* `pytumblr`
```
pip install pytumblr
```
* Youtube and Tumblr API keys

Usage
-----

```
python retrieve_youtube.py
```

or for tumblr

```
python retrieve_tumblr.py
```

Optional arguments include `--q search_term` and `--max_results 20`

Sample Word Cloud
-----------------

![Alt Youtube](youtube_tag_cloud.png?raw=true "Youtube Tag Cloud")
![Alt Tumblr](tumblr_tag_cloud.png?raw=true "Tumblr Tag Cloud")