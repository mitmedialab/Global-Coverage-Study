import logging, os, json, ConfigParser, sys
from operator import itemgetter
import requests
from mediameter.db import GeoStoryDatabase

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('geocoder')

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')
log.info("Deleting all geocoding results from the db (%s)" % config.get('db','name'))

db = GeoStoryDatabase(config.get('db','name'))

story_count = db.allStories().count()
cliffed_story_count = db.storiesWithCliffInfo().count()
log.info("  %d stories total. %d have cliff info." % (story_count,cliffed_story_count))

done = 0
last_pct = None
for story in db.storiesWithCliffInfo():
    if mediameter.db.CLIFF_RESULTS_ATTR in story:
        del story[mediameter.db.CLIFF_RESULTS_ATTR]
        del story[mediameter.db.CLIFF_COUNTRIES_FOCUS_ATTR]
        db.updateStory(story)
    done = done + 1

    pct_done = round((float(done)/float(story_count))*100)
    if (pct_done % 10 == 0) and (pct_done != last_pct):
        print str(pct_done)+'%'
        last_pct = pct_done

log.info("Done")