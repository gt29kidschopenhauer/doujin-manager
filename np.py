import grequests
import helper.Constants as Constants
import helper.helper as helper
import requests
import json
import helper.objects as objects
from random import randint, choice
import sqlite3
from string import capwords

class np_api:
    def __init__(self):
        pass

    def yieldTag(self, sort=False):
        generator = helper.getList(Constants.Affiliation.TAG, sort)
        for x in generator:
            yield x

    def yieldGroup(self, sort=False):
        generator = helper.getList(Constants.Affiliation.GROUP, sort)
        for x in generator:
            yield x

    def yieldArtist(self, sort=False):
        generator = helper.getList(Constants.Affiliation.ARTIST, sort)
        for x in generator:
            yield x

    def yieldCharacter(self, sort=False):
        generator = helper.getList(Constants.Affiliation.CHARACTER, sort)
        for x in generator:
            yield x

    def yieldParodie(self, sort=False):
        generator = helper.getList(Constants.Affiliation.PARODIE, sort)
        for x in generator:
            yield x

    def pickRandom(self):
        random = requests.head(Constants.RANDOM_URL, allow_redirects=True)
        return helper.createMedium(random.url.split("/")[-2])

    def info(self, code):
        jreq = json.loads(requests.get(Constants.API_CALL_ID + str(code)).text)
        authors = []
        characters = []
        parodies = []
        for tag in jreq["tags"]:
            if tag["type"] == "artist":
                authors.append(capwords(tag["name"]))
            elif tag["type"] == "character":
                characters.append(capwords(tag["name"]))
            elif tag["type"] == "language":
                if tag["name"] == "english":
                    language = "English"
                elif tag["name"] == "japanese":
                    language = "Japanese"
                elif tag["name"] == "chinese":
                    language = "Chinese"
            elif tag["type"] == "parody":
                parodies.append(capwords(tag["name"]))
        in4 = {
            "language": language,
            "authors": authors,
            "characters": characters,
            "parodies": parodies
        }
        return in4

    def search(self, title=None, characters=[], parodies=[], artist=[], groups=[], tags=[],
               sort=False):

        sorting = "date"
        query = Constants.QUERY_URL
        if title is not None:
            query += title + " "
        if characters:
            query += "character:" + " ".join(characters) + " "
        if parodies:
            query += "parodies:" + " ".join(parodies) + " "
        if artist:
            query += "artist:" + " ".join(artist) + " "
        if groups:
            query += "group:" + " ".join(groups) + " "
        if tags:
            query += "tags:" + " ".join(tags) + " "
        if sort:
            sorting = "popular"
        query = query[0:-1]

        queryPages = query + "&page=" + "1" + "&sort=" + sorting
        result = requests.get(queryPages).text
        jresult = json.loads(result)
        lastPage = int(jresult["num_pages"])
        urls = [(query + "&page=" + str(i) + "&sort=" + sorting)
                for i in range(2, lastPage + 1)]
        if not jresult["result"]:
            return
        for element in jresult["result"]:
            yield objects.Medium(element)
        rs = (grequests.get(u) for u in urls)
        generator = grequests.imap(rs, stream=True)
        for page in generator:
            result = page.text
            jresult = json.loads(result)
            if not jresult["result"]:
                return
            for element in jresult["result"]:
                yield objects.Medium(element)

    def searchRandomBADoujin(self, name, doujin_type):
        query = Constants.QUERY_URL + "parodies:blue archive"
        if name:
            query += " character:" + name
        if name != "sora":
            if doujin_type == Constants.DoujinType.CUNNY:
                result = requests.get(query).text
                while result[0] == "<":
                    result = requests.get(query).text
                jresult = json.loads(result)
                if "error" in jresult:
                    return -1
                num_pages = jresult["num_pages"]
                if num_pages == 0:
                    return 0
                elif num_pages == 1:
                    code = []
                    for doujin in jresult["result"]:
                        cunny = True
                        compilation = False
                        for tag in doujin["tags"]:
                            if tag["type"] == "tag" and (tag["name"] in Constants.others_tag or tag["name"] == "yuri"):
                                cunny = False
                                break
                            elif tag["type"] == "parody" and tag["name"] != "blue archive":
                                compilation = True
                                break
                        if cunny and not compilation:
                            code.append(doujin["id"])
                    if len(code) == 0:
                        return 0
                    return choice(code)
                cunny = False
                compilation = True
                count = 0
                while not cunny or compilation:
                    cunny = True
                    compilation = False
                    page = randint(1, num_pages)
                    result = requests.get(query + "&page=" + str(page)).text
                    while result[0] == "<":
                        result = requests.get(query + "&page=" + str(page)).text
                    jresult = json.loads(result)
                    if "error" in jresult:
                        if count >= 5:
                            return -1
                        count += 1
                        continue
                    doujin_num = randint(0, len(jresult["result"]) - 1)
                    for tag in jresult["result"][doujin_num]["tags"]:
                        if tag['type'] == 'tag' and (tag['name'] in Constants.others_tag or tag['name'] == 'yuri'):
                            cunny = False
                            break
                        elif tag["type"] == "parody" and tag["name"] != "blue archive":
                            compilation = True
                            break
                    code = jresult['result'][doujin_num]['id']
                return code
            elif doujin_type == Constants.DoujinType.EMUACH:
                query += ' tags:yuri'
                result = requests.get(query).text
                while result[0] == "<":
                    result = requests.get(query).text
                jresult = json.loads(result)
                if "error" in jresult:
                    return -1
                num_pages = jresult["num_pages"]
                emuach_doujins = []
                greqs = (grequests.get(query + "&page=" + str(i)) for i in range(1, num_pages + 1))
                generator = grequests.imap(greqs, stream=True)
                for page in generator:
                    try:
                        jresult = json.loads(page.text)
                    except:
                        return -1
                    if "error" in jresult:
                        continue
                    for doujin in jresult["result"]:
                        others = False
                        compilation = False
                        for tag in doujin["tags"]:
                            if tag['type'] == 'tag' and tag['name'] in Constants.others_tag:
                                others = True
                                break
                            elif tag["type"] == "parody" and tag["name"] != "blue archive":
                                compilation = True
                                break
                        if not others and not compilation:
                            emuach_doujins.append(doujin["id"])
                if len(emuach_doujins) == 0:
                    return 0
                return choice(emuach_doujins)
            else:
                codes = set()
                for tag in Constants.others_tag:
                    new_query = query + ' tags:' + tag
                    req = requests.get(new_query)
                    while req.text[0] == "<":
                        req = requests.get(new_query)
                    jresult = json.loads(req.text)
                    if "error" in jresult:
                        codes.add(-1)
                        continue
                    elif jresult["num_pages"] == 0:
                        codes.add(0)
                        continue
                    greqs = (grequests.get(new_query + "&page=" + str(i)) for i in range(1, jresult["num_pages"] + 1))
                    generator = grequests.imap(greqs, stream=True)
                    for page in generator:
                        try:
                            j = json.loads(page.text)
                        except:
                            return -1
                        if "error" in j:
                            continue
                        for doujin in j["result"]:
                            compilation = False
                            for tag in doujin["tags"]:
                                if tag["type"] == "parody" and tag["name"] != "blue archive":
                                    compilation = True
                                    break
                            if not compilation:
                                codes.add(doujin["id"])
                if -1 in codes:
                    if len(codes) == 1:
                        return -1
                    else:
                        codes.remove(-1)
                if 0 in codes:
                    if len(codes) == 1:
                        return 0
                    else:
                        codes.remove(0)
                return choice(list(codes))
        else:
            con = sqlite3.connect('doujins.db')
            cur = con.cursor()
            if doujin_type == Constants.DoujinType.CUNNY:
                codes = cur.execute('SELECT doujin_id FROM sora WHERE doujin_type = "cunny"').fetchall()
            elif doujin_type == Constants.DoujinType.EMUACH:
                codes = cur.execute('SELECT doujin_id FROM sora WHERE doujin_type = "emuach"').fetchall()
            else:
                codes = cur.execute('SELECT doujin_id FROM sora WHERE doujin_type = "others"').fetchall()
            if len(codes) == 0:
                return 0
            return choice(codes)[0]

    def searchExplicitWithID(self, code):
        return helper.createMedium(str(code))
