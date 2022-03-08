"""TODO Docstring
soon™
"""

__author__ = "Emanuele Borghini"
__version__ = "0.1"

__all__ = ["UrbanDictionary", "get_words_from_url"]


import re
import requests
import urllib.parse

from bs4 import BeautifulSoup, element
import lxml


def _escape_markdown(text: str):
    def replacement(match):
        return match.groupdict().get("url") or "\\".join(match.groupdict()["markdown"])
    regex = r"(?P<markdown>[_\\~|\*`]|%s)" % r"^>(?:>>)?\s|\[.+\]\(.+\)"
    return re.sub(regex, replacement, text, 0, re.MULTILINE)


def _get_string_from_div(div, markdown : bool = False):
    """Utility function to extract a string from a div.

        The string can be formatted using markdown,
        this function is highly dependend from
        https://www.urbandictionary.com/ html page
    """
    string = ""
    for html_elem in (content for content in div.contents):
        if markdown:
            text = _escape_markdown(html_elem.text)
        else:
            text = html_elem.text

        if isinstance(html_elem, element.Tag) and html_elem.name == "br":
            string += "\n"
        elif isinstance(html_elem, element.Tag) and html_elem.name == "a" and markdown:
            string += (f"[{text}]" +
                       f"(https://www.urbandictionary.com{html_elem.attrs['href']})")
        else:
            string += text
    return string


def get_words_from_url(url: str, markdown: bool = False):
    """Function that returns a list containing the words from any
       valid url from https://www.urbandictionary.com/ domain
    """

    # Static Session object
    try:
        session = get_words_from_url.session
    except AttributeError:
        session = get_words_from_url.session = requests.Session()

    # Fetch all of the html divs containing the words definitions
    response = session.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    divs = soup.findAll("div", class_="definition")

    # For each div extract the informations and put it in the list
    words = []
    for contents in (div.contents[0].contents for div in divs):
        words.append({"url": "https://www.urbandictionary.com" +
                             contents[0].contents[0].contents[0].attrs["href"],
                      "name": _get_string_from_div(contents[0], markdown),
                      "meaning": _get_string_from_div(contents[1], markdown),
                      "example": _get_string_from_div(contents[2], markdown),
                      "contributor": _get_string_from_div(contents[3], markdown)})
    return words


class UrbanDictionary():
    """A class to handle queries on https://www.urbandictionary.com/"""

    def __init__(self,
                query: str = None,
                random: bool = False,
                markdown: bool = False,
                caching: bool = True):
        if query and query.strip():
            self.query = urllib.parse.quote(query.strip())
            self.random = False
        else:
            self.query = None
            self.random = random
        self.is_markdown_enabled = markdown
        self.is_caching_enabled = caching
        self.word_index = 0
        self.page_index = 1
        self.page = get_words_from_url(self.url, self.is_markdown_enabled)
        self.pages = {self.page_index: self.page} if self.is_caching_enabled else {}

    @property
    def url(self):
        url = "https://www.urbandictionary.com/"
        if self.query:
            url += f"define.php?term={self.query}&"
        elif self.random:
            url += "random.php?"
        else:
            url += "?"
        return url + f"page={self.page_index}"

    @property
    def current_word(self):
        if self.page:
            return self.page[self.word_index]
        else:
            return None

    @property
    def has_previous_page(self):
        return self.random or self.page_index > 1

    @property
    def has_previous_word(self):
        return self.word_index > 0 or self.has_previous_page

    @property
    def has_next_page(self):
        self.page_index += 1
        words = (self.pages.get(self.page_index) or
                 get_words_from_url(self.url, self.is_markdown_enabled))
        if self.is_caching_enabled:
            self.pages[self.page_index] = words
        self.page_index -= 1
        return self.random or len(words) > 0

    @property
    def has_next_word(self):
        return self.word_index < len(self.page)-1 or self.has_next_page

    def go_to_previous_page(self):
        if not self.has_previous_page:
            raise StopIteration("There isn't a Page prior to the current one")

        self.word_index = 0
        self.page_index -= 1
        self.page = (self.pages.get(self.page_index) or
                     get_words_from_url(self.url, self.is_markdown_enabled))
        return self.page

    def go_to_previous_word(self):
        if not self.has_previous_word:
            raise StopIteration("There isn't a Word prior to the current one")

        if self.word_index > 0:
            self.word_index -= 1
        else:
            self.go_to_previous_page()
            self.word_index = len(self.page)-1
        return self.current_word

    def go_to_next_page(self):
        if not self.has_next_page:
            raise StopIteration("There isn't a Page after the current one")

        self.word_index = 0
        self.page_index += 1
        self.page = (self.pages.get(self.page_index) or
                     get_words_from_url(self.url, self.is_markdown_enabled))
        return self.page

    def go_to_next_word(self):
        if not self.has_next_word:
            raise StopIteration("There isn't a Word after the current one")

        if self.word_index < len(self.page)-1:
            self.word_index += 1
        else:
            self.go_to_next_page()
        return self.current_word
