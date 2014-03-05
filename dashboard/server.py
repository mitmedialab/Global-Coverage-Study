import os, sys, time, logging, ConfigParser
from flask import Flask, render_template
import media.source

app = Flask(__name__)

# setup logging
logging.basicConfig(filename='mc-server.log',level=logging.DEBUG)
log = logging.getLogger('mc-server')
log.info("---------------------------------------------------------------------------")

stat_engine = media.source.MediaSourceCollection()
stat_engine.loadAllMediaIds()

@app.route("/")
def index():
    media_info = stat_engine.listWithSentenceCounts()
    return render_template("base.html",
        media_info = media_info
    )

if __name__ == "__main__":
    app.debug = True
    app.run()
