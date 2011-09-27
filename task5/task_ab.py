# Run: python task_ab.py <data_source> <user sample rate>
# data_source expected to be in twitter json format

import sys
import random
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

    fig.savefig("plot_"+xlabel+"_"+ylabel+".png", format='png')
    
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

def main():
    if len(sys.argv) is not 3:
        print "usage: python task_ab.py <data_filepath> <user sample rate>"
        sys.exit(0)

    filepath = sys.argv[1]
    sample_rate = float(sys.argv[2])

    if not (0.0 < sample_rate <= 1.0):
        print "sample rate:" + sample_rate
        print "please input sample rate between 0 and 1"
        sys.exit(0)

    user_api1 = "api.twitter.com"
    user_api2 = "/1/users/show.json?screen_name=%(user)s&include_entities=2"
    api_following = "friends_count"
    api_follower = "followers_count"

    users = set()
    user_data_a, user_data_b = {}, {}

    # assume each line contains a single tweet
    #f = open("egypt_dataset.txt")
    f = open(filepath)
    for line in f:
        tweet = json.loads(line)
        user = tweet["from_user"]
        users.add(user)
    f.close()

    print "total users: " + str(len(users))
    print "sampling " + str(int(len(users) * sample_rate)) + "users"

    sample_users = random.sample(users, len(users))
    countdown = int(sample_rate * len(users))

    api_conn = httplib.HTTPConnection(user_api1)
    for user in sample_users:
        if countdown == 0:
            break

        if user not in user_data_a:
            api_conn.request("GET", "/" + user_api2 % { "user":user })
            response = api_conn.getresponse()

            if response.status == 200: 
                user_string = response.read()
                user_json = json.loads(user_string)
                user_data_a[str(user)] = user_json[api_follower]
                user_data_b[str(user)] = user_json[api_following]
                countdown -= 1
            elif response.status == 400: #rate limit exceeded
                print "rate limit reached"
                print "response: "+response.read()
                print "retrying in 10 minutes"
                time.sleep(60 * 10)

    plot_follow_histogram(user_data_a, "a_followers", "percentage")
    plot_follow_histogram(user_data_b, "b_followees", "percentage")

if __name__ == '__main__':
    main() 
