# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:32:28 2018

@author: Sara Zullino
"""
import os


def restore_raw_dirs(folder_to_convert):

    # Remove DICOM files from Bruker raw directory
    for (path, dirs, files) in os.walk(folder_to_convert):
        # print('Directory: {:s}'.format(path))
        # Repeat for each file in directory
        for file in files:
            if file.endswith(".dcm"):
                # print(os.path.join(path,file))
                os.remove(os.path.join(path, file))
