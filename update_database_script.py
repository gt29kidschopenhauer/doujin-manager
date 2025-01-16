import helper.Constants as Constants
from np import np_api
import sqlite3
import requests
import json
from string import capwords

conn = sqlite3.connect("doujins.db")
cur = conn.cursor()

cur.execute('SELECT MAX(id) FROM doujin')
max_id = cur.fetchone()[0]
if max_id is None:
	max_id = 0

req = requests.get("https://nhentai.net/api/galleries/search?query=parody:blue archive")
jreq = json.loads(req.text)
num_pages = jreq["num_pages"]
done = False

for i in range(1, num_pages + 1):
	req = requests.get("https://nhentai.net/api/galleries/search?query=parody:blue archive&page=" + str(i))
	jreq = json.loads(req.text)
	for doujin in jreq["result"]:
		doujin['id'] = int(doujin['id'])
		if doujin['id'] <= max_id:
			done = True
			break
		others = False
		emuach = False
		artist = []
		group = []
		character = []
		date = doujin["upload_date"]
		for tag in doujin["tags"]:
			if tag["type"] == "language" and tag["name"] != "translated":
				language = tag["name"]
			elif tag["type"] == "tag":
				if not others:
					if tag["name"] in Constants.others_tag:
						others = True
					elif tag["name"] == "yuri":
						emuach = True
			else:
				name = tag["name"].split('|')
				for n in name:
					if tag["type"] == "artist":
						artist.append(n.strip())
					elif tag["type"] == "group":
						group.append(n.strip())
					elif tag["type"] == "character" and n != 'sensei':
						character.append(capwords(n.strip()))
		if others:
			doujin_type = "others"
		elif emuach:
			doujin_type = "emuach"
		else:
			doujin_type = "cunny"
		cur.execute("INSERT INTO doujin (id, type, upload_date, language) VALUES(?, ?, ?, ?)", (doujin['id'], doujin_type, date, language))
		for a in artist:
			cur.execute("INSERT INTO author (name, doujin_id) VALUES(?, ?)", (a, doujin['id']))
		for g in group:
			cur.execute("INSERT INTO [group] (name, doujin_id) VALUES(?, ?)", (g, doujin['id']))
		for c in character:
			cur.execute("INSERT INTO student (full_name, doujin_id) VALUES(?, ?)", (c, doujin['id']))
		conn.commit()
	if done:
		break