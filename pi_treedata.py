
from PySimpleGUI import TreeData

from table import Row
from image_collection import COL_STATUS_LVL, ImageCollection
from pi_folder_stats import FolderStats

'''
    Subclass of TreeData that Loads an Image Table into TreeData.

    Any table will work as long as it has four columns:
    - 'file_location'  - the directory name relative to a given home directory
    - 'file_name'      - the name of the image file
    - 'img_status'     - status of the image (tbd,etc.)
    - 'rvw_lvl'        - highest review level

    A set of TreeData entries is created,  
    one for each folder represented by 'file_location'.
    A TreeData entry is then created for each file, with the 'file_location' as the parent key.

    Creating the 'file_location' nodes is a two step process, first creating
    a hierarchical dictionary representing the folders, then 
    traversing that dictionary to create a node for each directory.

    For example, the file location '/2018-11/ipod touch/2018-11-01' becomes
    the dictionary:
    {"2018-11":{
        "ipod touch": {
            "2018-11-01": {}
        }
     }
    }

    That dictionary is then traversed to insert TreeData nodes for:
      parent="",                    key="/2018-11",                       text="2018-11"
      parent="/2018-11",            key="/2018-11/ipod touch",            text="ipod touch"
      parent="/2018-11/ipod touch", key="/2018-11/ipod touch/2018-11-01", text="2018-11-01"

    Once that is done, an image can be inserted with the 'file_location' as the parent key. For example:
      parent"/2018-11/ipod touch/2018-11-01", key="/2018-11/ipod touch/2018-11-01/IMG_2770.JPG", text="IMG_2770.JPG"

'''
# dictionary key for folder stats
# since we split the path by '/', no folder name in the path will contain a '/'
_STATS_ = '/stats/' 

class PiTreeData(TreeData):

    folder_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABnUlEQVQ4y8WSv2rUQRSFv7vZgJFFsQg2EkWb4AvEJ8hqKVilSmFn3iNvIAp21oIW9haihBRKiqwElMVsIJjNrprsOr/5dyzml3UhEQIWHhjmcpn7zblw4B9lJ8Xag9mlmQb3AJzX3tOX8Tngzg349q7t5xcfzpKGhOFHnjx+9qLTzW8wsmFTL2Gzk7Y2O/k9kCbtwUZbV+Zvo8Md3PALrjoiqsKSR9ljpAJpwOsNtlfXfRvoNU8Arr/NsVo0ry5z4dZN5hoGqEzYDChBOoKwS/vSq0XW3y5NAI/uN1cvLqzQur4MCpBGEEd1PQDfQ74HYR+LfeQOAOYAmgAmbly+dgfid5CHPIKqC74L8RDyGPIYy7+QQjFWa7ICsQ8SpB/IfcJSDVMAJUwJkYDMNOEPIBxA/gnuMyYPijXAI3lMse7FGnIKsIuqrxgRSeXOoYZUCI8pIKW/OHA7kD2YYcpAKgM5ABXk4qSsdJaDOMCsgTIYAlL5TQFTyUIZDmev0N/bnwqnylEBQS45UKnHx/lUlFvA3fo+jwR8ALb47/oNma38cuqiJ9AAAAAASUVORK5CYII='
    file_icon = b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAACXBIWXMAAAsSAAALEgHS3X78AAABU0lEQVQ4y52TzStEURiHn/ecc6XG54JSdlMkNhYWsiILS0lsJaUsLW2Mv8CfIDtr2VtbY4GUEvmIZnKbZsY977Uwt2HcyW1+dTZvt6fn9557BGB+aaNQKBR2ifkbgWR+cX13ubO1svz++niVTA1ArDHDg91UahHFsMxbKWycYsjze4muTsP64vT43v7hSf/A0FgdjQPQWAmco68nB+T+SFSqNUQgcIbN1bn8Z3RwvL22MAvcu8TACFgrpMVZ4aUYcn77BMDkxGgemAGOHIBXxRjBWZMKoCPA2h6qEUSRR2MF6GxUUMUaIUgBCNTnAcm3H2G5YQfgvccYIXAtDH7FoKq/AaqKlbrBj2trFVXfBPAea4SOIIsBeN9kkCwxsNkAqRWy7+B7Z00G3xVc2wZeMSI4S7sVYkSk5Z/4PyBWROqvox3A28PN2cjUwinQC9QyckKALxj4kv2auK0xAAAAAElFTkSuQmCC'

    @staticmethod
    def _add_dict_folder(dict:dict[str:dict],nodes:list[str],idx:int,row:Row):
        ''' Recursively add the a list of directory names to a hierarchicial dictionary 
            incrementing the node index for each recursion. 
            
            While doing this, it is keeping track of file statistics for the directory
            using the FolderStats class and FolderStats add_stats(row) method '''
        if idx >= len(nodes):
            # all done
            return 
            
        key = nodes[idx]
        if not key in dict:
            dict[key] = {_STATS_: FolderStats()}

        dict[key][_STATS_].add_stats(row)

        idx += 1
        PiTreeData._add_dict_folder(dict[key],nodes,idx,row)
        
    def __init__(self,rows:list[Row]=[],stats=None):
        super().__init__()
        self.rows = rows
        self._insert_folders()
        self._insert_files()
    
    def _insert_folders(self):
        ''' insert folders into parent TreeData object'''
        dict = {}

        # add folders to a hierarchical dictionary
        for row in self.rows:
            img_folder = row['file_location']
            nodes = img_folder.split('/')
            PiTreeData._add_dict_folder(dict,nodes,1,row)

        # insert "root" folders and children into Parent TreeData object
        for k,v in dict.items():
            self._insert_treedata_folder(k,v,"")

    def _insert_treedata_folder(self,key,value,parent):
        ''' Traverse a hierarchical dictionary inserting the 
            keys into the TreeData '''
        td_key = f'{parent}/{key}'
        values = value[_STATS_].get_stats()
        cnt = values[2]
        values = ImageCollection.translate_status_lvl(values[0],values[1])
        values.append(str(cnt))
        self.insert(parent,td_key,key,values=values,icon=self.folder_icon)
        for k,v in value.items():
            if k != _STATS_:
                self._insert_treedata_folder(k,v,td_key)

    def _insert_files(self):
        ''' Insert a treedata node for each row in the table.
            All parents should have been inserted already via 
            _insert_tree_data_folders  '''
        for row in self.rows:
            parent = row['file_location']
            v      = row['file_name']
            values = row[COL_STATUS_LVL]

            self.insert(parent, f'{parent}/{v}',v,values=values, icon=self.file_icon)

    def _update_rows(self,tree,key_id_dict,rows):
        ''' Update the treedata for a list of rows.

            tree - the PySimpleGUI tree object
            'key_id_dict' - dictionary of item id to tkkinter id
            rows - rows which were updated

            TODO: propagate possible status change to parent folders
        '''
        for row in rows:
            parent = row['file_location']
            v      = row['file_name']
            values = row[COL_STATUS_LVL]

            key = f'{parent}/{v}'
            id = key_id_dict[key]

            tree.Widget.set(id,'#1',values[0])
            tree.Widget.set(id,'#2',values[1])


