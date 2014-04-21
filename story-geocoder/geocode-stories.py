import logging, os, json, ConfigParser, sys, Queue, threading, time
from operator import itemgetter
import requests
from mediameter.db import GeoStoryDatabase

THREADS_TO_RUN = 20
STORIES_AT_TIME = 5000

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

cliff_url = config.get('cliff','url')

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
            entities = fetchEntitiesFromCliff(text)
            if entities is not None:
                story = db.getStory(story_id)
                story['entities'] = entities
                db.updateStory(story)
                log.info("  updated "+str(story_id))
            self.queue.task_done()

# Query CLIFF to pull out entities from one story
def fetchEntitiesFromCliff(text):
    try:
        params = {'q':text}
        r = requests.get(cliff_url, params=params)
        entities = r.json()
        if entities['status']!='ok':
            return None
        return entities
    except requests.exceptions.RequestException as e:
        log.warn("ERROR RequestException " + str(e))

# Find records that don't have geodata and geocode them
storiesToDo = db.storiesWithoutCliffInfo().count()
while storiesToDo>0:
    start_time = time.time()

    storiesToDo = db.storiesWithoutCliffInfo().count()
    log.info( str(storiesToDo)+" stories left without cliff info" )

    to_process = []
    for story in db.storiesWithoutCliffInfo(STORIES_AT_TIME):
        if 'story_sentences' in story:
            sorted_sentences = [s['sentence'] for s in sorted(story['story_sentences'], key=itemgetter('sentence_number'))]
            story_text = ' '.join(sorted_sentences)
            to_process.append({ 'id': story['_id'], 'text': story_text })
    log.info("Queued "+str(len(to_process))+" stories")
    engine = Engine(to_process)
    engine.run()
    log.info("done with one round")

    durationSecs = float(time.time() - start_time)
    log.info( str( round(durationSecs/STORIES_AT_TIME,4) )+" secs per story this round" )
