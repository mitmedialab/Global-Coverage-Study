import os, math, csv, ConfigParser, time
from operator import itemgetter
import mediacloud

class MediaSourceCollection():
    '''
    
    '''

    def __init__(self,mc_api_key):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.media_sources = []
        self.cache_time = None
        self.cache_content = None
        # connect to Media Cloud
        self.mediacloud = mediacloud.api.MediaCloud(mc_api_key)

    def listWithSentenceCounts(self):
        now = int(time.time())
        if (self.cache_time is None) or (now-self.cache_time > 60*60):
            media_list = []
            for media_source in self.media_sources:
                info = media_source
                info['sentence_count'] = self._mediaSentenceCount(info['media_id'])
                media_list.append(info)
            self.cache_content = media_list
            self.cache_time = int(time.time())
        return self.cache_content

    def _mediaSentenceCount(self,media_id):
        try:
            res = self.mediacloud.sentenceList('*', 
                '+publish_date:[2014-04-01T00:00:00Z TO 2014-04-30T23:59:59Z] AND +media_id:'+str(media_id),
                0,0)
            return res['response']['numFound']
        except ValueError:
            return -1

    def loadAllMediaIds(self):
        self.loadFromCsv(self.current_dir+'/data/alexa-top-broadcast.csv')
        self.loadFromCsv(self.current_dir+'/data/alexa-top-magazine.csv')
        self.loadFromCsv(self.current_dir+'/data/alexa-top-newspaper.csv')
        self.loadFromCsv(self.current_dir+'/data/alexa-top-online.csv')
        self._sortByMediaId()

    def _sortByMediaId(self):
        self.media_sources.sort(key=itemgetter('category','media_id'))

    def mediaSources(self):
        return self.media_sources

    def loadFromCsv(self,file_path):
        url_col = 0
        category_col = 1
        id_col = 4
        source_list = []
        with open(file_path, 'rb') as csvfile:
            csv_reader = csv.reader(csvfile)
            csv_reader.next()   # skip header row
            for row in csv_reader:
                source = {
                    'url': row[url_col],
                    'category': row[category_col],
                    'media_id': row[id_col]
                }
                source_list.append( source )
        self.media_sources += source_list
        return len(source_list)

    def count(self):
        return len(self.media_sources)
