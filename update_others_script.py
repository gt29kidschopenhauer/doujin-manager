import helper.Constants as Constants
from np import np_api
import sqlite3
import requests
import json
from string import capwords

conn = sqlite3.connect("doujins.db")
cur = conn.cursor()

max_tags = {}

def resolve(tag):
	url = "https://nhentai.net/api/galleries/search?query=tags:" + tag
	rq = requests.get(url)
	jrq = json.loads(rq.text)
	if "num_pages" not in jrq:
		print("UNRESOLVED. TAG:", tag.upper())
		return
	lastPage = jrq["num_pages"]
	for i in range(1, lastPage + 1):
		page = requests.get(url + '&page=' + str(i))
		jrq = json.loads(page.text)
		if "result" not in jrq:
			print("RESOLVING ERROR. TAG:", tag + '. PAGE:', get_page(page.url))
			continue
		for doujin in jrq["result"]:
			doujin_id = int(doujin["id"])
			if doujin_id <= max_tags[tag]:
				print("FINISHED RESOLVING FOR TAG:", tag)
				return
			characters = is_blue_archive(doujin)
			if type(characters) is type([]):
				for character in characters:
					cur.execute('INSERT INTO others_doujin (doujin_id, full_name, others_tag) VALUES(?, ?, ?)', (doujin_id, capwords(character), tag))
	conn.commit()

def is_blue_archive(doujin):
	certify = False
	characters = []
	for tag in doujin['tags']:
		if tag['type'] == 'parody':
			if tag['name'] == 'blue archive':
				certify = True
			else:
				return False
		elif tag['type'] == 'character':
			characters.append(tag['name'])
	if certify:
		return characters

def get_page(nhentaiURL):
	page = 0
	place = 0
	for i in range(-1, -len(nhentaiURL) - 1, -1):
		if nhentaiURL[i].isdigit():
			page += int(nhentaiURL[i]) * 10 ** place
			place += 1
		else:
			return page

for tag in Constants.others_tag:
	cur.execute("SELECT MAX(doujin_id) FROM others_doujin WHERE others_tag = ?", (tag,))
	m = cur.fetchone();
	if m[0] is None:
		max_tags[tag] = 0
	else:
		max_tags[tag] = m[0]

cur.execute("SELECT full_name FROM students")
names = cur.fetchall()
full_names = {'Sensei'}
for name in names:
	full_names.add(name[0])

for tag in max_tags:
	url = "https://nhentai.net/api/galleries/search?query=parodies:blue archive tags:" + tag
	rq = requests.get(url)
	result = rq.text
	jresult = json.loads(result)
	if "num_pages" not in jresult:
		print("JSON ERROR. TAG:", tag.upper())
		resolve(tag)
		continue
	lastPage = jresult["num_pages"]
	for i in range(1, lastPage + 1):
		page_URL = url + '&page=' + str(i)
		rq = requests.get(page_URL)
		result = rq.text
		jresult = json.loads(result)
		if "result" not in jresult:
			print("JSON ERROR. TAG:", tag.upper() + '.', "PAGE:", i)
			continue
		doujins = jresult["result"]
		end = False
		for doujin in doujins:
			compilation = False
			doujin["id"] = int(doujin["id"])
			if doujin["id"] <= max_tags[tag]:
				end = True
				break
			doujin_id = doujin['id']
			characters = []
			for t in doujin['tags']:
				if t["type"] == "character":
					if capwords(t["name"]) not in full_names:
						compilation = True
						break
					elif capwords(t["name"]) == "Sensei":
						continue
					characters.append(capwords(t["name"]))
			if compilation:
				continue
			if len(characters) == 0:
				cur.execute("INSERT INTO others_doujin (doujin_id, others_tag) VALUES(?, ?)", (doujin_id, tag))
			else:
				for character in characters:
					cur.execute("INSERT INTO others_doujin (doujin_id, full_name, others_tag) VALUES(?, ?, ?)", (doujin_id, character, tag))
		if end:
			break
	print("UPDATE SUCCESSFULL. TAG:", tag)
	conn.commit()
