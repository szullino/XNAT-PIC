#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:36:46 2019

@author: Sara Zullino, Alessandro Paglialonga
"""
from tkinter import messagebox
import os, re
import sys
import traceback

def list_cust_vars(folder):
    path = os.path.normpath(folder)
    # i=0
    flag = 1
    for root, dirs, files in sorted(os.walk(path, topdown=True)):
        depth = root[len(path) :].count(os.path.sep)
        if files != []:
            for file in files:
                #print("Nome file: %s" %file)
                # match and find every single file inside that folder, 
                # no matter the name and the extension (but it has to be dicom mandatory)
                if re.match("([^^]|[a-z]|[A-Z]|[0-9])*$", file):  
                    flag = flag & 1
                else:
                    flag = flag & 0

            if flag == 1:  ## I FOUND THE SUBJECT DEPTH
                subject_depth = depth - 3
                if subject_depth < 0:
                    subject_depth = 0
                break
    custom_values = []
    custom_vars = []
    try:
        for root, dirs, _ in sorted(os.walk(path, topdown=True)):
            depth = root[len(path) :].count(os.path.sep)
            if subject_depth == depth:
                path = root

                # MAX 3 CUSTOM VARIABLES
                # WE ONLY TAKE A POSSIBLE CUSTOM VALUE FOR EACH CUSTOM VARIABLE JUST TO SHOW IT TO THE USER
                for i in range(0, 3):
                    custom_values.append(os.path.basename(path))
                    path = os.path.dirname(path)
                    custom_vars.append(os.path.basename(path))
                    path = os.path.dirname(path)

                # custom_vars=custom_vars[::-1]    ## Il '-1' non prende lo '/'
                # custom_values=custom_values[::-1]
                break
                # dirs[:]=[]
    except Exception as err:
        messagebox.showerror("List Custom Variables Error", err)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        sys.exit(1)   
    

    return custom_vars, custom_values


if __name__ == "__main__":
    values, vars = list_cust_vars(os.path.expanduser("~"))

