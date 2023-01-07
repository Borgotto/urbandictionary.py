import PySimpleGUI as sg

from urbandictionary_scraper import UrbanDictionary, get_words_from_url, auto_complete

# urban dictionary init
ud = UrbanDictionary()
ud.get_wotd()

# GUI layout
sg.theme("Dark Blue 3")
layout = [
    [sg.Multiline(key="query", size=(101,1), tooltip="Type any word here...", pad=((5,5),(5,15))),
     sg.Button("🔎", key="search", size=(6,2), font=(None,11), tooltip="Search", pad=((10,5),(0,7)), focus=True),
     sg.Button("🔁",key="random", size=(6,2), font=(None,11), tooltip="Random word", pad=((5,5),(0,7)))
    ],
    [sg.Button("<<", key="previousPage", tooltip="previous page", size=(20,1), disabled = not ud.has_previous_page),
     sg.Button("<", key="previousWord", tooltip="previous word", size=(20,1), disabled = not ud.has_previous_word),
     sg.Button("⌂", key="homePage", tooltip="home page", size=(20,1), disabled = ud.word is None),
     sg.Button(">", key="nextWord", tooltip="next word", size=(20,1), disabled = not ud.has_next_word),
     sg.Button(">>", key="nextPage", tooltip="next page", size=(20,1), disabled = not ud.has_next_page),
    ],
    [sg.Text(getattr(ud.word,'word',''),key="name",font=(None,12,"bold"),size=(50,None), tooltip="word")],
    [sg.Text(getattr(ud.word,'definition',''),key="meaning",size=(100,None), tooltip="meaning")],
    [sg.Text(getattr(ud.word,'example',''),key="example",font=(None,10,"italic"),size=(100,None), tooltip="example")],
    [sg.Text(getattr(ud.word,'author',''),key="contributor",size=(100,None), tooltip="contributor", pad=((5,5),(5,15)))]
]
window = sg.Window('Urban Dictionary', layout, finalize=True)

# gui logics
while True:
    interaction = window.read()
    if interaction is None:
        continue
    event, values = interaction

    # manage events
    if event is None:
        break
    elif event == "random":
        ud.get_random_word()
    elif event == "search":
        input = values.get("query").replace("\n"," ")
        if input:
            ud.get_definition(input)
            if ud.word is None:
                close_matches = auto_complete(input)[:5]
                message = f"Sorry, we couldn't find: {input}"+('\n\nDid you mean:\n'+'\n'.join(close_matches) if close_matches else '')
                sg.popup(message, title="¯\\_(ツ)_/¯")
                continue
        else:
            sg.popup(f"Insert some text first", title="Error")
            continue
    elif event == "previousPage":
        ud.go_to_previous_page()
    elif event == "previousWord":
        ud.go_to_previous_word()
    elif event == "homePage":
        ud.get_wotd()
    elif event == "nextWord":
        ud.go_to_next_word()
    elif event == "nextPage":
        ud.go_to_next_page()

    # update UI elements
    word = ud.word
    window["name"].update(word.word)
    window["meaning"].update(word.definition)
    window["example"].update(word.example)
    window["contributor"].update(word.author)
    window['homePage'].update(disabled = ud.word is None)
    window["previousPage"].update(disabled = not ud.has_previous_page)
    window["previousWord"].update(disabled = not ud.has_previous_word)
    window["nextWord"].update(disabled = not ud.has_next_word)
    window["nextPage"].update(disabled = not ud.has_next_page)
