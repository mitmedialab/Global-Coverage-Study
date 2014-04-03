import logging, os, json, ConfigParser
import requests
from operator import itemgetter
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

# Query CLIFF to pull out entities from one story
def geoparseSingleText(text):
	try:
		params = {'q':text}
		r = requests.get(geoserver_url, params=params)
		entities = r.json()
		return entities
	except requests.exceptions.RequestException as e:
		print "ERROR RequestException " + str(e)

# Find records that don't have geodata and geocode them
stories = db_collection.find({ 'entities': {'$exists':False} })
for story in stories:
	sorted_sentences = [s['sentence'] for s in sorted(story['story_sentences'], key=itemgetter('sentence_number'))]
	story_text = ' '.join(sorted_sentences)
	story['entities'] = geoparseSingleText(story_text)
	db_collection.save(story)
	print "Saved " + sorted_sentences[0][0:40] + "..."

