import logging, ConfigParser, sys, json, time, os
import csv
import mediacloud
import mediameter.source
from mediameter.db import GeoStoryDatabase

STORIES_PER_PAGE = 1000

logging.basicConfig(filename='fetcher.log',level=logging.DEBUG)
log = logging.getLogger('fetcher')
log.info("======================================================================")

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

# connect to everything
collection = mediameter.source.MediaSourceCollection(config.get('api','key'))
collection.loadAllMediaIds()
mc = collection.mediacloud
db = GeoStoryDatabase(config.get('db','name'))

log.info('Loaded '+str(collection.count())+' media sources to pull')

# walk through all the sources, grabbing all the stories from each
skipped_story_counts = []
for source_count, source in enumerate(collection.mediaSources()[:1]):
    log.info("---------------------------------------------------------------------------")
    log.info('  Starting with %s (%s): %s %d of %d' % (
        source['url']
        , source['media_id']
        , source['category']
        , source_count
        , len(collection.mediaSources())
    ))
    
    last_processed_stories_id = db.maxStoryProcessedId(source['media_id'])  # pick up where the db left off last run

    query_str = '*'
    extra_args = {'category':source['category'], 'media_source_url':source['url']}
    filter_str = config.get('query', 'dates')+' AND +media_id:'+str(source['media_id'])

    # page through the stories, saving them in the DB
    skipped_ap_stories = 0
    more_stories = True
    while more_stories:
        log.info('    loading stories from '+str(last_processed_stories_id))
        try:
            stories = mc.storyList(query_str, filter_str, last_processed_stories_id, STORIES_PER_PAGE, text=True)
            if len(stories) > 0:
                for story in stories:
                    if story['ap_syndicated'] == 0:
                        saved = db.addStory(story, {'type':source['category']})
                        if saved:
                            log.debug('  saved '+str(story['processed_stories_id']))
                        else:
                            log.debug('  skipped '+str(story['processed_stories_id']))
                    else:
                        skipped_ap_stories = skipped_ap_stories + 1
                        log.debug('  skipped AP story '+str(story['processed_stories_id']))
                last_processed_stories_id = stories[len(stories)-1]['processed_stories_id']
                more_stories = True
            else:
                more_stories = False
        except Exception as e:
            # probably a 404, so sleep and then just try again
            log.info('  '+str(e))
            time.sleep(1)
    log.info('  Done with '+source['url']+' ('+source['media_id']+'): '+source['category'])
    skipped_story_counts.append({ 
        'media_id': source['media_id'],
        'url': source['url'],
        'category': source['category'],
        'skipped_ap': skipped_ap_stories
    })

with open('output/skipped_ap_story_counts.csv', 'wb') as csv_file:
    field_names = ['media_id', 'url', 'category', 'skipped_ap']
    writer = csv.DictWriter(csv_file, fieldnames=field_names)
    writer.writeheader()
    for row in skipped_story_counts:
       writer.writerow(row)
