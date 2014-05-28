import csv, json

country_info = {}
media_types = []
media_sources = []
data_pieces = []

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
        count_of_type = dict(zip(media_types,row[1:]))
        country_info[country]['count_of_type'] = count_of_type
print "  Loading story counts by source and country"
with open('data/stories-by-source-and-country.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    media_sources = reader.next()[1:]
    for row in reader:
        country = row[0]
        if country not in country_info:
            country_info[country] = {}
        count_of_source = dict(zip(media_sources,row[1:]))
        country_info[country]['count_of_source'] = count_of_source
print "  Loading country data"
with open('data/WorldPopAndGDP.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    data_pieces = reader.next()[3:]
    for row in reader:
        country = row[1]
        if country not in country_info:
            country_info[country] = {}
        count_of_source = dict(zip(data_pieces,row[3:]))
        country_info[country]['data'] = count_of_source
print "done"

# Now compute percentages for types and sources
print "Normalizing..."
print "  Normalizing type info"
for media_type in media_types:
    total = 0
    for info in country_info.values():
        if 'count_of_type' in info:
            total = total + int(info['count_of_type'][media_type])
for info in country_info.values():
    if 'count_of_type' in info:
        info['pct_of_type'] = {}
        for media_type in media_types:
            info['pct_of_type'][media_type] = 100.0*float(info['count_of_type'][media_type])/float(total)
print "  Normalizing source info"
for media_source in media_sources:
    total = 0
    for info in country_info.values():
        if 'count_of_source' in info:
            total = total + int(info['count_of_source'][media_source])
for info in country_info.values():
    if 'count_of_source' in info:
        info['pct_of_source'] = {}
        for media_source in media_sources:
            info['pct_of_source'][media_source] = 100.0*float(info['count_of_source'][media_source])/float(total)
print "done"

# print out combined results
print "Combining results..."
data_pieces = sorted(data_pieces)
media_types = sorted(media_types)
media_sources = sorted(media_sources)
csvfile = open('combined-data.csv', 'wb') 
csvwriter = csv.writer(csvfile)
header = [ 'country' ]
header = header + data_pieces + media_types + media_sources
csvwriter.writerow(header)
for country in sorted(country_info.keys()):
    row = [ country ]
    for data_piece in data_pieces:
        if 'data' in country_info[country]:
            row.append( country_info[country]['data'][data_piece] )
        else:
            row.append("")
    for media_type in media_types:
        if 'pct_of_type' in country_info[country]:
            row.append( round(country_info[country]['pct_of_type'][media_type],4) ) 
        else:
            row.append("")
    for media_source in media_sources:
        if 'pct_of_source' in country_info[country]:
            row.append( round(country_info[country]['pct_of_source'][media_source],4) )
        else:
            row.append("")
    csvwriter.writerow(row)

print "done"
