#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:36:46 2019

@author: xnat
"""
from tkinter import messagebox
import os, re, glob
import sys
import traceback

def list_cust_vars(folder):
    path = os.path.normpath(folder)
    # i=0
    flag = 1
    for root, dirs, files in sorted(os.walk(path, topdown=True)):
        depth = root[len(path) :].count(os.path.sep)
        #print(os.path.join(path,root))
        #print(files)
        if files != []:
            for file in files:
                #print("Nome file: %s" %file)
                #print(file)
                if re.match(
                    "([a-z]|[A-Z]|[0-9])*.dcm$", file
                ):  # check if every file inside that folder is dicom
                    flag = flag & 1
                else:
                    flag = flag & 0

            if flag == 1:  ## I FOUND THE SUBJECT DEPTH
                subject_depth = depth - 2
                if subject_depth < 0:
                    subject_depth = 0
                break
    custom_values = []
    custom_vars = []
    try:
        for root, dirs, _ in sorted(os.walk(path, topdown=True)):
            depth = root[len(path) :].count(os.path.sep)
            print(depth)
            print(subject_depth)
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
        messagebox.showerror("Error", err)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_tb(exc_traceback)
        sys.exit(1)   
        
    return custom_vars, custom_values


if __name__ == "__main__":
    values, vars = list_cust_vars("/home/xnat/Documents/Scan_XNAT/patients/DICOM/")
    print(vars)
    print(values)
