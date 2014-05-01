import logging
import requests

class Cliff():
    '''
    Make requests to a cliff server
    '''

    PATH_TO_CLIFF = "/CLIFF/parse/text"

    JSON_PATH_TO_ABOUT_COUNTRIES = 'results.places.about.countries';

    STATUS_OK = "ok"

    def __init__(self,host,port):
        self._log = logging.getLogger('cliff')
        self._url = host+":"+str(port)+Cliff.PATH_TO_CLIFF
        self._log.info("Conneced to CLIFF at "+self._url)

    def query(self,text):
        payload = {'q':text}
        try:
            r = requests.post(self._url, data=payload)
            self._log.debug('CLIFF says '+r.content)
            return r.json()
        except requests.exceptions.RequestException as e:
            self._log.error("RequestException " + str(e))
        return ""
