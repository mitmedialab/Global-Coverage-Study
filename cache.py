import hashlib, os, codecs

'''
Super simple file-based cache.  Helpful if you're developing a webpage scraper
and want to be a bit more polite while developing.
'''

DEFAULT_DIR = "cache"

dir = DEFAULT_DIR

def md5_key(string):
    m = hashlib.md5()
    m.update(string)
    return m.hexdigest()

def set_dir(dir = DEFAULT_DIR):
    if not os.path.exists(dir):
        os.makedirs(dir)

def contains(key):
    return os.path.isfile(os.path.join(dir,key))

def get(key):
    if os.path.isfile(os.path.join(dir,key)):
        with open(os.path.join(dir,key), "r") as myfile:
            return myfile.read()
    return None

def put(key,content):
    text_file = codecs.open(os.path.join(dir,key), encoding='utf-8', mode="w")
    text_file.write(content)
    text_file.close()
