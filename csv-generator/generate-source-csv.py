import sys, time, ConfigParser, os, csv
from iso3166 import countries
from operator import itemgetter

from mediameter.db import GeoStoryDatabase
import mediameter.source

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

# connect to database
db = GeoStoryDatabase(config.get('db','name'), config.get('db','host'))

collection = mediameter.source.MediaSourceCollection(config.get('api','key'))
collection.loadAllMediaIds()

source_country_count = {}
media_sources = sorted(collection.mediaSources(), key=itemgetter('url'))
all_countries = sorted(db.allPrimaryCountries())


print "Starting to generate csv"

for source in media_sources:
    media_id = source['media_id']
    print "  Working on "+source['url']+" ("+str(media_id)+")"
    source_country_count[media_id] = {}
    for country_code in all_countries:
        count = db.storyFromSourceAboutCountry(media_id,country_code)
        source_country_count[media_id][country_code] = count

print "Writing output CSV"

with open("output/stories-by-source-and-country.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    countries = sorted( db.allPrimaryCountries() )
    media_source_urls = [source['url'] for source in media_sources]
    writer.writerow( ['country'] + media_sources )
    for country in countries:
        row = [ country ]
        for source in media_sources:
            media_id = source['media_id']
            count = 0
            if country in source_country_count[media_id]:
                count = source_country_count[media_id][country]
            else:
                count = 0
            row.append( count )
        writer.writerow(row)

print "  done"
