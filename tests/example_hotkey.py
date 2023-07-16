import PySimpleGUI as sg

layout = [
    [sg.Button("ok", size=(10, 2), key='button1'),
     sg.Button("exit", size=(10, 2), key='button2')],
]
window = sg.Window('Hotkeys', layout, use_default_focus=False, finalize=True)
button1, button2 = window['button1'], window['button2']

window.bind("<Control_L><o>", "ALT-o")
window.bind("<Alt_L><x>", "ALT-x")

button1.Widget.configure(underline=0, takefocus=0)
button2.Widget.configure(underline=1, takefocus=0)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event in ("button1", "ALT-o"):
        print('OK')
    elif event in ("button2", "ALT-x"):
        break

window.close()