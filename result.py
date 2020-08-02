#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Twitter用のimport
from requests_oauthlib import OAuth1Session
from datetime import datetime, date, timedelta
import json
import twitter

# DB接続用
import psycopg2

### Constants
oath_key_dict = {
    "consumer_key": "xxxxx",
    "consumer_secret": "xxxxxx",
    "access_token": "xxxxxx",
    "access_token_secret": "xxxxxx"
}

dsn = "postgres://sample.com"

### Functions
def main():
    tweets = tweet_search("#のこし OR しかのこのこのここしたんたん", oath_key_dict)
    count = 1
    flag = 0

    #message = "Twitter APIによる自動ツイートテスト" + "（" + datetime.strftime(datetime.today(), '%m/%d') + "）"
    message = "自動測定機能確認（" + datetime.strftime(datetime.today(), '%m/%d') + "）"

    # DBへ接続
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute('BEGIN')
   
    print("---------------------------------")
    for tweet in reversed(tweets["statuses"]):
        tweet_id = tweet[u'id_str']
        text = tweet[u'text']
        
        check1 = tweet_id2time(int(tweet_id)).strftime("%d")
        check2 = tweet_id2time(int(tweet_id)).strftime("%H")
        
        if check1 == datetime.strftime(datetime.today(), '%d') and check2 == "00":
            flag = 1

        if flag == 0:
            continue
       
        # Exclusion about retweet
        if text.startswith("RT @"):
            continue

        created_at = tweet[u'created_at']
        user_id = tweet[u'user'][u'id_str']
        user_description = tweet[u'user'][u'description']
        screen_name = tweet[u'user'][u'screen_name']
        user_name = tweet[u'user'][u'name']
        msec_date = tweet_id2time(int(tweet_id)).strftime("%m/%d %H:%M:%S.%f")
        print("No." + str(count))
        print("screen_name:" + screen_name)
        print("user_name:" + user_name)
        print("created_at:" + msec_date)
        print("tweet_id:" + tweet_id)
        print("text:\n" + text)
        print("---------------------------------")
        
        if count < 4:
            #message += "\n\n" + str(count) + "位"
            #message += "\nuser_name : " + user_name
            message += "\ntweet_time: " + msec_date
           
            cur.execute("select * from nokoshi where screen_name=%s", (screen_name,))
            rows = cur.fetchall()
            if rows == []:
                print("New entry!")
                cur.execute("insert into nokoshi values(%s, %s, %s, %s)", (screen_name, user_name, str(4 - count), "00:00:00"))
            else:
                print("The entry is updated!")
                
         
        count = count + 1
    
    auth = twitter.OAuth(
        consumer_key=oath_key_dict["consumer_key"],
        consumer_secret=oath_key_dict["consumer_secret"],
        token=oath_key_dict["access_token"],
        token_secret=oath_key_dict["access_token_secret"]
    )
    #t_post = twitter.Twitter(auth=auth)
    #t_post.statuses.update(status=message)
    #print(message)
    cur.execute('COMMIT')
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
        "result_type": "recent",
        "count": "100"
    }
    oath = create_oath_session(oath_key_dict)
    responce = oath.get(url, params = params)
    if responce.status_code != 200:
        print("Error code: " + responce.status_code)
        return None
    tweets = json.loads(responce.text)
    return tweets

def tweet_id2time(id):
    return datetime.fromtimestamp((float(id >> 22) + 1288834974657)/1000.0)
    

# Execute
if __name__ == "__main__":
    main()
