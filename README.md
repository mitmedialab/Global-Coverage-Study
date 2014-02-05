Geographic Coverage Study
=========================

A study of global online media coverage.  The goal is to identify top American online media outlets 
(via Alexa ranking), use the MediaCloud dataset and tools to geoparse and locate stories, and then compare
global coverage between them.

Process
-------

1. First we ran `scrape-alexa.py` to pull the top arts and news rankings from the Alexa website. (Jan 21, 2014)
2. Then three of us handcoded the `data/alexa-NNNN-ranks-raw.csv` following the `doc/AlexaSourceCodingGuidelines.pdf` document.
3. Then we ran `compute-intercoder-reliability.py` to compute inter-coder reliability.
4. Then we resolved (small number of) disagreements manually to produce the `data/alexa-NNNN-ranks-golden.csv` files.
5. Then we added in the Alexa "Global Rank" metric by running `scrape-alexa-details.py`.
6. Then we ran `make-top-results.py` to produce "Top N" lists for each source type we care about. (Feb 5, 2014)
