# urbandictionary.py 📚
A web scraper written in Python to extract words from https://www.urbandictionary.com/

### Requirements:
- [Python 3.8](https://www.python.org/downloads/)
- [BeautifulSoup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-beautiful-soup)
- [lxml](https://lxml.de/installation.html)
- [PySimpleGUI](https://pysimplegui.readthedocs.io/en/latest/#install) (optional, if you don't want to use main.py)

`cd` to the repo folder and install via `pip install -r requirements.txt` command

### Features:
- pretty much everything you can do through the website but without graphical interface <br />
  (except for user-related stuff like login, vote or submit new definitions)

|              Feature              |                    State                    |
|-----------------------------------|:-------------------------------------------:|
| get words from the main page      | <span title="Implemented">✔️</span>        |
| search for a specific definition  | <span title="Implemented">✔️</span>        |
| fetch random words                | <span title="Implemented">✔️</span>        |
| get words votings                 | <span title="Not implemented :c">❌</span> |
| user log-in                       | <span title="Not implemented :c">❌</span> |
| add definitions                   | <span title="Not implemented :c">❌</span> |
| ability to vote                   | <span title="Not implemented :c">❌</span> |

### Usage:
- #### print words from the main page
```python
from urban_dictionary import UrbanDictionary

ud = UrbanDictionary()

word_of_the_day = ud.word
print("Today's WOTD is", word_of_the_day.name)

if ud.has_next_word:
    word = ud.go_to_next_word()
    print("Yesterday's WOTD was", word.name)

if ud.has_next_page:
    ud.go_to_next_page()
    print("Last week's WOTD was", ud.word.name, end="\n\n")
```
- #### search for specific words
```python
ud = UrbanDictionary("meaning of life")

# Be sure to check that there's actually a definition for that word
if ud.word is None:
    print("no definition")
else:
    print("Top definition for 'meaning of life' is:\n" +
          ud.word.meaning, end="\n\n")
```
- #### you can also get random words
```python
ud = UrbanDictionary(random=True)

# There's always going to be a word to get, no checks needed
print("Feeling lucky? Here's a random word:\n" +
      ud.word.name + "\n" +
      ud.word.example, end="\n\n")

# Let's get another random page full of random words
ud.go_to_previous_page()
print("Another random word:\n" +
      ud.word.name + "\n" +
      ud.word.example, end="\n\n")
```

###### please, please, please send feedback
