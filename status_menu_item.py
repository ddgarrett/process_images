
from pi_action import PiAction

import pi_config as c

class StatusMenuItem(PiAction):
    '''
        Define Menu Items which set status and level.

        This class reserves the event ID prefix "::-STATUSITEM_".
        Events are named "-STATUSITEM_n" where 'n' is a sequental number
        incremented for each instance of this class.

        Example below builds an array which can be used as the value for a 
        right click menu which Allows setting an image to 'reject', 'bad', 
        or 'dup'.

        menu = ['', 
            ['Reviewed As',[
                 StatusMenuItem('Reject','reject','0',self.get_row).item(), 
                 StatusMenuItem('Bad Quality','bad','1',self.get_row).item(),
                 StatusMenuItem('Duplicate','dup','2',self.get_row).item()
            ]
        ]

        Parms:
        text - The Menu Item text to be displayed
        status - value to set the selected rows status to
        level  - value to set selected rows level to
        rowget - method to call to get a list of rows affected

        The rowget is passed the values received when the event 
        was received and must return a list of zero or more rows
        for which the level and status will be set.
    '''
    last_id = 0

    @classmethod
    def next_id(cls):
        cls.last_id += 1
        return cls.last_id
    
    def __init__(self,text,status,level,rowget=None,):
        self._id = self.next_id()
        self._text = text
        self._status = status
        self._level = level
        self._rowget = rowget

        super().__init__(event=self._get_event())

    def _get_event(self):
        return f'-STATUSITEM_{self._id}-'
    
    def item(self):
        ''' return an item name and unique event id'''
        return f'{self._text}::{self._get_event()}'
    
    def handle_event(self,event,values):
        rows = self._rowget(values)
        for row in rows:
            row['rvw_lvl'] = self._level
            row['img_status'] = self._status

        values[c.EVT_TABLE_ROW_CHG] = rows
        c.listeners.notify(c.EVT_TABLE_ROW_CHG,values)
