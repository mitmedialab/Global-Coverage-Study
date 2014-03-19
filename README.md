Geographic Coverage Study
=========================

A study of global online media coverage.  The goal is to identify top American online media outlets 
(via Alexa ranking), use the MediaCloud dataset and tools to geoparse and locate stories, and then compare
global coverage between them.

Process
-------

1. Ran `scraper/scrape-alexa.py` to pull the top arts and news rankings from the Alexa website. (Jan 21, 2014)
2. Three of us handcoded the `scraper/data/alexa-NNNN-ranks-raw.csv` following the `doc/AlexaSourceCodingGuidelines.pdf` document.
3. We ran `scraper/compute-intercoder-reliability.py` to compute inter-coder reliability.
4. We resolved (small number of) disagreements manually to produce the `scraper/data/alexa-NNNN-ranks-golden.csv` files.
5. We added in the Alexa "Global Rank" metric by running `scraper/scrape-alexa-details.py`.
6. We ran `scraper/make-top-results.py` to produce "Top N" lists for each source type we care about. (Feb 17, 2014)
7. We hand-edited any entries in the "Top N" lists that didn't make sense - sportsillustrated was the only one (Feb 17, 2014)
8. We removed any non-english sources - eenadu.net on the newspaper list was the only one (Feb 28, 2014)
9. We added a MediaCloud source_id to the "Top N" lists, and adding in any missing sites to MediaCloud via their admin UI.
10. We used a tiny web app (in `media-source-dashboard/`) to make sure stories were being collected by MediaCloud correctly.
