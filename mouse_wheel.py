import PySimpleGUI as sg

layout = [  [sg.Text('My Window')],
            [sg.Multiline(size=(40,20), key='-ML-')],
            [sg.Input(key='-IN-'), sg.Text(size=(12,1), key='-OUT-')],
            [sg.Button('Go'), sg.Button('Exit')]  ]

window = sg.Window('Window Title', layout, return_keyboard_events=True)

while True:             # Event Loop
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    if window.find_element_with_focus().Key == '-ML-':
        print('Multiline event ', event, values)

window.close()