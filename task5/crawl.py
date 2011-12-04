import sys, os, re, httplib, urlparse, json
from BeautifulSoup import BeautifulSoup
from StringIO import StringIO
from PIL import Image
import urllib2
import urllib
import pycurl

import gevent, exceptions
from gevent import monkey, Greenlet
from gevent.queue import Queue
import time
import random

shared_q = Queue()
monkey.patch_all()

temp_name = 'img_temp'
default_filter_keywords = [
    'doubleclick', # google ad
    'thumb',        # used for thumbnails 
        ]

context_keywords = [
        'egypt',
        'london',
        'riot',
        'unrest',
        'cairo',
        'tahrir',
        'japan',
        'tsunami',
        'irene',
        'hurricane',
        'flood',
        'water',
]

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8)'
#user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : user_agent }

DEBUG = False
def debug_print(log):
    if DEBUG:
        print log

def keyword_filtered(claim_url):
    for i in default_filter_keywords:
        if i in claim_url:
            return True

    for i in context_keywords:
        if i in claim_url:
            return True

    return False

def crawl_img_list(link):
    original_url = "http://"+link if "http" not in link else link
    try:
        # this doesn't handle redirect
        #req = urllib2.Request(original_url, headers)
        #dst = urllib2.urlopen(req, timeout=5)
        dst = urllib2.urlopen(original_url, timeout=5)
        final_url = dst.geturl()
        raw_html = dst.read() 
        dst.close()
    except:
        return "", ""

    return get_all_img(final_url, raw_html)

def get_all_img(origin, html):
    img_list = []
    try:
        soup = BeautifulSoup(html)
    except UnicodeDecodeError:
        debug_print( "unable to parse URL")
        return ""

    img_tags = soup.findAll('img')
    if img_tags == None:
        debug_print( "no image found")
        return ""
        
    temp_name = str(int(10000000000 * random.random()))
    max_dim_url = ""
    max_dim = (0,0)
    # download imgs and check dimension
    for i in img_tags:
        try:
            esc_url = url_fix(get_absolute(origin, i['src']))

            k = urllib2.urlopen(esc_url).read()
            img_list.append(esc_url)

            f = open(temp_name, 'w')
            while not os.path.isfile(temp_name):
                temp_name = str(int(10000000000 * random.random()))
            f.write(k)
            f.close()
            im = Image.open(temp_name)
            #debug_print( str(im.size))
            if is_wanted(im.size) and keyword_filtered(esc_url):
                if im.size > max_dim:
                    max_dim = im.size
                    max_dim_url = i['src']
        except:
            debug_print("problem accessing the image")
            continue

    if os.path.isfile(temp_name):
        os.remove(temp_name)

    # handle on-site image
    return img_list, max_dim_url


def is_wanted(dim):
    # check ratio for ad
    ratio_thres = 4
    small_thres = (300, 180)

    k = (1/float(ratio_thres)) < dim[0]/float(dim[1]) < ratio_thres and\
    sum(dim) > sum(small_thres) # check if image is too small (often icon)
    return k

# copied from Werkzeug
def url_fix(s, charset='utf-8'):
    """Sometimes you get an URL by a user that just isn't a real
    URL because it contains unsafe characters like ' ' and so on.  This
    function can fix some of the problems in a similar way browsers
    handle data entered by the user:

    :param charset: The target charset for the URL if the url was
                    given as unicode string.
    """
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def get_absolute(origin, path):
    k = re.match(r'(?P<top>(https?://[a-zA-Z0-9.]+))/?\S+', path) 
    if k != None:
        return path
    else:
        return k.group('top')+ path 

def is_rt(tweet):
    rt_keys = [ 'rt ', ' rt', 'retweet']
    for i in rt_keys:
        if i in tweet.lower():
            return True
    return False

def work(tweet_raw):
    # need to be fixed for invalid json data like irene; i hate inconsistent data
    cleaned = tweet_raw.replace('\\','').replace('\'', '\"').replace(' None', ' null')
    try:
        tweet_json = json.loads(cleaned)
        tweet_text = tweet_json['text']
        if not is_rt(tweet_text):
            current = {}
            current['claim_desc'] = tweet_text

            urls = re.findall(r'https?://\S+', tweet_text)
            if len(urls) != 0:
                current['all_imgs'], current['claim_img'] = crawl_img_list(urls[0]) # crawl on first url only
                if not (len(current['all_imgs']) == 0 or current['all_imgs'] == ''):
                    shared_q.put(current)
    except:
        # ignore this tweet
        pass

def fileIO(inputfile):
    outf = open('output_' + inputfile, 'w')

    count = 0
    while True:
        try:
            got = shared_q.get(block=False)
            if got == exceptions.StopIteration:
                print "yosi!"
                break
            got['id'] = count
            count += 1
            outf.write(json.dumps(got)+'\n')
        except gevent.queue.Empty:
            time.sleep(0)

    outf.close()
            
def main():
    inputfile = sys.argv[1]
    inputf = open(inputfile)
    tweets = inputf.readlines()
    inputf.close()

    jobs = [gevent.spawn(work, tweet) for tweet in tweets]

    g = Greenlet(fileIO, inputfile)
    g.start()
    gevent.joinall(jobs)
    shared_q.put(StopIteration)
    g.join()
    print 'join done'
    
if __name__ == '__main__':
    main() 
