import logging, os, json, ConfigParser, sys, Queue, threading, time
from operator import itemgetter
import requests

import mediameter.cliff
from mediameter.db import GeoStoryDatabase

# This is meant to be run from a cron job every N minutes

THREADS_TO_RUN = 1
STORIES_AT_TIME = 10

logging.basicConfig(filename='geocoder.log',level=logging.INFO)
log = logging.getLogger('geocoder')
log.info("---------------------------------------------------------------------------")

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

# connect to everything
db = GeoStoryDatabase(config.get('db','name'))
cliff = mediameter.cliff.Cliff(config.get('cliff','host'),config.get('cliff','port'))

class Engine:
    def __init__(self, texts):
        self.queue = Queue.Queue()
        for text in texts:
            self.queue.put((text['id'], text['text']))
            
    def run(self):
        num_workers = THREADS_TO_RUN
        for i in range(num_workers):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
        self.queue.join()
        
    def worker(self):
        while True:
            story_id, text = self.queue.get()
            try:
                cliff_results = cliff.parseText(text)
                if cliff_results['status'] == cliff.STATUS_OK:
                    log.debug("  loading story "+story_id)
                    story = db.getStory(story_id)
                    story[mediameter.db.CLIFF_RESULTS_ATTR] = cliff_results
                    story[mediameter.db.CLIFF_COUNTRIES_FOCUS_ATTR] = []
                    if 'counties' in cliff_results['results']['places']['focus']:
                        story[mediameter.db.CLIFF_COUNTRIES_FOCUS_ATTR] = [ c['countryCode'] 
                            for c in cliff_results['results']['places']['focus']['countries']]
                    db.updateStory(story)
                    log.info("  updated "+str(story_id))
            except requests.exceptions.RequestException as e:
                log.warn("ERROR RequestException " + str(e))                
            self.queue.task_done()

# Find records that don't have geodata and geocode them
storiesToDo = db.storiesWithoutCliffInfo().count()
log.info("Found %d stories to process." % storiesToDo)
while storiesToDo>0:
    start_time = time.time()

    storiesToDo = db.storiesWithoutCliffInfo().count()
    log.info( str(storiesToDo)+" stories left without cliff info" )

    to_process = []
    for story in db.storiesWithoutCliffInfo(STORIES_AT_TIME):
        # we don't get the story text in one block, so we have to stitch it back
        # together from the sentences (in the correct order)
        if 'story_sentences' in story:
            sorted_sentences = [s['sentence'] for s in sorted(story['story_sentences'], key=itemgetter('sentence_number'))]
            story_text = ' '.join(sorted_sentences)
            if len(story_text) == 0:
                # Empty story text will make CLIFF fail, throw in a failsafe
                story_text = 'the'
            to_process.append({ 'id': story['stories_id'], 'text': story_text })
    log.info("Queued "+str(len(to_process))+" stories")
    engine = Engine(to_process)
    engine.run()
    log.info("done with one round")

    durationSecs = float(time.time() - start_time)
    log.info( str( round(durationSecs/STORIES_AT_TIME,4) )+" secs per story this round" )
