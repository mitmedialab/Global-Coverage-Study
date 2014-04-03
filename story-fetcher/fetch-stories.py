import logging, ConfigParser, sys, json
import mediacloud
import dashboard.source

DB_NAME = 'mc_geostudy'
STORIES_PER_PAGE = 1000

logging.basicConfig(filename='scraper.log',level=logging.DEBUG)
log = logging.getLogger('scaper')
log.info("---------------------------------------------------------------------------")

dashboard = dashboard.source.MediaSourceCollection()
dashboard.loadAllMediaIds()
mc = dashboard.mediacloud
db = mediacloud.storage.MongoStoryDatabase(DB_NAME)

log.info('Loaded '+str(dashboard.count())+' media sources to pull')

# walk through all the sources, grabbing all the stories from each
for source in dashboard.mediaSources():
    log.info('  Starting with '+source['url']+' ('+source['media_id']+'): '+source['category'])
    
    query_str = '*'
    extra_args = {'category':source['category'], 'media_source_url':source['url']}
    filter_str = '+publish_date:[2014-03-01T00:00:00Z TO 2014-03-31T00:00:00Z] AND +media_id:'+str(source['media_id'])

    # page through the stories, saving them in the DB
    more_stories = True
    last_processed_stories_id = 0
    while more_stories:
        log.info('    loading stories from '+str(last_processed_stories_id))
        stories = mc.storyList(query_str, filter_str, last_processed_stories_id, STORIES_PER_PAGE)
        for story in stories:
            db.addStory(story, {'type':source['category']})
        last_processed_stories_id = stories[len(stories)-1]['stories_id']
        more_stories = True if len(stories)>0 else False
