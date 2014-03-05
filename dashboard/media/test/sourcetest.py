
import unittest
import media.source

class MediaSourceCollectionTest(unittest.TestCase):

    def testLoadAllMediaIds(self):
        stat_engine = media.source.MediaSourceCollection()
        stat_engine.loadAllMediaIds()
        media_count = stat_engine.count()
        self.assertEquals(media_count,79)

    def testMediaCount(self):
        stat_engine = media.source.MediaSourceCollection()
        media_count = stat_engine.loadFromCsv('data/alexa-top-broadcast.csv')
        self.assertEquals(media_count,20)
        self.assertEquals(stat_engine.count(),20)
        self.assertEquals(len(stat_engine.mediaSources()),20)

    def testLoadFromCsv(self):
        stat_engine = media.source.MediaSourceCollection()
        media_count = stat_engine.loadFromCsv('data/alexa-top-broadcast.csv')
        self.assertEquals(media_count,20)

    def testMediaSentenceCount(self):
        stat_engine = media.source.MediaSourceCollection()
        sentence_count = stat_engine._mediaSentenceCount(1)
        self.assertTrue(sentence_count>0)    	

    def testListWithSentenceCounts(self):
        stat_engine = media.source.MediaSourceCollection()
        media_count = stat_engine.loadFromCsv('data/alexa-top-broadcast.csv')
    	media_info = stat_engine.listWithSentenceCounts()
    	print media_info

    def suite():
        return unittest.makeSuite(MediaSourceCollectionTest, 'test')
