#!/usr/bin/python

import ast
import csv
import json
from collections import defaultdict

dict = defaultdict(int)
with open('youtube_results.csv', 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',', quotechar='\"')
	for row in reader:
		tags = row.get('tags')
		try:
			tags = ast.literal_eval(tags)
			for tag in tags:
				dict[tag] += 1
		except:
			pass

with open('youtube_sets', 'wb') as dictfile:
	dictfile.write(json.dumps(dict))



dict = defaultdict(int)
with open('tumblr_results.csv', 'rb') as csvfile:
	reader = csv.DictReader(csvfile, delimiter=',', quotechar='\"')
	for row in reader:
		tags = row.get('tags')
		try:
			tags = ast.literal_eval(tags)
			for tag in tags:
				dict[tag] += 1
		except:
			pass

with open('tumblr_sets', 'wb') as dictfile:
	dictfile.write(json.dumps(dict))
