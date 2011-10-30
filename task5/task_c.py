
# c) Retweet Histogram. 
#X-axis: number of retweets of a single tweet. 
#Y-axis: % of tweets that have this number of retweets each.

import sys, re, json
rt_map = {}

charcut = 25
RT_text = r"(?P<head>.*)(RT @.+:? )+(?P<tail>.*)"

def build_rt_map(tweet):
    """
        if original tweet alreay in rt_map: increment
        it's not: ""

        if original retweet cannot be located: create entry in the rt_map
    """
    if "RT" in tweet: # this is a cheap...but the most popular way to rt
        m = re.search(RT_text, tweet)

        if m == None:
            #print "RT text not found:" + tweet
            return 1
        tweet = m.group('head') + m.group('tail')
        tweet_id = get_id(tweet)
        #print "tw:" + tweet
        #print "id:" + tweet_id
        if rt_map.get(tweet_id):
            rt_map[tweet_id] += 1
            #print "score! " + str(rt_map[tweet_id])
        else:
            rt_map[tweet_id] = 1
    else: # not RT
        rt_map[tweet[:charcut]] = 1

    return 0

def get_id(text):
    return text if len(text) < charcut else text[:charcut]


i, j = 0, 0
# assume tweet is in chronological order
f = open("../egypt_dataset.txt")
for line in f:
    tweet = json.loads(line)
    j += build_rt_map(tweet['text'])
    i += 1
f.close()

f = open("retweet_data.json", 'w')
f.write(str(rt_map))
f.close()
print "not counted: " + str(float(j)/i) + "(" + str(j) + ")"
