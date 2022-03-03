from bs4 import BeautifulSoup, element
from requests import get
from urllib.parse import quote
import re

def getWordsFromUrl(url : str):
    """
        Function that returns a dictionary containing the words from any valid url from https://www.urbandictionary.com/ domain
    """
    def getStringFromDiv(div, markdown : bool = False):
        """
            Utility function to extract a string from a div, the string can be formatted using markdown,
            this function is highly dependend from https://www.urbandictionary.com/ html formatting
        """
        string = ""
        for html_elem in (elem for elem in div.contents):
            if markdown:
                replace_func = lambda match: match.groupdict().get('url') or ('\\' + match.groupdict()['markdown'])
                escape_markdown_regex = r'(?P<markdown>[_\\~|\*`]|%s)' % r'^>(?:>>)?\s|\[.+\]\(.+\)'
                text = re.sub(escape_markdown_regex, replace_func, html_elem.text, 0, re.MULTILINE)
            else:
                text = html_elem.text

            if isinstance(html_elem, element.Tag) and html_elem.name == 'br':
                string += "\n"
            elif isinstance(html_elem, element.Tag) and html_elem.name == "a" and markdown:
                string += "["+text+"](https://www.urbandictionary.com"+html_elem.attrs["href"]+")"
            else:
                string += text
        return string

    #fetch all of the html divs containing the words definitions
    divs = BeautifulSoup(get(url).content, "html.parser").findAll("div", class_='definition')

    #for each div extract the informations about the word and put it in the dictionary
    words = {}
    for contents in (div.contents[0].contents for div in divs):
        words[len(words)] = { "url": "https://www.urbandictionary.com"+contents[0].contents[0].contents[0].attrs["href"],
                              "name": getStringFromDiv(contents[0]),
                              "name_markdown": getStringFromDiv(contents[0], markdown=True),
                              "meaning": getStringFromDiv(contents[1]),
                              "meaning_markdown": getStringFromDiv(contents[1], markdown=True),
                              "example": getStringFromDiv(contents[2]),
                              "example_markdown": getStringFromDiv(contents[2], markdown=True),
                              "contributor": getStringFromDiv(contents[3]),
                              "contributor_markdown": getStringFromDiv(contents[3], markdown=True) }
    return words


class UrbanDictionary():
    """a class to handle a bidirectional search query on https://www.urbandictionary.com/"""

    def __init__(self, query : str = None, random : bool = False, enableCaching : bool = True):
        self.query = quote(query.strip()) if query and query.strip() else None
        self.random = random if not self.query else False

        self.wordIndex = 0
        self.pageIndex = 1
        self.words = getWordsFromUrl(self.url)

        self.cachingEnabled = enableCaching
        self.pages = {self.pageIndex: self.words} if self.cachingEnabled else {}

    @property
    def url(self):
        string = "https://www.urbandictionary.com/"
        if self.query:
            string += f"define.php?term={self.query}&"
        elif self.random:
            string += f"random.php?"
        else:
            string += "?"
        string += f"page={self.pageIndex}"
        return string

    @property
    def currentWord(self):
        return self.words.get(self.wordIndex)

    @property
    def hasPreviousPage(self):
        return self.random or self.pageIndex > 1

    @property
    def hasNextPage(self):
        self.pageIndex += 1
        words = self.pages.get(self.pageIndex) or getWordsFromUrl(self.url)
        if self.cachingEnabled: self.pages[self.pageIndex] = words
        self.pageIndex -= 1
        return self.random or len(words) > 0

    @property
    def hasPreviousWord(self):
        return self.wordIndex > 0 or self.hasPreviousPage

    @property
    def hasNextWord(self):
        return self.wordIndex < len(self.words)-1 or self.hasNextPage

    def goToPreviousPage(self):
        if not self.hasPreviousPage:
            raise StopIteration("There isn't a Page prior to the current one")

        self.wordIndex = 0
        self.pageIndex -= 1
        self.words = self.pages.get(self.pageIndex) or getWordsFromUrl(self.url)
        return self.words

    def goToPreviousWord(self):
        if not self.hasPreviousWord:
            raise StopIteration("There isn't a Word prior to the current one")

        if self.wordIndex > 0:
            self.wordIndex -= 1
        else:
            self.goToPreviousPage()
            self.wordIndex = len(self.words)-1

        return self.currentWord

    def goToNextPage(self):
        if not self.hasNextPage:
            raise StopIteration("There isn't a Page subsequent to the current one")

        self.wordIndex = 0
        self.pageIndex += 1
        self.words = self.pages.get(self.pageIndex) or getWordsFromUrl(self.url)
        return self.words

    def goToNextWord(self):
        if not self.hasNextWord:
            raise StopIteration("There isn't a Word subsequent to the current one")

        if self.wordIndex < len(self.words)-1:
            self.wordIndex += 1
        else:
            self.goToNextPage()

        return self.currentWord