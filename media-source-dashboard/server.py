import os, sys, time, logging, ConfigParser
from flask import Flask, render_template
import mediameter.source
from mediameter.db import GeoStoryDatabase

app = Flask(__name__)

# setup logging
logging.basicConfig(filename='mc-server.log',level=logging.DEBUG)
log = logging.getLogger('mc-server')
log.info("---------------------------------------------------------------------------")

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

# connect to db and media cloud
db = GeoStoryDatabase(config.get('db','name'), config.get('db','host'))
collection = mediameter.source.MediaSourceCollection(config.get('api','key'))

collection.loadAllMediaIds()

@app.route("/")
def index():
    local_story_counts = db.mediaStoryCounts()
    media_info = collection.listWithSentenceCounts()
    for m in media_info:
    	m['db_stories'] = local_story_counts[int(m['media_id'])] if int(m['media_id']) in local_story_counts else 0
    total_mc_stories = sum( [m['sentence_count'] for m in media_info] )
    total_db_stories = db.allStories().count()
    total_geocoded_stories = total_db_stories - db.storiesWithoutCliffInfo().count()
    return render_template("base.html",
        media_info = media_info,
        total_mc_stories = total_mc_stories,
        total_db_stories = total_db_stories,
        geocoded_pct = int(round(float(total_geocoded_stories)/float(total_db_stories),2)*100)
    )

def number_format(value):
    return "{:,}".format(value)
app.jinja_env.filters['number_format'] = number_format

if __name__ == "__main__":
    app.debug = True
    app.run()
