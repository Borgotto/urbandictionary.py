import re
import requests
from urllib.parse import quote
from datetime import datetime as dt
from enum import Enum

class Word:
    """
    A class describing a word definition from www.urbandictionary.com
    """

    def __init__(self,
                    definition: str,
                    date: str,
                    permalink: str,
                    thumbs_up: int,
                    thumbs_down: int,
                    author: str,
                    word: str,
                    defid: int,
                    current_vote: str,
                    written_on: dt,
                    example: str):
        self.definition = definition
        self.date = date
        self.permalink = permalink
        self.thumbs_up = thumbs_up
        self.thumbs_down = thumbs_down
        self.author = author
        self.word = word
        self.defid = defid
        self.current_vote = current_vote
        self.written_on = written_on
        self.example = example

    def __eq__(self, __o: object) -> bool:
        try:
            return self.defid == getattr(__o, 'defid', None)
        except AttributeError:
            return False

    def __repr__(self):
        return f"Word(definition: {self.definition!r}, date: {self.date!r}, permalink: {self.permalink!r}, thumbs_up: {self.thumbs_up!r}, thumbs_down: {self.thumbs_down!r}, author: {self.author!r}, word: {self.word!r}, defid: {self.defid!r}, current_vote: {self.current_vote!r}, written_on: {self.written_on!r}, example: {self.example!r})"

def get_words_from_url(url: str, markdown: bool = False) -> list[Word]:
    """Utility function to extract the words from any valid url from the
    api.urbandictionary.com endpoints

    Arguments
    -------------
    url: `str`
        the full URL from api.urbandictionary.com
        e.g. https://api.urbandictionary.com/v0/define?term=life&page=1

    markdown: `bool`
        whether to format the string to support markdown

    Return value
    -------------
    A `list` containing the `Word` objects
    """

    # Static Session object
    try:
        session = get_words_from_url.session
    except AttributeError:
        session = get_words_from_url.session = requests.Session()

    # Fetch the json from the url
    response = session.get(url).json()
    if response.get('error') or response.get('list') is None:
        raise Exception(response.get('error') or 'Invalid response')

    # Create markdown links for the words defined in square brackets
    def _format_markdown(string: str):
        regex = '\[.*?\]'
        transform_func = lambda x: x.group()+f'(https://www.urbandictionary.com/define.php?term={quote(x.group()[1:-1])})' if markdown else x.group()[1:-1]
        return re.sub(regex, transform_func, string)

    # Create and return a list of Word objects
    return [Word(
            definition=_format_markdown(word.get('definition','')),
            date=word.get('date'),
            permalink=word.get('permalink'),
            thumbs_up=word.get('thumbs_up'),
            thumbs_down=word.get('thumbs_down'),
            author=word.get('author'),
            word=word.get('word'),
            defid=word.get('defid'),
            current_vote=word.get('current_vote'),
            written_on=dt.strptime(word['written_on'],'%Y-%m-%dT%H:%M:%S.%fZ'),
            example=_format_markdown(word.get('example',''))
        ) for word in response['list']]

def auto_complete(query: str) -> list[str]:
    """
    Returns a list of words that auto complete the query, these strings can later be used to query the entire word
    """
    # Static Session object
    try:
        session = auto_complete.session
    except AttributeError:
        session = auto_complete.session = requests.Session()

    # Fetch the json from the url
    response = session.get(f'https://api.urbandictionary.com/v0/autocomplete?term={quote(query)}').json()
    try:
        if response.get('error'):
            raise Exception(response.get('error') or 'Invalid response')
    except AttributeError:
        pass

    return response



class UrbanDictionary:
    """A class to handle queries on https://www.urbandictionary.com/"""

    class query_type(Enum):
        """Enum to handle the different types of queries"""
        EMPTY = None
        WORD = ''
        RANDOM = -1
        WOTD = -2

    def __init__(
                self,
                markdown: bool = False,
                caching: bool = True):
        """
        Arguments
        -------------------------
        markdown: `bool`
            if true `Word`s will be formatted to support markdown

        caching: `bool`
            if true `Word`s will be cached to save time and bandwidth
        """
        self.is_markdown: bool = markdown
        self.is_caching: bool = caching
        self.query = self.query_type.EMPTY
        self.word_index: int = 0
        self.page_index: int = 0
        self.cached_pages: list[list[Word]] = []  # Empty if not is_caching

    @property
    def url(self) -> str:
        """
        the current URL used to query from urbandictionary.com
        e.g. https://www.urbandictionary.com/define.php?term=life
        """
        if self.query == self.query_type.EMPTY: # If no query is set return None
            return ''

        base_url = "https://api.urbandictionary.com/v0/"
        query_str = ''
        if self.query and type(self.query) == str:
            query_str = f"define?term={quote(str(self.query))}&page={self.page_index+1}"
        elif self.query == self.query_type.RANDOM:
            query_str = "random"
        elif self.query == self.query_type.WOTD:
            query_str = f"words_of_the_day?page={self.page_index+1}"
        return base_url + query_str

    @property
    def word(self) -> Word | None:
        """Returns the current `Word` of the current page"""
        try:
            return self.page[self.word_index]
        except IndexError:
            return None

    @property
    def page(self) -> list[Word]:
        """Returns the current page (`list[Word]`)"""
        if self.query == self.query_type.EMPTY:
            return []

        # Try to get the page from the cache, if it fails get it from the url
        try:
            page = self.cached_pages[self.page_index]
        except IndexError:
            page = get_words_from_url(self.url, self.is_markdown)

        # If caching is enabled, cache the page
        if self.is_caching:
            if self.page_index > len(self.cached_pages)-1:
                self.cached_pages.insert(self.page_index, page)
            else:
                self.cached_pages[self.page_index] = page

        return page

    @property
    def has_previous_page(self) -> bool:
        return self.page_index > 0

    @property
    def has_previous_word(self) -> bool:
        return self.word_index > 0 or self.has_previous_page

    @property
    def has_next_page(self) -> bool:
        self.page_index += 1
        next_page = self.page
        self.page_index -= 1
        return len(next_page) > 0

    @property
    def has_next_word(self) -> bool:
        return self.word_index < len(self.page)-1 or self.has_next_page

    def go_to_previous_page(self) -> list[Word]:
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

    def go_to_previous_word(self) -> Word | None:
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

    def go_to_next_page(self) -> list[Word]:
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

    def go_to_next_word(self) -> Word | None:
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

    def _new_query(self, type: query_type, query: str = '') -> Word | None:
        self.query = query if type == self.query_type.WORD else type
        self.page_index = 0
        self.word_index = 0
        self.cached_pages = []
        return self.word

    def get_definition(self, word: str) -> Word | None:
        """
        Query for a specific word, a random word or words of the day

        Arguments
        -------------------------
        query: `str`
            the word or phrase to query for

        Return value
        -------------------------
        The first `Word` of the first page
        """
        return self._new_query(self.query_type.WORD, word)

    def get_random_word(self) -> Word | None:
        """
        Get random words

        Return value
        -------------
        The first `Word` of the first page
        """
        return self._new_query(self.query_type.RANDOM)

    def get_wotd(self) -> Word | None:
        """
        Get a page of the words of the day

        Return value
        -------------
        The first `Word` of the first page
        """
        return self._new_query(self.query_type.WOTD)
