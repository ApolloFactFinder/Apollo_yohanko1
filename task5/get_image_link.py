import sys, os, re, httplib, urlparse, json
from BeautifulSoup import BeautifulSoup
from StringIO import StringIO
from PIL import Image
import urllib2
import pycurl

temp_name = 'img_temp'


IMG_KEYWORDS = [
"twitpic", "imgur", "postimage", "picasaweb",
"flickr", "imagehostinga", "photobucket",
"yfrog", "zooomr", 
"image", "img",  "photo", "pic"
]# not used

# copied from Werkzeug
import urllib
import urlparse

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

def is_wanted(dim):
    # check ratio for ad
    ratio_thres = 4
    small_thres = (300, 180)

    k = (1/float(ratio_thres)) < dim[0]/float(dim[1]) < ratio_thres and\
    sum(dim) > sum(small_thres) # check if image is too small (often icon)
    return k

def filter_img_on_url(url, dk, fk):
    """ 
        True: if dk is in url
        False: if fk is in url or dk is not in url
    """
    url = url.lower()
    for k in fk: # usually ad url like doubleclick.net here
        if k.lower() in url:
            return False
    for k in dk: # dataset from our keywords
        if k.lower() in url:
            return True
    return False

def get_absolute(origin, path):
    k = re.match(r'(?P<top>(https?://[a-zA-Z0-9.]+))/?\S+', path) 
    if k != None:
        return path
    else:
        return k.group('top')+ path 
    

def get_biggest_img(origin, html, dk, fk):
    try:
        soup = BeautifulSoup(html)
    except UnicodeDecodeError:
        print "unable to parse URL"
        return ""
    img_tags = soup.findAll('img')

    if img_tags == None:
        print "no image found"
        return ""
        
    max_dim_url = ""
    max_dim = (0,0)
    # download imgs and check dimension
    for i in img_tags:
        try:
            esc_url = url_fix(get_absolute(origin, i['src']))
            if not is_relevant(esc_url, dk, fk):
                continue
            k = urllib2.urlopen(esc_url).read()
        except: #urllib2.HTTPError, ignore 4xx errors
            print esc_url
            print "problem reading the image"
            continue

        try:
            f = open(temp_name, 'w')
            f.write(k)
            f.close()
            im = Image.open(temp_name)
            #print im.size
            if is_wanted(im.size):
                if im.size > max_dim:
                    max_dim = im.size
                    max_dim_url = i['src']
        except:
            print "problem opening the image"
            continue

    if os.path.isfile(temp_name):
        os.remove(temp_name)

    # handle on-site image
    return max_dim_url
        

def inspect_link_urllib2(link, dk, fk):
    original_url = "http://"+link if "http" not in link else link
    try:
        dst = urllib2.urlopen(original_url, timeout=5)
        final_url = dst.geturl()
        raw_html = dst.read() 
        dst.close()
    except:
        print "url invalid: " + repr(link)
        return link, ""

    biggest_image_link = get_biggest_img(final_url, raw_html, dk, fk)
    
    return final_url, biggest_image_link
     

def get_image_link(tweet, data_keywords=[], filter_keywords=[]):
    """
        tweet: json format
        data_keywords: include image if url contains these keywords
        filter_keywords: excludes image if url contains these keywords

        returns None , if link is broken
                (<final_url>, <url_to_biggest_img>), <url_to_biggest_img> is '' if image is not found
    """
    urls = re.findall(r'https?://\S+', tweet['text'])
    if len(urls) != 0:
        for link in urls:
            img_link = inspect_link_urllib2(link, data_keywords, filter_keywords)
            print img_link
            return img_link
    
#if __name__ == '__main__':
#   print inspect_link_urllib2("http://www.photozz.com/?1ixz")
#    print inspect_link_urllib2("http://www.guardian.co.uk/commentisfree/2011/aug/18/riots-sentencing-courts?utm_source=twitterfeed&utm_medium=twitter&utm_campaign=Feed%3A+theguardian%2Fmedia%2Frss+%28Media%29")
#    #f = open("../egypt_dataset.txt")
#    f = open("../london_riots.txt")
#    tweets = f.readlines()
#    f.close()
#    for tweet in tweets:
#        try:
#            print get_image_link(json.loads(tweet.replace("\'","\"").replace("None", "\"\"")))
#        except:
#            print "oh man"
