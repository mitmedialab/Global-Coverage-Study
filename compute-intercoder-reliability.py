import codecs, csv, os.path, logging, sys

DATA_DIR = 'data'

# column indices
CD_TYPE_COL = 3
CD_COUNTRY_COL = 4
LL_TYPE_COL = 5
LL_COUNTRY_COL = 6
RB_TYPE_COL = 7
RB_COUNTRY_COL = 8
AGREED_TYPE_COL = 9
AGREED_COUNTRY_COL = 10

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Starting to compute intercoder reliability:")

# http://stackoverflow.com/questions/1518522/python-most-common-element-in-a-list
def most_common(lst):
    return max(set(lst), key=lst.count)

def compute_intercoder_reliability(input_file, output_file):
	logging.info("  Computing from "+input_file)
	csv_writer = csv.writer( codecs.open(output_file, encoding='utf-8', mode='w'), delimiter=',' )
	record_count = 0
	type_agree_count = 0
	country_agree_count = 0
	with codecs.open(input_file, encoding='utf-8', mode='r') as csvfile:
		output_row = ['rank','domain','url','CD type','CD country','LL type','LL country',
					  'RB type','RB country','type','country']
		csv_writer.writerow( output_row )
		csv_reader = csv.reader(csvfile, delimiter=',')
		csv_reader.next()	# skip two header rows
		csv_reader.next()
		for row in csv_reader:
			output_row = list(row)
			types = [x.strip().lower() for x in [ row[CD_TYPE_COL], row[LL_TYPE_COL], row[RB_TYPE_COL] ] ]
			unique_types = list(set(types))
			countries = [x.strip().lower() for x in [ row[CD_COUNTRY_COL], row[LL_COUNTRY_COL], row[RB_COUNTRY_COL] ] ]
			unique_countries = list(set(countries))
			if len(unique_types)==1:
				output_row.append( unique_types[0] )
				type_agree_count = type_agree_count + 1
			elif len(unique_types)==2:
				output_row.append( most_common(types) )
				type_agree_count = type_agree_count + 1
			else:
				output_row.append( 'ERROR' )
			if len(unique_countries)==1:
				output_row.append( unique_countries[0] )
				country_agree_count = country_agree_count + 1
			elif len(unique_countries)==2:
				output_row.append( most_common(countries) )
				country_agree_count = country_agree_count + 1
			else:
				output_row.append( 'ERROR' )
			csv_writer.writerow( output_row )
			record_count = record_count + 1
	logging.info('    Found '+str(record_count)+' rows')
	logging.info('    Agreed on '+str(type_agree_count)+' types') 
	logging.info('    Agreed on '+str(country_agree_count)+' countries') 

compute_intercoder_reliability( 
	os.path.join(DATA_DIR, 'alexa-arts-ranks-combined.csv') ,
	os.path.join(DATA_DIR, 'alexa-arts-ranks-golden.csv') 
)

compute_intercoder_reliability(
	os.path.join(DATA_DIR, 'alexa-news-ranks-combined.csv'),
	os.path.join(DATA_DIR, 'alexa-news-ranks-golden.csv') 
)