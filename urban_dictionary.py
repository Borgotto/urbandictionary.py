"""TODO Docstring
soon™
"""

__author__ = "Emanuele Borghini"
__version__ = "0.1"

__all__ = ["UrbanDictionary", "Word", "get_words_from_url"]


import re
import requests
import urllib.parse

from bs4 import BeautifulSoup, element
import lxml


def _escape_markdown(text: str):
    def replacement(match):
        return (match.groupdict().get("url") or
                "\\".join(match.groupdict()["markdown"]))
    regex = r"(?P<markdown>[_\\~|\*`]|%s)" % r"^>(?:>>)?\s|\[.+\]\(.+\)"
    return re.sub(regex, replacement, text, 0, re.MULTILINE)


def get_string_from_div(div: element.Tag, markdown: bool = False):
    """Utility function to extract a string from 'definition' divs.

    Arguments
    -------------
    div: `element.Tag`
        an html div from urbandictionary.com

    markdown: `bool`
        whether to format the string to support markdown

    Return value
    -------------
    A string containing the joined text of all elements inside the div

    N.B.
    -------------
    this function is highly dependant from
    https://www.urbandictionary.com/ html page
    """

    string = ""
    for child in div.children:
        if markdown:
            text = _escape_markdown(child.text)
        else:
            text = child.text

        if isinstance(child, element.Tag) and child.name == "a" and markdown:
            string += (f"[{text}]" +
                        "(https://www.urbandictionary.com" +
                       f"{child.attrs['href']})")
        elif isinstance(child, element.Tag) and child.name == "br":
            string += "\n"
        else:
            string += text
    return string


def get_words_from_url(url: str, markdown: bool = False):
    """Utility function to extract the words from any valid url from the
    urbandictionary.com domain

    Arguments
    -------------
    url: `str`
        the full URL from urbandictionary.com
        e.g. https://www.urbandictionary.com/define.php?term=life

    markdown: `bool`
        whether to format the string to support markdown

    Return value
    -------------
    A `list` containing the `Word` objects

    N.B.
    -------------
    this function is highly dependant from
    https://www.urbandictionary.com/ html page
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
    words: list[Word] = []

    # Foreach definition div extract the Word and append it to the list
    for div in divs:
        word_divs = div.contents[0].contents
        word = Word(url="https://www.urbandictionary.com" +
                        word_divs[0].contents[0].contents[0].attrs["href"],
                    name=get_string_from_div(word_divs[0], markdown),
                    meaning=get_string_from_div(word_divs[1], markdown),
                    example=get_string_from_div(word_divs[2], markdown),
                    contributor=get_string_from_div(word_divs[3], markdown))
        words.append(word)
    return words

class Word:
    """
    A class describing a word definition from www.urbandictionary.com
    """

    def __init__(
                 self,
                 url: str,
                 name: str,
                 meaning: str,
                 example: str,
                 contributor: str,
                 voting : tuple = (0,0)):
        self.url = url
        self.name = name
        self.meaning = meaning
        self.example = example
        self.contributor = contributor
        self.voting = voting

    def __eq__(self, __o: object) -> bool:
        try:
            return (self.url == __o.url and
                    self.name == __o.name and
                    self.meaning == __o.meaning and
                    self.example == __o.example)
        except AttributeError:
            return False


class UrbanDictionary:
    """A class to handle queries on https://www.urbandictionary.com/"""

    def __init__(
                self,
                query: str = None,
                random: bool = False,
                markdown: bool = False,
                caching: bool = True):
        """
        Arguments
        -------------------------
        query: `str`
            represents the text searched on urbandictionary.com.
            if None the site's homepage is queried

        random: `bool`
            if true random `Word`s will be queried

        markdown: `bool`
            if true `Word`s will be formatted to support markdown

        caching: `bool`
            if true `Word`s will be cached to save time and bandwidth
        """
        self.query = query.strip() if query and query.strip() else None
        self.is_random = random if not self.query else False
        self.is_markdown = markdown
        self.is_caching = caching
        self.word_index = 0
        self.page_index = 1
        self.pages: dict[int,list[Word]] = {}  # empty if not is_caching

    @property
    def url(self):
        """
        the current URL used to query from urbandictionary.com
        e.g. https://www.urbandictionary.com/define.php?term=life
        """
        url = "https://www.urbandictionary.com/"
        if self.query:
            url += f"define.php?term={urllib.parse.quote(self.query)}&"
        elif self.is_random:
            url += "random.php?"
        else:
            url += "?"
        return url + f"page={self.page_index}"

    @property
    def word(self):
        """Returns the current `Word` of the current page"""
        try:
            return self.page[self.word_index]
        except IndexError:
            return None

    @property
    def page(self):
        """Returns the current page (`list[Word]`)"""
        page = (self.pages.get(self.page_index) or
                get_words_from_url(self.url, self.is_markdown))
        if self.is_caching:
            self.pages[self.page_index] = page
        return page

    @property
    def has_previous_page(self):
        return self.is_random or self.page_index > 1

    @property
    def has_previous_word(self):
        return self.word_index > 0 or self.has_previous_page

    @property
    def has_next_page(self):
        self.page_index += 1
        next_page = self.page
        self.page_index -= 1
        return self.is_random or len(next_page) > 0

    @property
    def has_next_word(self):
        return self.word_index < len(self.page)-1 or self.has_next_page

    def go_to_previous_page(self):
        """
        Move onto the first `Word` of the previous page.

        Return value
        -------------
        The previous page (`list[Word]`) if present

        Raises
        -------------
        `StopIteration` in case there isn't a previous page
        """
        if not self.has_previous_page:
            raise StopIteration("There isn't a Page prior to the current one")

        self.word_index = 0
        self.page_index -= 1
        return self.page

    def go_to_previous_word(self):
        """
        Move onto the previous `Word` of the current page or last `Word`
        of the previous page

        Return value
        -------------
        The previous `Word` if present

        Raises
        -------------
        `StopIteration` in case there isn't a previous word or page
        """
        if not self.has_previous_word:
            raise StopIteration("There isn't a Word prior to the current one")

        if self.word_index > 0:
            self.word_index -= 1
        else:
            self.go_to_previous_page()
            self.word_index = len(self.page)-1
        return self.word

    def go_to_next_page(self):
        """
        Move onto the first `Word` of the next page.

        Return value
        -------------
        The next page (`list[Word]`) if present

        Raises
        -------------
        `StopIteration` in case there isn't a next page
        """
        if not self.has_next_page:
            raise StopIteration("There isn't a Page after the current one")

        self.word_index = 0
        self.page_index += 1
        return self.page

    def go_to_next_word(self):
        """
        Move onto the next `Word` of the current page or first `Word` of
        the next page

        Return value
        -------------
        The next `Word` if present

        Raises
        -------------
        `StopIteration` in case there isn't a next word or page
        """
        if not self.has_next_word:
            raise StopIteration("There isn't a Word after the current one")

        if self.word_index < len(self.page)-1:
            self.word_index += 1
        else:
            self.go_to_next_page()
        return self.word
