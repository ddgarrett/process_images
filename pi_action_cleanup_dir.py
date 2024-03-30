''' Implement action to cleanup directories in a collection.

    Intended to be run after a reorg of images where images are moved into 
    /yyyy-mm-dd/ folders. Folders and files left after that reorg are then moved into
    either /_empty/ or /_lost/ folders.

    1. moves all unrecognized directories that don't begin with '_'
       into /_empty/

    2. moves any files in /_empty/ or the collection folder root, 
       into directory /_lost/, maintaining directory structure


'''

import os
import time

import PySimpleGUI as sg

import pi_config as c  # configuration/globals singleton
import pi_util as util 

from pi_action import PiAction



class PiCleanupDir(PiAction):
    ''' Cleanup current directory 
    
        1. Move unrecognized directories not in the collection
           into a _empty directory
           
        2. Move files not part of the collection
           into a _lost directory

        Note:
        - _empty and _lost directories are suffixed with a time stamp
          to make them unique
        
    '''
    
    def handle_event(self,event,values):

        if not c.table or len(c.table.rows()) == 0:
            sg.popup('Select directory or collection before running Cleanup')
            return 
        
        # get current dir, list of subdir and list of files
        root = next(os.walk(c.directory),None) # just get first tuple in os.walk

        if not root:
            sg.popup(f'Directory not found: {c.directory}')
            print("directory not found:",c.directory)
            return

        dir_sfx = str(round(time.time()*1000))
        empty_dir = '/_empty_' + dir_sfx
        lost_dir  = '/_lost_'  + dir_sfx

        # move unrecognized subdirectories to empty directory
        for dir in root[1]:
            if dir[0] in ['_','.','$']:
                print("skipping:",dir)
            elif util.dir_in_collection('/'+dir):
                print("dir in collection:",dir)
            else:
                print("moving:",dir,"to",empty_dir+'/'+dir)
                util.move_dir('/'+dir,empty_dir)

        # move any files in collection directory into lost directory
        print("moving",root[2])
        for fn in root[2]:
            util.move_file('/',lost_dir,fn)
                
        # walk the empty directory to move any files in them
        print("walking",c.directory+empty_dir)

        # use to root_idx to remove c.directory 
        # from before source and dest directory names
        root_idx = len(c.directory) 

        # use src_idx to remove source directory name from before dest
        src_idx  = len(empty_dir)

        # move any files from _empty to _lost
        for root, dirs, files in os.walk(c.directory+empty_dir):

            src_dir = root[root_idx:]
            dst_dir = lost_dir + src_dir[src_idx:]

            for fn in files:
                util.move_file(src_dir,dst_dir,fn)


