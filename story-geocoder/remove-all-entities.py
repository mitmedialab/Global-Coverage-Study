import logging, os, json, ConfigParser, sys
from operator import itemgetter
import requests
from mediameter.db import GeoStoryDatabase

logging.basicConfig(filename='geocoder.log',level=logging.DEBUG)
log = logging.getLogger('geocoder')
log.info("---------------------------------------------------------------------------")
log.info("Deleting geo-coded info! ")

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

db = GeoStoryDatabase(config.get('db','name'))

storyCount = db.storyCount()
log.info(str(storyCount)+" stories to process")

done = 0
last_pct = None
for story in db.allStories():
    if 'entities' in story:
        del story['entities']
        db.updateStory(story)
    done = done + 1

    pct_done = round((float(done)/float(storyCount))*100)
    if (pct_done % 10 == 0) and (pct_done != last_pct):
        print str(pct_done)+'%'
        last_pct = pct_done
