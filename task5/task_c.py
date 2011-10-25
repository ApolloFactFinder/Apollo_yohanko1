
# c) Retweet Histogram. 
#X-axis: number of retweets of a single tweet. 
#Y-axis: % of tweets that have this number of retweets each.

import sys, re, json
rt_map = {}

charcut = 25

def build_rt_map(tweet):
    """
        if original tweet alreay in rt_map: increment
        it's not: ""

        if original retweet cannot be located: create entry in the rt_map
    """
    if "RT" in tweet: # this is a cheap...but the most popular way to rt
        m = re.search(r"^(RT @\w+:? )+(?P<text>.+)", tweet)

        if m == None:
            print "RT text not found:" + tweet
            return
        tweet = m.group('text')
        tweet_id = get_id(tweet)
        if rt_map.get(tweet_id):
            rt_map[tweet_id] += 1
        else:
            rt_map[tweet_id] = 1
    else: # not RT
        rt_map[tweet[:charcut]] = 1

def get_id(text):
    if len(text) < charcut:
        identifier = text
    else:
        identifier = text[:charcut]



# assume tweet is in chronological order
f = open("../egypt_dataset.txt")
for line in f:
    tweet = json.loads(line)
    build_rt_map(tweet['text'])
f.close()
