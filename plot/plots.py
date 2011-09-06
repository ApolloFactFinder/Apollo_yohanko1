import matplotlib
import matplotlib.pyplot as plt
import json
import re
import httplib
import urlparse
import time
# task
#5. Analysis of social links in Egypt and Japan data sets.
#Result: Construct a network where each source we have tweets from is a node, and each relation in the form X follows Y is a directed link from Y to X. Draw the following curves:


#a) Distribution of Out-degree. X-axis: number of followers a node has (that are also in our set of sources). Y-axis: % of nodes that has that number of followers.
#this has better representation in histogram
#b) Distribution of In-degree. X-axis: number of sources that a node follows (that are in our set of sources). Y-axis: % of nodes that follow that number.
#bins = 100
def plot_follow_histogram(user_data, xlabel, ylabel):
    # save data as flat file in case we wanna plot differently
    f = open("data_"+xlabel+"_"+ylabel+".json", 'w')
    f.writelines(str(user_data).replace("\'", "\""))
    f.close()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(user_data.values(), normed=True)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    fig.savefig("plot_"+xlabel+"_"+ylabel, format='png')
    

#c) Retweet Histogram. X-axis: number of retweets of a single tweet. Y-axis: % of tweets that have this number of retweets each.
# y-axis: out of total tweets?
def plot_c():
    pass

#d) The percentage of tweets that have references to pictures.
#need plot for this? not sure what's "references" refers to?


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

def is_image_link(link):
    u = unshorten_url(link)
    for i in IMG_KEYWORDS:
        if i in u:
            return True
    return False

def main():
    user_api1 = "api.twitter.com"
    user_api2 = "/1/users/show.json?screen_name=%(user)s&include_entities=2"
    api_following = "friends_count"
    api_follower = "followers_count"

    tweet_count = 0
    link_count = 0
    img_link_count = 0

    user_data_a = {}
    user_data_b = {}

    # assume each line contains a single tweet
    f = open("egypt_dataset.txt")

    api_conn = httplib.HTTPConnection(user_api1)
    for line in f:
        tweet_count += 1
        tweet = json.loads(line)

        # getting data for part a and b
        user = tweet["from_user"]
        if user is None:
            print tweet
            break

        if user not in user_data_a:
            api_conn.request("GET", "/" + user_api2 % { "user":user })
            response = api_conn.getresponse()
            if response.status == 200: 
                user_string = response.read()
                user_json = json.loads(user_string)
                user_data_a[str(user)] = user_json[api_follower]
                user_data_b[str(user)] = user_json[api_following]
            elif response.status == 400: #rate limit exceeded
                print "rate limit reached"
                print "response: "+response.read()
                print "sleeping for 1 hours"
                time.sleep(3600)
        else:
            continue
        

        if False: # part d: % of images in tweet -> around 3%
            urls = re.findall(r'https?://\S+', tweet['text'])
            if len(urls) is not 0:
                link_count += 1
                for link in urls:
                    if is_image_link(link):
                        img_link_count += 1
                        break # count only once per tweet
            if tweet_count % 1000 == 0:
                print "total link count: " + str(link_count)
                print "total image link count: " + str(img_link_count)
                print "total tweets: " + str(tweet_count)
                print "percentage: " + str((img_link_count*100) / float(tweet_count))

    f.close()

    plot_follow_histogram(user_data_a, "a_followers", "percentage")
    plot_follow_histogram(user_data_b, "b_followees", "percentage")
    #plot_c()

if __name__ == '__main__':
    main() 
