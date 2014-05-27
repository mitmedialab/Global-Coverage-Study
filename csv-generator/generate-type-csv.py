import sys, time, ConfigParser, os, csv
import iso3166

from mediameter.db import GeoStoryDatabase

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

# connect to database
db = GeoStoryDatabase(config.get('db','name'), config.get('db','host'))

type_country_count = {}

# get list of all media sources
print "Starting to generate csv"
media_counts = db.mediaTypeStoryCounts()
for media_type, media_story_count in media_counts.iteritems():
    print "  Working on "+media_type+" type ("+str(media_story_count)+" articles)"
    type_country_count[media_type] = {}
    # setup tfidf computation
    all_countries = db.allAboutCountries(media_type)
    for country_code in all_countries:
        count = db.storiesOfType(media_type,country_code).count()
        type_country_count[media_type][country_code] = count

print "Writing output CSV"

with open("output/stories-by-type-and-country.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    types = sorted( type_country_count.keys() )
    countries = sorted( db.allAboutCountries() )
    writer.writerow( ['country'] + types )
    for country in countries:
        try:
            row = [ iso3166.countries.get(country).alpha3 ]
        except KeyError:
            print "Unknown country "+str(country)+" - skipping"
            continue
        for media_type in types:
            count = 0
            if country in type_country_count[media_type]:
                count = type_country_count[media_type][country]
            else:
                count = 0
            row.append( count )
        writer.writerow(row)

print "  done"
