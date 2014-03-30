import logging
import os
import ConfigParser
import requests
import json
import pymongo
from pymongo import MongoClient


logging.basicConfig(filename='geocoder.log',level=logging.DEBUG)
log = logging.getLogger('geocoder')
log.info("---------------------------------------------------------------------------")

CONFIG_FILENAME = 'geo.config'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,CONFIG_FILENAME))

db_client = MongoClient()
db = db_client[config.get('db','name')]
db_collection = db[config.get('db','collection')]

geoserver_url = config.get('geoparser','geoserver_url')


#pull out geodata for single text from CLIFF_CLAVIN
def geoparseSingleText(text):
	try:
		params = {'text':text}
		
		r = requests.get(geoserver_url, params=params)
		
		geodata = r.json()

		if "places" in geodata.keys() and any(geodata["places"]):
			return geodata
		else: 
			return {}	

	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)

# Sorting function for sorting sentences out of MC MongoDB
def asint(s):
    try: return int(s), ''
    except ValueError: return sys.maxint, s

# Find records that don't have geodata
q = db_collection.find({ 'geodata': {'$exists':False} })
for doc in q:
	sortedSentences= [(doc["sentences"][k]) for k in sorted(doc["sentences"], key=asint)]
	story = ' '.join(sortedSentences)
	doc["geodata"] = geoparseSingleText(story)
	db_collection.save(doc)
	print "Saved " + sortedSentences[0][0:40] + "..."

