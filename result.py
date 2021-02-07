# -*- coding: utf-8 -*-

import os
from bottle import route, run, static_file
from datetime import datetime, date, timedelta
import psycopg2

dsn = os.environ["DATABASE_URL"]


@route("/css/<filename:path>")
def send_css(filename):
    return static_file(filename, root=f"css")



@route("/total")
def total_result():
	# 初期化
	source = "<html>\n<head>\n<title>のこしランキング(全期間)</title>\n<link rel=\"stylesheet\" href=\"/css/hp_style.css\">\n</head>\n<body>\n"
	
	today_date = datetime.strftime(datetime.today(), '%Y-%m-%d')
	# DBへ接続
	conn = psycopg2.connect(dsn)
	cur = conn.cursor()
	
	with open("./shika.txt") as f:
		shika = f.read()

	with open("./tiger.txt") as f:
		tiger = f.read()

	count = 1
	cur.execute("select nokoshi.updated_date, user_data.user_name, nokoshi.record, user_data.image_url from nokoshi inner join user_data on nokoshi.screen_name = user_data.screen_name where updated_date=%s order by updated_date desc, record asc limit 3;", (today_date,))
	rows = cur.fetchall()

	source += "<h1><img src=\"data:image/png;base64," + shika + "\" width=\"60\" height=\"60\"></img>"
	source += "のこしツイートランキング（全期間）\n"
	source += "<img src=\"data:image/png;base64," + tiger + "\" width=\"60\" height=\"60\"></img></h1>\n"

	source += "<p>「しかのこのこのここしたんたん」を3回唱えたツイートの測定結果を表示するサイトです。<br>"
	source += "最新の結果は<a href=\"https://nokoshi-ranking.herokuapp.com/\">TOPページ</a>から確認できます。</p>"
	source += "<p>現在『しかのこのこのここしたんたん 2巻』予約受付中！！"
	source += "<a href=\"https://www.amazon.co.jp/dp/406522330X\">こちら</a>から予約できます。</p>"

	count = 1
	source += "<h2>のこし最速ツイートランキング</h2>\n"
	source += "<p>のこしランキングにランクインした記録が対象。各ランカーの最速値で比較。5位まで表示</p>\n"
	source += "<table border=\"1\">\n"
	source += "<tr><th>順位</th><th colspan=\"2\">Twitter表示名</th><th>記録時刻</th></tr>\n"
	cur.execute("SELECT OriginalList.screen_name, OriginalList.user_name, OriginalList.image_url, RecordList.MinRecord FROM user_data AS OriginalList INNER JOIN (SELECT screen_name, MIN(record) AS MinRecord FROM nokoshi GROUP BY screen_name) AS RecordList ON OriginalList.screen_name = RecordList.screen_name order by RecordList.MinRecord limit 5;")
	rows = cur.fetchall()
	for row in rows: 
		source += "<tr><td>"
		source += str(count) + "位"
		source += "</td><td>"

		if str(row[2]) != "None":
			source += "<img border=\"0\" src=\"" + str(row[2]) + "\" width=\"48\" height=\"48\"></img></td><td>" + row[1]
		else:
			source += "</td><td>" + row[1]
		source += "</td><td>"
		source += str(row[3])
		source += "</td></tr>\n"
		count += 1
	source += "</table>\n"
	
	count = 1
	source += "<h2>のこし総合得点ランキング</h2>\n"
	source += "<p>毎日のランキング結果より、1位=3ポイント、2位=2ポイント、3位=1ポイントを付与</p>\n"
	source += "<table border=\"1\">\n"
	source += "<tr><th>順位</th><th colspan=\"2\">Twitter表示名</th><th>総合得点</th><th>ランクイン回数</th></tr>\n"
	cur.execute("SELECT distinct OriginalList.screen_name, OriginalList.user_name, PointList.TotalPoint, PointList.RecordCount, PointList.EntryDate, OriginalList.image_url FROM user_data AS OriginalList INNER JOIN (SELECT screen_name, SUM(point) AS TotalPoint, COUNT(screen_name) AS RecordCount, MIN(updated_date) AS EntryDate FROM nokoshi GROUP BY screen_name) AS PointList ON OriginalList.screen_name = PointList.screen_name order by PointList.TotalPoint desc, PointList.EntryDate asc;")
	rows = cur.fetchall()
	for row in rows: 
		source += "<tr><td>"
		source += str(count) + "位"
		source += "</td><td>"
		
		if str(row[5]) != "None":
			source += "<img border=\"0\" src=\"" + str(row[5]) + "\" width=\"48\" height=\"48\"></img></td><td>" + row[1]
		else:
			source += "</td><td>" + row[1]
		source += "</td><td>"
		source += str(row[2])
		source += "</td><td>"
		source += str(row[3])
		source += "</td></tr>\n"
		count += 1
	source += "</table>\n"

	source += "</body></html>"
	cur.close() 
	conn.close() 
	return source



@route("/")
def hello_world():
	# 初期化
	source = "<html>\n<head>\n<title>のこしランキング</title>\n<link rel=\"stylesheet\" href=\"/css/hp_style.css\">\n</head>\n<body>\n"
	
	today_date = datetime.strftime(datetime.today(), '%Y-%m-%d')
	# DBへ接続
	conn = psycopg2.connect(dsn)
	cur = conn.cursor()
	
	with open("./shika.txt") as f:
		shika = f.read()

	with open("./tiger.txt") as f:
		tiger = f.read()

	count = 1
	cur.execute("select nokoshi.updated_date, user_data.user_name, nokoshi.record, user_data.image_url from nokoshi inner join user_data on nokoshi.screen_name = user_data.screen_name where updated_date=%s order by updated_date desc, record asc limit 3;", (today_date,))
	rows = cur.fetchall()

	source += "<h1><img src=\"data:image/png;base64," + shika + "\" width=\"60\" height=\"60\"></img>"
	source += "のこしツイートランキング\n"
	source += "<img src=\"data:image/png;base64," + tiger + "\" width=\"60\" height=\"60\"></img></h1>\n"

	source += "<p>「しかのこのこのここしたんたん」を3回唱えたツイートの測定結果を表示するサイトです。<br>"
	source += "結果に誤り等があれば、該当ツイートを記載の上、当日測定結果ツイートのリプライまたは「@8Byte_pawn」へツイートをお願いします。<br>"
	source += "なお、このページでは2021/2/7以降の記録が反映されてます。<br>"
	source += "全期間の最速ツイート記録・総合得点記録は<a href=\"https://nokoshi-ranking.herokuapp.com/total\">こちら</a>で確認できます。</p>"
	
	source += "<p>現在『しかのこのこのここしたんたん 2巻』予約受付中！！"
	source += "<a href=\"https://www.amazon.co.jp/dp/406522330X\">こちら</a>から予約できます。</p>"


	source += "<h2>のこしツイートランキング（" + today_date + "分）</h2>\n"
	source += "<p>毎日0:00.00～0:59.59で早く投稿された上位3ツイートが対象。最終結果は遅くとも1:00.00に確定。<br>"
	source += "複数該当ツイートがある場合は、0時に近いツイートを対象に判定。</p>\n"

	source += "<table border=\"1\">\n"
	source += "<tr><th>順位</th><th colspan=\"2\">Twitter表示名</th><th>記録時刻</th><th>日付</th></tr>\n"
	for row in rows: 
		source += "<tr><td>"
		source += str(count) + "位"
		source += "</td><td>"
		if str(row[3]) != "None":
			source += "<img border=\"0\" src=\"" + str(row[3]) + "\" width=\"48\" height=\"48\"></img></td><td>" + row[1]
		else:
			source += "</td><td>" + row[1]
		source += "</td><td>"
		source += str(row[2])
		source += "</td><td>"
		source += str(row[0])
		source += "</td></tr>\n"
		count += 1
	source += "</table>\n"
	
	count = 1
	source += "<h2>のこし最速ツイートランキング</h2>\n"
	source += "<p>のこしランキングにランクインした記録が対象。各ランカーの最速値で比較。5位まで表示</p>\n"
	source += "<table border=\"1\">\n"
	source += "<tr><th>順位</th><th colspan=\"2\">Twitter表示名</th><th>記録時刻</th></tr>\n"
	cur.execute("SELECT OriginalList.screen_name, OriginalList.user_name, OriginalList.image_url, RecordList.MinRecord FROM user_data AS OriginalList INNER JOIN (SELECT screen_name, MIN(record) AS MinRecord FROM (SELECT * from nokoshi where updated_date >= '2021-02-07') AS LATEST GROUP BY screen_name) AS RecordList ON OriginalList.screen_name = RecordList.screen_name order by RecordList.MinRecord limit 5;")
	rows = cur.fetchall()
	for row in rows: 
		source += "<tr><td>"
		source += str(count) + "位"
		source += "</td><td>"

		if str(row[2]) != "None":
			source += "<img border=\"0\" src=\"" + str(row[2]) + "\" width=\"48\" height=\"48\"></img></td><td>" + row[1]
		else:
			source += "</td><td>" + row[1]
		source += "</td><td>"
		source += str(row[3])
		source += "</td></tr>\n"
		count += 1
	source += "</table>\n"
	
	count = 1
	source += "<h2>のこし総合得点ランキング</h2>\n"
	source += "<p>毎日のランキング結果より、1位=3ポイント、2位=2ポイント、3位=1ポイントを付与</p>\n"
	source += "<table border=\"1\">\n"
	source += "<tr><th>順位</th><th colspan=\"2\">Twitter表示名</th><th>総合得点</th><th>ランクイン回数</th></tr>\n"
	cur.execute("SELECT distinct OriginalList.screen_name, OriginalList.user_name, PointList.TotalPoint, PointList.RecordCount, PointList.EntryDate, OriginalList.image_url FROM user_data AS OriginalList INNER JOIN (SELECT screen_name, SUM(point) AS TotalPoint, COUNT(screen_name) AS RecordCount, MIN(updated_date) AS EntryDate FROM (SELECT * from nokoshi where updated_date >= '2021-02-07') AS LATEST GROUP BY screen_name) AS PointList ON OriginalList.screen_name = PointList.screen_name order by PointList.TotalPoint desc, PointList.EntryDate asc;")
	rows = cur.fetchall()
	for row in rows: 
		source += "<tr><td>"
		source += str(count) + "位"
		source += "</td><td>"
		
		if str(row[5]) != "None":
			source += "<img border=\"0\" src=\"" + str(row[5]) + "\" width=\"48\" height=\"48\"></img></td><td>" + row[1]
		else:
			source += "</td><td>" + row[1]
		source += "</td><td>"
		source += str(row[2])
		source += "</td><td>"
		source += str(row[3])
		source += "</td></tr>\n"
		count += 1
	source += "</table>\n"

	source += "</body></html>"
	cur.close() 
	conn.close() 
	return source

run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
