# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 15:19:34 2018

@author: Sara Zullino
"""
import os
from os import rmdir
import errno

# Remove empty directories
def remove_empty_dirs(dst):
    dirs = [x[0] for x in os.walk(dst, topdown=False)]
    for dir in dirs:
        try:
            rmdir(dir)
        except Exception as e:
            if e.errno == errno.ENOTEMPTY:
                pass
                # print("Directory: {0} not empty".format(dir))
