import logging, ConfigParser, sys, json
import mediacloud

MEDIA_ID = 1094
DB_NAME = 'mc_geostudy'
SENTENCES_PER_PAGE = 10000

# prep shared args
query_str = '*'
filter_str = '+publish_date:[2014-03-01T00:00:00Z TO 2014-03-31T00:00:00Z] AND +media_id:'+str(MEDIA_ID)

# connect to the media cloud
config = ConfigParser.ConfigParser()
config.read('mc-client.config')
mc = mediacloud.api.MediaCloud(config.get('api','user'),config.get('api','pass'))

# create a db
db = mediacloud.storage.MongoStoryDatabase(DB_NAME)

# count the sentences
res = mc.sentencesMatching(query_str, filter_str)
sentence_count = res['response']['numFound']
logging.info(sentence_count)

# walk all the sentences creating stories in the db
current = 0
while current < sentence_count:
    stories = mc.sentencesMatchingByStory(query_str, filter_str, current, SENTENCES_PER_PAGE)
    for story_sentences in stories.values():
        db.addStoryFromSentences(story_sentences)
    current = current + SENTENCES_PER_PAGE
