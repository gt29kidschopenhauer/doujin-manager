import grequests
import json
from . import Constants
from . import objects
from bs4 import BeautifulSoup
import requests

def createMedium(id):
    result = json.loads(requests.get(Constants.API_CALL_ID + id).text)
    if "id" not in result:
        return -1
    return objects.Medium(result)

def getList(affiliation, sort=False):
    strategie = None
    if affiliation == Constants.Affiliation.TAG:
        strategie = TagStrategie(sort)
    elif affiliation == Constants.Affiliation.ARTIST:
        strategie = ArtistStrategie(sort)
    elif affiliation == Constants.Affiliation.CHARACTER:
        strategie = CharacterStrategie(sort)
    elif affiliation == Constants.Affiliation.PARODIE:
        strategie = ParodieStrategie(sort)
    elif affiliation == Constants.Affiliation.GROUP:
        strategie = GroupStrategie(sort)
    else:
        raise TypeError
    generator = strategie.getList()
    for entry in generator:
        text = entry.text.rsplit(' ', 1)
        yield {Constants.NAME: text[0], Constants.COUNT: text[1][1:-1],
               Constants.ID: entry[Constants.CLASS][1][4:]}


class AbstractStrategie:
    def __init__(self, sort):
        self._sort = sort

    def getList(self):
        site = self.getFirstSite()
        results, lastPage = self.parsingSite(site, first=True)
        urls = self.createUrls(lastPage)
        for x in results:
            yield x
        rs = (grequests.get(u) for u in urls)
        generator = grequests.imap(rs, stream=True)
        for entry in generator:
            for x in self.parsingSite(entry):
                yield x

    def parsingSite(self, site, first=False):
        if first:
            soup = BeautifulSoup(site.text, Constants.LXML)
            results = soup.select(Constants.SELECT_TAG)
            lastPage = int(soup.select(Constants.SELECT_LAST_PAGE)[
                           0][Constants.HREF][6:])
            return (results, lastPage)
        else:
            soup = BeautifulSoup(site.text, Constants.LXML)
            results = soup.select(Constants.SELECT_TAG)
            return results


class TagStrategie(AbstractStrategie):
    def __init__(self, sort):
        super().__init__(sort)

    def getFirstSite(self):
        if self._sort:
            return requests.get(Constants.TAGS_URL_SORTED + str(1))
        else:
            return requests.get(Constants.TAGS_URL + str(1))

    def createUrls(self, lastPage):
        if self._sort:
            return [(Constants.TAGS_URL_SORTED + str(i)) for i in range(2, lastPage + 1)]
        else:
            return [(Constants.TAGS_URL + str(i)) for i in range(2, lastPage + 1)]


class ArtistStrategie(AbstractStrategie):
    def __init__(self, sort):
        super().__init__(sort)

    def getFirstSite(self):
        if self._sort:
            return requests.get(Constants.ARTISTS_URL_SORTED + str(1))
        else:
            return requests.get(Constants.ARTISTS_URL + str(1))

    def createUrls(self, lastPage):
        if self._sort:
            return [(Constants.ARTISTS_URL_SORTED + str(i)) for i in range(2, lastPage + 1)]
        else:
            return [(Constants.ARTISTS_URL + str(i)) for i in range(2, lastPage + 1)]


class CharacterStrategie(AbstractStrategie):
    """
    Strategie for getting characters
    """
    def __init__(self, sort):
        super().__init__(sort)

    def getFirstSite(self):
        if self._sort:
            return requests.get(Constants.CHARACTERS_URL_SORTED + str(1))
        else:
            return requests.get(Constants.CHARACTERS_URL + str(1))

    def createUrls(self, lastPage):
        if self._sort:
            return [(Constants.CHARACTERS_URL_SORTED + str(i)) for i in range(2, lastPage + 1)]
        else:
            return [(Constants.CHARACTERS_URL + str(i)) for i in range(2, lastPage + 1)]


class ParodieStrategie(AbstractStrategie):
    def __init__(self, sort):
        super().__init__(sort)

    def getFirstSite(self):
        if self._sort:
            return requests.get(Constants.PARODIES_URL_SORTED + str(1))
        else:
            return requests.get(Constants.PARODIES_URL + str(1))

    def createUrls(self, lastPage):
        if self._sort:
            return [(Constants.PARODIES_URL_SORTED + str(i)) for i in range(2, lastPage + 1)]
        else:
            return [(Constants.PARODIES_URL + str(i)) for i in range(2, lastPage + 1)]


class GroupStrategie(AbstractStrategie):
    def __init__(self, sort):
        super().__init__(sort)

    def getFirstSite(self):
        if self._sort:
            return requests.get(Constants.GROUPS_URL_SORTED + str(1))
        else:
            return requests.get(Constants.GROUPS_URL + str(1))

    def createUrls(self, lastPage):
        if self._sort:
            return [(Constants.GROUPS_URL_SORTED + str(i)) for i in range(2, lastPage + 1)]
        else:
            return [(Constants.GROUPS_URL + str(i)) for i in range(2, lastPage + 1)]
