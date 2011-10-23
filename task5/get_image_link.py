import re, httplib, urlparse
import json

IMG_KEYWORDS = [
"twitpic", "imgur", "postimage", "picasaweb",
"flickr", "imagehostinga", "photobucket",
"yfrog", "zooomr", 
"image", "img",  "photo", "pic"
]

link_cache = {}

import urllib2
from BeautifulSoup import BeautifulSoup
# don't bother to use api for each...inspected manually for each html 
def get_image_hotlink(url):
    url = "http://"+url if "http" not in url else url
    try:
        dst = urllib2.urlopen(url, timeout=5)
    except Exception:
        return url

    raw_html = dst.read() 
    dst.close()
    soup = BeautifulSoup(raw_html)

    image_url = url # just return pure url for other hostings... 
    print "url::"  + image_url
    if "twitpic" in url:
        img_tag = soup.find('img', attrs = { 'id':re.compile("photo-display"), 'class' : re.compile("photo") })
    elif "yfrog" in url:
        img_tag = soup.find('img', attrs = { 'id':re.compile("main_image") })
    elif "img.ly" in url:
        img_tag = soup.find('img', attrs = { 'id':re.compile("the-image") })
    elif "flickr" in url:
        img_tag = soup.find('img', attrs = { 'alt':re.compile("photo") })
    else:
        return image_url

    if img_tag != None:
        image_url = img_tag['src']
    else:
        return "" # image not found case

    return "http:" + image_url if "http:" not in image_url else image_url

def unshorten_url(url):
    try:
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc, timeout=5) # modify this value at your convinience
        h.request('HEAD', parsed.path)
        response = h.getresponse()
        if response.status == 300 and response.getheader('Location'):
            return unshorten_url(response.getheader('Location')) # changed to process chains of short urls
        else:
            return url
    except Exception:
        return ""

def inspect_link(link):
    cached = link_cache.get(link)
    if cached != None:
        return cached

    u = unshorten_url(link)
    for i in IMG_KEYWORDS:
        if i in u:
            hotlink = get_image_hotlink(u)
            link_cache[link] = hotlink
            print hotlink
            return hotlink
    return ""

def get_image_link(tweet):
    """
        get tweet in json format
        returns "" , if url does not contain image or link is broken
                link to the image, if tweet contains active image link
                    if the image is hosted on "popular" hosting, it returns the hotlink of the image.
                    else returns the url of hosting site containing the image.

        if multiple image links are avaiable in a tweet, only first one is returned
    """
    urls = re.findall(r'https?://\S+', tweet['text'])
    if len(urls) != 0:
        for link in urls:
            img_link = inspect_link(link)
            if img_link != "":
                print img_link
                return img_link
    return ""
    
#if __name__ == '__main__':
#    f = open("../egypt_dataset.txt")
#    tweets = f.readlines()
#    f.close()
#    for tweet in tweets:
#        get_image_link(json.loads(tweet))
