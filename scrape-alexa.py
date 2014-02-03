import requests, md5, math, csv, logging
from bs4 import BeautifulSoup
import tldextract

import cache

URLS_PER_PAGE = 25
BASE_URL = "http://www.alexa.com/topsites/category"
NEWS_CATEGORY = "/Top/News"
ARTS_CATEGORY = "/Top/Arts"

def fetch_webpage(url, use_cache=True):
	key = cache.md5_key(url)
	if use_cache and cache.contains(key):
		return cache.get(key)
	content = requests.get(url).text
	cache.put(key,content)
	return content

def extract_ranked_urls(content):
	soup = BeautifulSoup(content)
	ranks = []
	for li in soup.find_all('li', class_="site-listing"):
		rank = li.div.string
		url = li.h2.string
		domain_parts = tldextract.extract(url)
		if domain_parts[0]=='':
			domain = '.'.join( domain_parts[1:] )
		else:
			domain = '.'.join( domain_parts )
		ranks.append([rank,domain,url])
	return ranks

def scrape_page(url):
	content = fetch_webpage(url)
	return extract_ranked_urls(content)

def scrape_top(category, count):
	logging.info("Scraping top "+str(count)+" from "+category)
	page_count = int(math.ceil(count / URLS_PER_PAGE))
	logging.info("  "+str(page_count)+" pages")
	ranks = []
	for page in range(0, page_count):
		page_url = BASE_URL+";"+str(page)+category
		logging.info("  page "+str(page+1)+" of "+str(page_count)+" ("+page_url+")")
		ranks += scrape_page( page_url )
	return ranks

def write_ranks_csv(name, data):
	with open(name, 'wb') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['rank', 'domain', 'url', 'type', 'country'])
		for row in data:
			writer.writerow(row)

logging.basicConfig(level=logging.DEBUG)
logging.info("Starting scraper:")

news_ranks = scrape_top( NEWS_CATEGORY, 200 )
write_ranks_csv('alexa-news-ranks.csv', news_ranks)

arts_ranks = scrape_top( ARTS_CATEGORY, 100 )
write_ranks_csv('alexa-arts-ranks.csv', arts_ranks)

