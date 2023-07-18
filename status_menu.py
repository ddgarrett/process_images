'''
    Return a common set of menu items to set the status of one or more photos.

    Returns an array of items which can be added to a list of menu items.

    Use something like this to embed the items in your memnu
    menu = ['',
             [ 'your item 1',
               StatusMenu(self.rowgetter).get_menu(),
               'your item 2']
            ]

'''

import pi_config as c
from status_menu_item import StatusMenuItem

class StatusMenu():
    def __init__(self,rowget=None):
        self.rowget = rowget

    def get_menu(self):
        menu = [ 
             'Set Status...',[
                 StatusMenuItem('Reject',c.STAT_REJECT,c.LVL_INITIAL,self.rowget).item(), 
                 StatusMenuItem('Bad Quality',c.STAT_QUAL_BAD,c.LVL_QUAL,self.rowget).item(),
                 StatusMenuItem('Duplicate',c.STAT_DUP,c.LVL_DUP,self.rowget).item(),
                 StatusMenuItem('Just Okay',c.STAT_OK,c.LVL_OK,self.rowget).item(),
                 StatusMenuItem('Good',c.STAT_GOOD,c.LVL_GOOD,self.rowget).item(),
                 StatusMenuItem('Best!',c.STAT_BEST,c.LVL_BEST,self.rowget).item()],
             'TBD - Possible...',[
                 StatusMenuItem('Reject',c.STAT_TBD,c.LVL_INITIAL,self.rowget).item(),
                 StatusMenuItem('Bad Quality',c.STAT_TBD,c.LVL_QUAL,self.rowget).item(),
                 StatusMenuItem('Duplicate',c.STAT_TBD,c.LVL_DUP,self.rowget).item(),
                 StatusMenuItem('Ok Good Best',c.STAT_TBD,c.LVL_OK,self.rowget).item(),
                 StatusMenuItem('Good or Best',c.STAT_TBD,c.LVL_GOOD,self.rowget).item()
                 ],
            ]
        
        return menu