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
import multiprocessing
import Queue
import sys

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
    u = s_unshorten_url(link)
    for i in IMG_KEYWORDS:
        if i in u:
            return u + "\r\n"
    return ""

def queue_image_links(chunk_range):
    # assume each line contains a single tweet
    for index in xrange(chunk_range[0], chunk_rage[1]):
        tweet = json.loads(tweets[index-1])
        urls = re.findall(r'https?://\S+', tweet['text'])
        if len(urls) is not 0:
            for link in urls:
                img_link = get_image_link(link)
                if img_link == "":
                    break
                else:
                   links_queue.put((index, img_link))

def proc_init(shared_queue, shared_tweets):
    global links_queue
    global tweets
    links_queue = shared_queue
    tweets = shared_tweets


# flow: spawn threads for IO, which put their results into a queue 
# after all thread is done, sort queue and write into a file
def main():
    if len(sys.argv) is not 3:
        print "usage: python task_d.py <data_filepath> <# of procs>"
        print "suggest # of procs == 100"
        sys.exit(0)

    datafile = sys.argv[1] 

    dataf = open(datafile)
    tweets = dataf.readlines() # yeah! throw whole thing in the memory for multiprocessing
    dataf.close()

    #total_tweets = len(k)
    total_tweets = 1000
    links_queue = Queue.PriorityQueue() # queue of (index, unshortened url string)

    num_procs = int(sys.argv[2])
    jobsize = int(total_tweets / num_procs) # NOTE: ignore negligible remainder for now... 

    # could use manager...but no priority queue support
    #manager = multiprocessing.Manager()
    #shared_q = manager.

    starts, ends = [], []
    for i in range(1, total_tweets+1, jobsize):
        starts.append(i)
        if i+jobsize > total_tweets:
            ends.append(total_tweets)
        else:
            ends.append(i+jobsize)

    pl = multiprocessing.Pool(num_procs, initializer = proc_init, initargs = (links_queue, tweets))
    pl.map_async(queue_image_links, zip(starts, ends))
    pl.close()
    pl.join()

    output = open("image_links.txt", "w")
    while not links_queue.empty():
        output.writelines(str(links_queue.get())[1:-1])
    output.close()

if __name__ == '__main__':
    main() 
