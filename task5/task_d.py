# parallel version of getting image links
# task
#5. Analysis of social links in Egypt and Japan data sets.
#Result: Construct a network where each source we have tweets from is a node, and each relation in the form X follows Y is a directed link from Y to X. Draw the following curves:

#d) The percentage of tweets that have references to pictures.
#need plot for this? not sure what's "references" refers to?

import matplotlib
import matplotlib.pyplot as plt
import json
import re
import httplib
import urlparse
import time
from multiprocessing import Pool
import linecache
def unshorten_url(url):
    try:
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc, timeout=5)
        h.request('HEAD', parsed.path)
        response = h.getresponse()
        if response.status/100 == 3 and response.getheader('Location'):
            return unshorten_url(response.getheader('Location')) # changed to process chains of short urls
        else:
            return url
    except Exception:
        return ""

import urllib2
def s_unshorten_url(url):
    try:
        dst = urllib2.urlopen(url, timeout=10)
    except Exception:
        return ""
    return dst.url

# sample tweet
#{"text": "RT @Salon: Egypt's final web provider goes dark http://salon.com/a/sWCYfAA", 
#"profile_image_url": "http://a0.twimg.com/profile_images/540646668/salon_icon_93x93_normal.png", 
#"to_user_id_str": null, 
#"from_user": "Salon", 
#"from_user_id": 1407317, 
#"to_user_id": null, 
#"geo": null, 
#"id": 32282967938170880, 
#"iso_language_code": "en", 
#"from_user_id_str": "1407317", 
#"source": "&lt;a href=&quot;http://twitter.com/&quot;&gt;web&lt;/a&gt;", 
#"id_str": "32282967938170880", 
#"created_at": "Tue, 01 Feb 2011 03:43:54 +0000", 
#"metadata": {"result_type": "recent"}}
IMG_KEYWORDS = [
"twitpic", "imgur", "postimage", "picasaweb",
"flickr", "imagehostinga", "photobucket",
"yfrog", "zooomr", 
"image", "img",  "photo", "pic"
]

def get_image_link(link):
    u = unshorten_url(link)
    for i in IMG_KEYWORDS:
        if i in u:
            return u + "\r\n"
    return ""

def build_image_link_list(start, end):
    # assume each line contains a single tweet
    img_links = []
    for index in xrange(start, end):
        line = linecache.getline("egypt_dataset.txt", index) # NOTE: load whole file into memory
        tweet = json.loads(line)

        urls = re.findall(r'https?://\S+', tweet['text'])
        if len(urls) is not 0:
            for link in urls:
                img_link = get_image_link(link)
                if img_link == "":
                    break
                else:
                   img_links.append((str(index), img_link))
    return img_links 

def count_tweets(filepath);
    pass

def main():
    total_tweets = 1873613 # hard coded for egypt dataset for now...
    tweet_count = 0

    num_procs = 1000
    jobsize = int(total_tweets / num_procs) # NOTE: ignore negligible remainder for now... 
    
    p = Pool(num_procs)
    chunks = [(i,i+jobsize) for i in range(0, total_tweets+1, jobsize)]
    image_list = [p.apply_async(build_image_link_list, c) for c in chunks]

    output = open("image_links.txt", "w")
    output.writelines(img_links)
    output.close()

if __name__ == '__main__':
    main() 
