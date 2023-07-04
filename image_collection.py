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

    def __init__(self,fn:str,metadata:CsvTable=None):
        if metadata == None:
            metadata = c.metadata

        super().__init__(fn=fn,metadata=metadata)

