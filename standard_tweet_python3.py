#!/usr/bin/env python
# -*- coding:utf-8 -*-

# Twitter用のimport
from requests_oauthlib import OAuth1Session
from datetime import datetime, date, timedelta
import json
import twitter

# DB接続用
import os
import psycopg2

# sleep
from time import sleep

### Constants
oath_key_dict = {
    "consumer_key": os.environ["CONSUMER_KEY"],
    "consumer_secret": os.environ["CONSUMER_SECRET"],
    "access_token": os.environ["ACCESS_TOKEN_KEY"],
    "access_token_secret": os.environ["ACCESS_TOKEN_SECRET"]
}

dsn = os.environ["DATABASE_URL"]

### Functions
def main():
    # 初期化
    count = 1	
    
    now_hour = datetime.now().strftime('%H')
    if  2 <= int(now_hour) <= 23:
        print("It is not recording time.")
        exit(1)

    sleep(30)

    # DBへ接続
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute('BEGIN')
   
    # 当日すでにDB内に3つレコードがある場合、処理を中断
    check_date = datetime.strftime(datetime.today(), '%Y/%m/%d')
    cur.execute("select count(screen_name) from nokoshi where updated_date=%s", (check_date,))
    rows = cur.fetchall()
    if rows[0][0] >= 3:
        print("3 records is existed.")
        cur.execute('COMMIT')
        cur.close() 
        conn.close() 
        exit(1)

    search_word = "#のこし OR しかのこのこのここしたんたん since:"\
                  + datetime.strftime(datetime.today() - timedelta(days=1), '%Y-%m-%d')\
                  + "_23:55:00_JST"
    tweets = tweet_search(search_word, oath_key_dict)

    message = "自動測定結果（" + datetime.strftime(datetime.today(), '%m/%d') + "）"

    for tweet in reversed(tweets["statuses"]):
        tweet_id = tweet[u'id_str']
        text = tweet[u'text']
        
        check1 = tweet_id2time(int(tweet_id)).strftime("%d")
        check2 = tweet_id2time(int(tweet_id)).strftime("%H")
        
        # スクリプト実行日かつ0時投稿のツイート以外対象外
        if check1 != datetime.strftime(datetime.today(), '%d') or check2 != "00":
            continue
       
        # リツイートは対象外
        if text.startswith("RT @"):
            print("Retweet.")
            continue

        # 三回繰り返しているか確認
        if text.count('しかのこのこのここしたんたん') < 3:
            print("This tweet do not have nokoshi word more than 3times.\n")
            continue

        created_at = tweet[u'created_at']
        user_id = tweet[u'user'][u'id_str']
        #user_description = tweet[u'user'][u'description']
        screen_name = tweet[u'user'][u'screen_name']
        user_name = tweet[u'user'][u'name']
        image_url = tweet[u'user'][u'profile_image_url_https']
        msec_date = tweet_id2time(int(tweet_id)).strftime("%m/%d %H:%M:%S.%f")
        msec_date = msec_date[:-3]
       
        if count < 4:
            date = tweet_id2time(int(tweet_id)).strftime("%Y%m%d")
            time = tweet_id2time(int(tweet_id)).strftime("%H:%M:%S.%f")
            
            cur.execute("select * from nokoshi where screen_name=%s and updated_date=%s", (screen_name, date,))
            rows = cur.fetchall()

            if rows == []:
                # 投稿日初のツイートのとき、データベースにデータを追加
                cur.execute("insert into nokoshi (screen_name, updated_date, record, point) values(%s, %s, %s, %s)", (screen_name, date, time, str(4 - count)))
                # ユーザ名管理データベースの更新（登録なしなら新規登録、あれば更新）
                cur.execute("select * from user_data where screen_name=%s", (screen_name,))
                rows = cur.fetchall()
                if rows == []:
                    cur.execute("insert into user_data (screen_name, user_name, image_url) values(%s, %s, %s)", (screen_name, user_name, image_url, ))
                else:
                    cur.execute("update user_data set user_name=%s,image_url=%s where screen_name=%s", (user_name, image_url, screen_name, ))
            else:
                # 二回目以降のツイートはランキング対象外として処理
                # if文でfalse判定となった場合、そのツイートはデータベース登録済み（ランクイン）ツイートとなる
                cur.execute("select * from nokoshi where screen_name=%s and updated_date=%s and record=%s", (screen_name, date, time,))
                rows = cur.fetchall()
                # rowsが空になった場合、すでに登録されているものとは異なるが、ランキング対象＝二つ目以降のツイートと判定できる
                if rows == []:
                    continue
            
            # ランキング対象の情報をツイート文に記載
            message += "\n\n" + str(count) + "位"
            message += "\n" + user_name
            message += "\n" + msec_date
        
        # DB登録処理完了後、必ずcountがアップ
        count = count + 1
        
    # ランキングの結果が3位まで選出されているか、50～59分の間になれば結果をツイート
    now_min = datetime.now().strftime('%M')
    message += "\nby nokoshi-ranking.herokuapp.com"
    if count > 3 or 50 <= int(now_min) <= 59:
        print(message)
        auth = twitter.OAuth(
            consumer_key=oath_key_dict["consumer_key"],
            consumer_secret=oath_key_dict["consumer_secret"],
            token=oath_key_dict["access_token"],
            token_secret=oath_key_dict["access_token_secret"]
        )
        t_post = twitter.Twitter(auth=auth)
        t_post.statuses.update(status=message)
   
    print(message)
    cur.execute('COMMIT')
    cur.close() 
    conn.close() 
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
