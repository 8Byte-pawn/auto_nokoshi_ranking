#!/usr/bin/env python
# -*- coding:utf-8 -*-

from requests_oauthlib import OAuth1Session
from datetime import datetime, date, timedelta
import json

### Constants
oath_key_dict = {
    "consumer_key": "xxxxxx",
    "consumer_secret": "xxxxxx",
    "access_token": "xxxxxx",
    "access_token_secret": "xxxxxx"
}

### Functions
def main():
    tweets = tweet_search("#のこし OR しかのこのこのここしたんたん", oath_key_dict)
    count = 1
    print "---------------------------------"
    for tweet in reversed(tweets["statuses"]):
        tweet_id = tweet[u'id_str']
        tweet_date = tweet_id2time(int(tweet_id)).strftime("%H:%M")
        #if tweet_date != "00:00":
        #    continue

        text = tweet[u'text']
        created_at = tweet[u'created_at']
        user_id = tweet[u'user'][u'id_str']
        user_description = tweet[u'user'][u'description']
        screen_name = tweet[u'user'][u'screen_name']
        user_name = tweet[u'user'][u'name']
        msec_date = tweet_id2time(int(tweet_id)).strftime("%Y-%m-%d %H:%M:%S.%f")
        print "No." + str(count)
        print "screen_name:", screen_name
        print "user_name:", user_name
        print "created_at:", msec_date
        print "tweet_id:", tweet_id
        print "text:\n", text
        print "---------------------------------"
        count = count + 1
    return

def create_oath_session(oath_key_dict):
    oath = OAuth1Session(
        oath_key_dict["consumer_key"],
        oath_key_dict["consumer_secret"],
        oath_key_dict["access_token"],
        oath_key_dict["access_token_secret"]
    )
    return oath

def tweet_search(search_word, oath_key_dict):
    url = "https://api.twitter.com/1.1/search/tweets.json?"
    params = {
        "q": search_word, 
        "lang": "ja",
        #"until": datetime.strftime(datetime.today() + timedelta(days=1), '%Y-%m-%d'),
        "result_type": "recent",
        "count": "100"
    }
    oath = create_oath_session(oath_key_dict)
    responce = oath.get(url, params = params)
    if responce.status_code != 200:
        print "Error code: %d" %(responce.status_code)
        return None
    tweets = json.loads(responce.text)
    return tweets

def tweet_id2time(id):
    return datetime.fromtimestamp((float(id >> 22) + 1288834974657)/1000.0)
    

# Execute
if __name__ == "__main__":
    main()
