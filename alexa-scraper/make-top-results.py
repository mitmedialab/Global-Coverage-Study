import codecs, csv, os.path, logging, sys
from operator import itemgetter

DATA_DIR = 'data'
TOP_N = 20

# input column indices 
DOMAIN_COL = 1
AGREED_TYPE_COL = 9
AGREED_COUNTRY_COL = 10
GLOBAL_RANK_COL = 11
SOURCE_TYPES = [ 'broadcast', 'newspaper', 'magazine', 'online']

# output colum indices
OUT_DOMAIN_COL = 0
OUT_TYPE_COL = 1
OUT_COUNTRY_COL = 2
OUT_GLOBAL_RANK_COL = 3

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logging.info("Starting to create results spreadsheets:")

def load_and_clean_source_list(file_name):
    '''
    Load a 'X-golden-metadata' CSV and grab just the columns we need (domain, type, country, global rank).
    '''
    cleaned_sources = []
    source_csv = csv.reader( codecs.open(os.path.join(DATA_DIR,file_name), encoding='utf-8', mode='r') )
    source_csv.next()   # skip header row
    for row in source_csv:
        cleaned_sources.append( [ row[DOMAIN_COL], row[AGREED_TYPE_COL], row[AGREED_COUNTRY_COL], row[GLOBAL_RANK_COL] ] )
    return cleaned_sources

def domain_in_sources_already(source_list, domain):
    '''
    Is a domain in the source_list already?
    '''
    for row in source_list:
        if row[OUT_DOMAIN_COL]==domain:
            return True
    return False

def load_combined_source_list():
    '''
    Load the news and arts golden-metadata lists, combine them, clean them, and return 
    a list of domains / rank tuple sorted by global rank 
    '''
    # load the two lists
    news_sources = load_and_clean_source_list('alexa-news-ranks-golden-metadata.csv')
    arts_sources = load_and_clean_source_list('alexa-arts-ranks-golden-metadata.csv')
    # combine the lists
    raw_combined_sources = news_sources + arts_sources
    # get rid of the duplicates
    combined_sources = []
    for source in raw_combined_sources:
        if not domain_in_sources_already(combined_sources,source[0]):
            combined_sources.append( source )
    # turn global rank into number for comparing them
    for idx in range(0,len(combined_sources)):
        combined_sources[idx][OUT_GLOBAL_RANK_COL] = int(combined_sources[idx][OUT_GLOBAL_RANK_COL])
    # combine sources by global rank
    grouped_sources = {}    # global rank => [ domain* ]
    for source in combined_sources:
        if source[OUT_TYPE_COL] in SOURCE_TYPES:   # filter for only the SOURCE_TYPES we care about
            if source[OUT_GLOBAL_RANK_COL] not in grouped_sources:
                grouped_sources[ source[OUT_GLOBAL_RANK_COL] ] = [ 
                    [ source[OUT_DOMAIN_COL] ],
                    [ source[OUT_TYPE_COL] ], 
                    source[OUT_COUNTRY_COL], 
                    source[OUT_GLOBAL_RANK_COL]
                ]
            else:
                grouped_sources[ source[OUT_GLOBAL_RANK_COL] ][OUT_DOMAIN_COL].append( source[OUT_DOMAIN_COL] )
    for rank in grouped_sources:
        grouped_sources[rank][OUT_TYPE_COL] = max(set(grouped_sources[rank][OUT_TYPE_COL]), key=grouped_sources[rank][OUT_TYPE_COL].count)  # pick the most common one
    # sort by global rank
    combined_sources = sorted(grouped_sources.values(), key=itemgetter(OUT_GLOBAL_RANK_COL))
    logging.info('  Combined, filered, and sorted '+str(len(combined_sources))+' arts and news rankings')
    return combined_sources

def write_top_sources_csv(source_type):
    matching_sources = [row for row in all_sources if row[1]==source_type]
    logging.info('  Found '+str(len(matching_sources))+' '+source_type+' sources')
    output_file = os.path.join(DATA_DIR, 'alexa-top-'+source_type+'.csv')
    csv_writer = csv.writer( codecs.open(output_file, encoding='utf-8', mode='w'), delimiter=',' )
    csv_writer.writerow( ['domain','type','country','global rank'] )
    for source in matching_sources[:TOP_N]:
        source[OUT_DOMAIN_COL] = ",".join( source[OUT_DOMAIN_COL] )
        csv_writer.writerow( source )
    logging.info('    wrote top '+str(TOP_N)+' to '+output_file)
    return False

# load sources, merge, and write out top N list for each
all_sources = load_combined_source_list()   # global var used in functions
for source_type in SOURCE_TYPES:
    write_top_sources_csv( source_type )
