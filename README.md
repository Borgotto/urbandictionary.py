# urbandictionary.py
A web scraper written in Python to extract words from https://www.urbandictionary.com/

### Requirements:
- [Python 3.8.8](https://www.python.org/downloads/) (or newer)
- [BeautifulSoup 4.9+](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
- [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/#install) (optional, if you don't want to use main.py)
- `cd` to the repo folder and install via `pip install -r requirements.txt` command

### Features:
- everything you can do through the website but without graphical interface <br />
  (except for user-related stuff like login, vote or submit new definitions)

### Usage:
- #### print words from the main page
```python
from urban_dictionary import UrbanDictionary

ud = UrbanDictionary()

word_of_the_day = ud.currentWord
print( "Today's WOTD is", word_of_the_day.get("name") )

if ud.hasNextWord:
  ud.goToNextWord()
  print( "Yesterday's WOTD was", ud.currentWord.get("name") )
  
if ud.hasNextPage:
  ud.goToNextPage()
  print( "Last week's WOTD was", ud.currentWord.get("name") )
```
- #### search for specific words
```python
from urban_dictionary import UrbanDictionary

ud = UrbanDictionary("meaning of life")

#be sure to check that there's actually a definition for that word
if ud.currentWord is None:
  print("no definition")
else:
  print( "Top definition for 'meaning of life' is:", ud.currentWord.get("meaning") )
```
- #### you can also get random words
```python
from urban_dictionary import UrbanDictionary

ud = UrbanDictionary(random=True)

#there's always going to be a word to get, no checks needed
print( "Feeling lucky? Here's a random word \n" + ud.currentWord.get("name") + "\n\n" + ud.currentWord.get("example") )

#let's get another random page full of random words
ud.goToPreviousPage()
print( "Another random word \n" + ud.currentWord.get("name") + "\n\n" + ud.currentWord.get("example") )
```
