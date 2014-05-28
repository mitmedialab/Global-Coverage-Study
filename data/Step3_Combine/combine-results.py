import csv, json

country_info = {}
media_types = []
media_sources = []

# First load in all the info
print "Loading data..."
print "  Loading story counts by type and country"
with open('data/stories-by-type-and-country.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    media_types = reader.next()[1:]
    for row in reader:
    	country = row[0]
    	if country not in country_info:
    		country_info[country] = {}
    	count_by_type = dict(zip(media_types,row[1:]))
        country_info[country]['count_by_type'] = count_by_type
print "  Loading story counts by source and country"
with open('data/stories-by-source-and-country.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    media_sources = reader.next()[1:]
    for row in reader:
    	country = row[0]
    	if country not in country_info:
    		country_info[country] = {}
    	count_by_source = dict(zip(media_sources,row[1:]))
        country_info[country]['count_by_source'] = count_by_source
print "  Loading country data"
with open('data/WorldPopAndGDP.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    data_pieces = reader.next()[3:]
    for row in reader:
    	country = row[1]
    	if country not in country_info:
    		country_info[country] = {}
    	count_by_source = dict(zip(data_pieces,row[1:]))
        country_info[country]['data'] = count_by_source
print "done"

print country_info.values()[0]['count_by_type']

# Now compute percentages for types and sources
print "Normalizing..."
print "  Normalizing type info"
for media_type in media_types:
	total = 0
	for info in country_info.values():
		if 'count_by_type' in info:
			total = total + int(info['count_by_type'][media_type])
for info in country_info.values():
	if 'count_by_type' in info:
		info['pct_by_type'] = {}
		for media_type in media_types:
			info['pct_by_type'][media_type] = float(info['count_by_type'][media_type])/float(total)
print "  Normalizing source info"
for media_source in media_sources:
	total = 0
	for info in country_info.values():
		if 'count_by_source' in info:
			total = total + int(info['count_by_source'][media_source])
for info in country_info.values():
	if 'count_by_source' in info:
		info['pct_by_source'] = {}
		for media_type in media_types:
			info['pct_by_source'][media_source] = float(info['count_by_source'][media_source])/float(total)

print country_info['RUS']

print "done"
