import logging, ConfigParser, sys, json
import mediacloud
import dashboard.source

DB_NAME = 'mc_geostudy'
SENTENCES_PER_PAGE = 10000

logging.basicConfig(filename='scraper.log',level=logging.DEBUG)
log = logging.getLogger('scaper')
log.info("---------------------------------------------------------------------------")

dashboard = dashboard.source.MediaSourceCollection()
dashboard.loadAllMediaIds()
mc = dashboard.mediacloud
db = mediacloud.storage.MongoStoryDatabase(DB_NAME)

log.info('Loaded '+str(dashboard.count())+' media sources to pull')

# walk through all the sources, saving the sentences
for source in dashboard.mediaSources():
    log.info('  Starting with '+source['url']+' ('+source['media_id']+'): '+source['category'])
    
    query_str = '*'
    extra_args = {'category':source['category'], 'media_source_url':source['url']}
    filter_str = '+publish_date:[2014-03-01T00:00:00Z TO 2014-03-31T00:00:00Z] AND +media_id:'+str(source['media_id'])
    
    # count the sentences
    res = mc.sentencesMatching(query_str, filter_str)
    sentence_count = res['response']['numFound']
    log.info('    Found '+str(sentence_count)+' sentences')

    # walk all the sentences creating stories in the db
    current = 0
    while current < sentence_count:
        log.info('    loading sentences from '+str(current))
        stories = mc.sentencesMatchingByStory(query_str, filter_str, current, SENTENCES_PER_PAGE)
        for story_sentences in stories.values():
            db.addStoryFromSentences(story_sentences,{'type':source['category']})
        current = current + SENTENCES_PER_PAGE
