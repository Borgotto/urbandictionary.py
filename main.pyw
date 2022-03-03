from urban_dictionary import UrbanDictionary
import PySimpleGUI as sg

#urban dictionary init
ud = UrbanDictionary()

# GUI layout
sg.theme("Dark Blue 3")
layout = [
    [sg.Multiline(key="query", size=(101,1), tooltip="Type any word here...", pad=((5,5),(5,15))),
     sg.Button("🔎", key="search", size=(6,2), font=(None,11), tooltip="Search", pad=((10,5),(0,7))),
     sg.Button("🔁",key="random", size=(6,2), font=(None,11), tooltip="Random word", pad=((5,5),(0,7)))],

    [sg.Button("<<", key="previousPage", tooltip="previous page", size=(20,1), disabled = not ud.hasPreviousPage),
     sg.Button("<", key="previousWord", tooltip="previous word", size=(20,1), disabled = not ud.hasPreviousWord),
     sg.Button("⌂", key="homePage", tooltip="home page", size=(20,1), focus=True),
     sg.Button(">", key="nextWord", tooltip="next word", size=(20,1), disabled = not ud.hasNextWord),
     sg.Button(">>", key="nextPage", tooltip="next page", size=(20,1), disabled = not ud.hasNextPage),
    ],

    [sg.Text(ud.currentWord["name"],key="name",font=(None,12,"bold"),size=(50,None), tooltip="word")],
    [sg.Text(ud.currentWord["meaning"],key="meaning",size=(100,None), tooltip="meaning")],
    [sg.Text(ud.currentWord["example"],key="example",font=(None,10,"italic"),size=(100,None), tooltip="example")],
    [sg.Text(ud.currentWord["contributor"],key="contributor",size=(100,None), tooltip="contributor", pad=((5,5),(5,15)))]
]
window = sg.Window('Urban Dictionary', layout, finalize=True)

#gui logics
while True:
    event, values = window.read()

    if event is None:
        break

    elif event == "homePage":
        ud = UrbanDictionary()
        window["query"].update("")

    elif event == "random":
        ud = UrbanDictionary(random=True)
        window["query"].update("")

    elif event == "search":
        if values.get("query").replace("\n"," "):
            query = UrbanDictionary(values.get("query").replace("\n"," "))
            if query.currentWord:
                ud = query
            else:
                sg.popup("Sorry, we couldn't find: " + values.get('query').replace('\n', ' '), title="¯\\_(ツ)_/¯")
        else:
            sg.popup(f"Insert some text first", title="Error")
            continue

    elif event == "previousPage":
        ud.goToPreviousPage()
    elif event == "previousWord":
        ud.goToPreviousWord()
    elif event == "nextPage":
        ud.goToNextPage()
    elif event == "nextWord":
        ud.goToNextWord()

    word = ud.currentWord
    window["name"].update(word["name"])
    window["meaning"].update(word["meaning"])
    window["example"].update(word["example"])
    window["contributor"].update(word["contributor"])

    window["previousPage"].update(disabled = not ud.hasPreviousPage)
    window["previousWord"].update(disabled = not ud.hasPreviousWord)
    window["nextWord"].update(disabled = not ud.hasNextWord)
    window["nextPage"].update(disabled = not ud.hasNextPage)
