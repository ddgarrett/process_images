import PySimpleGUI as sg
from PIL import Image
from pi_image_util import cnv_image

# help(sg.Column)
new_im = Image.new('RGBA', (200, 200), 'black')
im = cnv_image(new_im)

c1 = [[]]
for i in range(5):
    tooltip = f'tooltip for\nbutton {i}'
    # image_source=im,
    e = [[sg.Button(button_color=('white','black'),k=f'b{i}',
                     pad=0,expand_x=True,expand_y=True, border_width=0,
                    tooltip=tooltip)]]
    f = [sg.Frame(f'Frame f{i}',e,element_justification='center',
                  title_location=sg.TITLE_LOCATION_BOTTOM_LEFT,
                  size=(200,200), pad=0)]
    c1 += [f]


column1 = c1

layout = [
    [sg.Frame("",
        [[sg.Column(column1, scrollable=True,  vertical_scroll_only=True, key="-COL-",
                  expand_y=True, expand_x=True, pad=0,
                  justification='center',vertical_alignment="top")]], 
        expand_x=True,pad=0)
        # sg.Column(column2)
    ],
    [sg.Frame("",
     [[        sg.Text('Test here', relief=sg.RELIEF_SUNKEN,
                    size=(55, 1), pad=(0, 3), key='-STATUS-', expand_x=True),
        sg.Sizegrip(pad=(3,3))
    ]])
    ]
]


window = sg.Window('Scrollable', layout,size=(800, 500),
                   resizable=True, enable_window_config_events=True)

to = (0,0)
cnt = 0
prev_to = (1,1)
while True:
    event, values = window.read(100)

    if event in (sg.WIN_CLOSED, 'Exit'):
        break

    vsb = window['-COL-'].vsb   
    if vsb.get() != to:
        to = vsb.get()
        cnt = 1
        waiting = True
    else:
        if waiting:
            cnt += 1
            if cnt > 4:
                waiting = False
                print(int(to[0]*100),'to',int((to[1])*100-.01))

    if event != '__TIMEOUT__':
        print(f'event: {event}')
        print(f'  values:{values}')

window.close()