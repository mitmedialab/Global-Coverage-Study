import requests, os.path, csv, logging, codecs, time, re
from bs4 import BeautifulSoup
import tldextract

import cache

DOMAIN_COL = 1
DATA_DIR = 'data'
SITE_INFO_BASE_URL = "http://www.alexa.com/siteinfo/"

logging.basicConfig(level=logging.DEBUG)
logging.info("Starting metadata scraper:")

def fetch_webpage(url, use_cache=True):
    key = cache.md5_key(url)
    if use_cache and cache.contains(key):
        return cache.get(key)
    content = requests.get(url).text
    cache.put(key,content)
    return content

def extract_metadata(content):
    soup = BeautifulSoup(content)
    info = {}
    strongs = soup.find_all('strong', class_="font-big2")
    info['global_rank'] = re.sub("[^0-9]", "", strongs[0].a.string) # remove commas
    info['us_rank'] = re.sub("[^0-9]", "", strongs[1].a.string) # remove commas
    info['bounce_rate'] = strongs[2].string
    info['page_views'] = strongs[3].string
    info['time_on_site'] = strongs[4].string
    return info

def scrape_page(url):
    content = fetch_webpage(url)
    return extract_metadata(content)

def add_metadata_to_category_csv(file_name):
    source_csv = csv.reader( codecs.open(os.path.join(DATA_DIR,file_name), encoding='utf-8', mode='r') )
    header = source_csv.next()
    output_file = os.path.join(DATA_DIR, file_name[:-4]+'-metadata.csv')
    csv_writer = csv.writer( codecs.open(output_file, encoding='utf-8', mode='w'), delimiter=',' )
    csv_writer.writerow( header[:-1] + [ 'global rank', 'us rank', 'bounce rate', 'daily pageview', 'daily time on site'])
    for source_row in source_csv:
        logging.info( '  '+source_row[DOMAIN_COL] )
        site_info_url = SITE_INFO_BASE_URL + source_row[DOMAIN_COL]
        i = scrape_page( site_info_url )
        csv_writer.writerow( source_row[:-1] + [ i['global_rank'], i['us_rank'], i['bounce_rate'], i['page_views'], i['time_on_site'] ] )
        time.sleep(0.5)

add_metadata_to_category_csv('alexa-news-ranks-golden.csv')

add_metadata_to_category_csv('alexa-arts-ranks-golden.csv')

