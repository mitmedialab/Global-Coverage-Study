import logging, ConfigParser, sys, json, time, os
import mediacloud
import mediameter.source
from mediameter.db import GeoStoryDatabase

STORIES_PER_PAGE = 1000

tag_to_iso = {'geonames_661882':'ala','geonames_1149361':'afg','geonames_783754':'alb','geonames_2589581':'dza','geonames_5880801':'asm','geonames_3041565':'and','geonames_3351879':'ago','geonames_3573511':'aia','geonames_6697173':'ata','geonames_3576396':'atg','geonames_3865483':'arg','geonames_174982':'arm','geonames_3577279':'abw','geonames_2077456':'aus','geonames_2782113':'aut','geonames_587116':'aze','geonames_3572887':'bhs','geonames_290291':'bhr','geonames_1210997':'bgd','geonames_3374084':'brb','geonames_630336':'blr','geonames_2802361':'bel','geonames_3582678':'blz','geonames_2395170':'ben','geonames_3573345':'bmu','geonames_1252634':'btn','geonames_3923057':'bol','geonames_7626844':'bes','geonames_3277605':'bih','geonames_933860':'bwa','geonames_3371123':'bvt','geonames_3469034':'bra','geonames_1282588':'iot','geonames_3577718':'vgb','geonames_1820814':'brn','geonames_732800':'bgr','geonames_2361809':'bfa','geonames_433561':'bdi','geonames_1831722':'khm','geonames_2233387':'cmr','geonames_6251999':'can','geonames_3374766':'cpv','geonames_3580718':'cym','geonames_239880':'caf','geonames_2434508':'tcd','geonames_3895114':'chl','geonames_1814991':'chn','geonames_2078138':'cxr','geonames_1547376':'cck','geonames_3686110':'col','geonames_921929':'com','geonames_1899402':'cok','geonames_3624060':'cri','geonames_3202326':'hrv','geonames_3562981':'cub','geonames_7626836':'cuw','geonames_146669':'cyp','geonames_3077311':'cze','geonames_203312':'cod','geonames_2623032':'dnk','geonames_223816':'dji','geonames_3575830':'dma','geonames_3508796':'dom','geonames_1966436':'tls','geonames_3658394':'ecu','geonames_357994':'egy','geonames_3585968':'slv','geonames_2309096':'gnq','geonames_338010':'eri','geonames_453733':'est','geonames_337996':'eth','geonames_3474414':'flk','geonames_2622320':'fro','geonames_2205218':'fji','geonames_660013':'fin','geonames_3017382':'fra','geonames_3381670':'guf','geonames_4030656':'pyf','geonames_1546748':'atf','geonames_2400553':'gab','geonames_2413451':'gmb','geonames_614540':'geo','geonames_2921044':'deu','geonames_2300660':'gha','geonames_2411586':'gib','geonames_390903':'grc','geonames_3425505':'grl','geonames_3580239':'grd','geonames_3579143':'glp','geonames_4043988':'gum','geonames_3595528':'gtm','geonames_3042362':'ggy','geonames_2420477':'gin','geonames_2372248':'gnb','geonames_3378535':'guy','geonames_3723988':'hti','geonames_1547314':'hmd','geonames_3608932':'hnd','geonames_1819730':'hkg','geonames_719819':'hun','geonames_2629691':'isl','geonames_1269750':'ind','geonames_1643084':'idn','geonames_130758':'irn','geonames_99237':'irq','geonames_2963597':'irl','geonames_3042225':'imn','geonames_294640':'isr','geonames_3175395':'ita','geonames_2287781':'civ','geonames_3489940':'jam','geonames_1861060':'jpn','geonames_3042142':'jey','geonames_248816':'jor','geonames_1522867':'kaz','geonames_192950':'ken','geonames_4030945':'kir','geonames_831053':'xkx','geonames_285570':'kwt','geonames_1527747':'kgz','geonames_1655842':'lao','geonames_458258':'lva','geonames_272103':'lbn','geonames_932692':'lso','geonames_2275384':'lbr','geonames_2215636':'lby','geonames_3042058':'lie','geonames_597427':'ltu','geonames_2960313':'lux','geonames_1821275':'mac','geonames_718075':'mkd','geonames_1062947':'mdg','geonames_927384':'mwi','geonames_1733045':'mys','geonames_1282028':'mdv','geonames_2453866':'mli','geonames_2562770':'mlt','geonames_2080185':'mhl','geonames_3570311':'mtq','geonames_2378080':'mrt','geonames_934292':'mus','geonames_1024031':'myt','geonames_3996063':'mex','geonames_2081918':'fsm','geonames_617790':'mda','geonames_2993457':'mco','geonames_2029969':'mng','geonames_3194884':'mne','geonames_3578097':'msr','geonames_2542007':'mar','geonames_1036973':'moz','geonames_1327865':'mmr','geonames_3355338':'nam','geonames_2110425':'nru','geonames_1282988':'npl','geonames_2750405':'nld','geonames_2139685':'ncl','geonames_2186224':'nzl','geonames_3617476':'nic','geonames_2440476':'ner','geonames_2328926':'nga','geonames_4036232':'niu','geonames_2155115':'nfk','geonames_1873107':'prk','geonames_4041468':'mnp','geonames_3144096':'nor','geonames_286963':'omn','geonames_1168579':'pak','geonames_1559582':'plw','geonames_6254930':'pse','geonames_3703430':'pan','geonames_2088628':'png','geonames_3437598':'pry','geonames_3932488':'per','geonames_1694008':'phl','geonames_4030699':'pcn','geonames_798544':'pol','geonames_2264397':'prt','geonames_4566966':'pri','geonames_289688':'qat','geonames_935317':'reu','geonames_2260494':'cog','geonames_798549':'rou','geonames_2017370':'rus','geonames_49518':'rwa','geonames_2410758':'stp','geonames_3578476':'blm','geonames_3370751':'shn','geonames_3575174':'kna','geonames_3576468':'lca','geonames_3578421':'maf','geonames_3424932':'spm','geonames_3577815':'vct','geonames_4034894':'wsm','geonames_3168068':'smr','geonames_102358':'sau','geonames_2245662':'sen','geonames_6290252':'srb','geonames_241170':'syc','geonames_2403846':'sle','geonames_1880251':'sgp','geonames_7609695':'sxm','geonames_3057568':'svk','geonames_3190538':'svn','geonames_2103350':'slb','geonames_51537':'som','geonames_953987':'zaf','geonames_3474415':'sgs','geonames_1835841':'kor','geonames_7909807':'ssd','geonames_2510769':'esp','geonames_1227603':'lka','geonames_366755':'sdn','geonames_3382998':'sur','geonames_607072':'sjm','geonames_934841':'swz','geonames_2661886':'swe','geonames_2658434':'che','geonames_163843':'syr','geonames_1668284':'twn','geonames_1220409':'tjk','geonames_149590':'tza','geonames_1605651':'tha','geonames_2363686':'tgo','geonames_4031074':'tkl','geonames_4032283':'ton','geonames_3573591':'tto','geonames_2464461':'tun','geonames_298795':'tur','geonames_1218197':'tkm','geonames_3576916':'tca','geonames_2110297':'tuv','geonames_5854968':'umi','geonames_4796775':'vir','geonames_226074':'uga','geonames_690791':'ukr','geonames_290557':'are','geonames_2635167':'gbr','geonames_6252001':'usa','geonames_3439705':'ury','geonames_1512440':'uzb','geonames_2134431':'vut','geonames_3164670':'vat','geonames_3625428':'ven','geonames_1562822':'vnm','geonames_4034749':'wlf','geonames_2461445':'esh','geonames_69543':'yem','geonames_895949':'zmb','geonames_878675':'zwe'}
allowed_tags = tag_to_iso.keys()

sources = set()
countries = set()
counts_by_pair = {}

logging.basicConfig(filename='fetcher.log',level=logging.DEBUG)
log = logging.getLogger('fetcher')
log.info("======================================================================")

# load shared config file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
config = ConfigParser.ConfigParser()
config.read(parent_dir+'/mc-client.config')

# connect to everything
collection = mediameter.source.MediaSourceCollection(config.get('api','key'))
collection.loadAllMediaIds()
mc = collection.mediacloud
db = GeoStoryDatabase(config.get('db','name'))

log.info('Loaded '+str(collection.count())+' media sources to pull')

# walk through all the sources, grabbing all the stories from each
for source_count, source in enumerate(collection.mediaSources()):
    log.info("---------------------------------------------------------------------------")
    log.info('  Starting with %s (%s): %s %d of %d' % (
        source['url']
        , source['media_id']
        , source['category']
        , source_count
        , len(collection.mediaSources())
    ))
    source_url = source['url']
    sources.add(source_url)
    
    last_processed_stories_id = db.maxStoryProcessedId(source['media_id'])  # pick up where the db left off last run

    query_str = '*'
    extra_args = {'category':source['category'], 'media_source_url':source['url']}
    filter_str = config.get('query','dates')+' AND +media_id:'+str(source['media_id'])

    # page through the stories, saving them in the DB
    more_stories = True
    while more_stories:
        log.info('    loading stories from '+str(last_processed_stories_id))
        try:
            stories = mc.storyList(query_str, filter_str, last_processed_stories_id, STORIES_PER_PAGE, ap_stories_id=1)
            if len(stories)>0:
                for idx, story in enumerate(stories):
                    try:
                        ap_stories_id = int(story.get('ap_stories_id', 0))
                    except (TypeError, KeyError):
                        ap_stories_id = 0
                    if ap_stories_id != 0:
                        continue
                    try:
                        tag_count = 0
                        story_tags = []
                        for tag in story["story_tags"]:
                            try:
                                geo_tag = tag["tag"]
                                if geo_tag in allowed_tags:
                                    country = tag_to_iso[geo_tag]
                                    countries.add(country)
                                    story_tags.append(country)
                                    tag_count += 1
                            except KeyError:
                                pass
                        for country in story_tags:
                            pair = (source_url, country)
                            counts_by_pair[pair] = counts_by_pair.get(pair, 0) + 1.0/len(story_tags);
                    except KeyError:
                        pass
                last_processed_stories_id = stories[len(stories)-1]['processed_stories_id']
                more_stories = True
            else:
                more_stories = False
        except Exception as e:
            # probably a 404, so sleep and then just try again
            log.info('  '+str(e))
            time.sleep(1)
    log.info('  Done with '+source['url']+' ('+source['media_id']+'): '+source['category'])

with open('output/stories-by-source-and-country.csv', 'wb') as f:
    countries = sorted(list(countries))
    urls = sorted(list(sources))
    log.info('Found urls:')
    for url in urls:
        log.info("    %s" % url)
    log.info('Found countries:')
    for c in countries:
        log.info("    %s" % c)
        f.write(",%s" % (c,))
    f.write("\n")
    for url in urls:
        url = url.split(',')[0].strip()
        f.write(url)
        for c in countries:
            pair = (url, c)
            count = counts_by_pair.get(pair, 0)
            f.write(",%f" % count)
        f.write("\n")
