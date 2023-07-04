'''
    Image Collection Table

    Holds data about an image collection as defined by 
    image_collection_metadata.csv

'''
from __future__ import annotations

import PySimpleGUI as sg

import pi_config as c
from csv_table import CsvTable

class ImageCollection(CsvTable):

    # System field name constants
    # Use as table[Table.NAME] or table.get(Table.NAME)
    FULL_IMAGE_FN    = "FULL_IMAGE_FN"   # name needed to open the image file
    IMAGE_DIR        = "IMAGE_DIR"

    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'


    def __init__(self,fn:str,metadata:CsvTable=None):
        if metadata == None:
            metadata = c.metadata

        super().__init__(fn=fn,metadata=metadata)

    ''' get system value '''
    def get_sys_value(self,name:str) -> any:
        if name == ImageCollection.FULL_IMAGE_FN:
            return self.get_full_image_fn()
        
        if name == ImageCollection.IMAGE_DIR:
            return self.get_image_dir()
        
        return super().get_sys_value(name)
    
    def get_full_image_fn(self):
        return f'{c.directory}{self["file_location"]}/{self["file_name"]}'
    
    def get_image_dir(self):
        return f'{c.directory}{self["file_location"]}'
    
    def get_treedata(self) -> sg.TreeData:
        ''' return a Hierarchical TreeData representation of this collection '''
        treedata = sg.TreeData()
        self._insert_treedata_folders(treedata)
        self._insert_treedata_files(treedata)
        return treedata

    def _insert_treedata_folders(self,treedata:sg.TreeData):
        prev_folder = ""
        dict = {}

        # add folders to a hierarchical dictionary
        for row in self:
            img_folder = self['file_location']
            if prev_folder != img_folder:
                prev_folder = img_folder
                nodes = nodes.split('/')
                ImageCollection._add_dict_folder(dict,nodes,1)

        # insert folders into treedata
        for k,v in dict.items():
            ImageCollection._insert_treedata_folder(treedata,k,v,"")

    @staticmethod
    def _add_dict_folder(dict:dict[str:dict],nodes:list[str],idx:int):
        ''' add the indexed node to a hierarchicial dictionary
            then call self for next node'''
        if idx >= len(nodes):
            # all done
            return 
            
        key = nodes[idx]
        if not key in dict:
            dict[key] = {}

        idx += 1
        ImageCollection._add_dict_folder(dict[key],nodes,idx)

    @staticmethod
    def _insert_treedata_folder(treedata,key,value,parent):
        td_key = f'{parent}/{key}'
        treedata.insert(parent,td_key,key,values=[],icon=ImageCollection.folder_icon)
        for k,v in value.items():
            ImageCollection._insert_treedata_folder(treedata,k,v,td_key)

    def _insert_treedata_files(self,treedata:sg.TreeData):
        for row in self:
            parent = row['file_location']
            v      = row['file_name']
            treedata.insert(parent, f'{parent}/{v}',v,values=[], icon=self.file_icon)
