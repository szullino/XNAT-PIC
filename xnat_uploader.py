#!/home/ictadmin/xnat/bin/python

"""
Created on Mar 1, 2019

@author: xnat
"""
import shutil, os
import xnat
from glob import glob
from tkinter import messagebox
import re
from setuptools.unicode_utils import try_encode
import datetime
import pydicom
import sys
import traceback
try:
    import tkinter as tk        # python v3
except:
    import Tkinter as tk        # python v2
from tkinter import filedialog

# from tkinter import ttk


def xnat_uploader(folder_to_convert, project_id, num_cust_vars, address, user, psw):

    try:
        flag = 1
        path = folder_to_convert

        ## FIND DEPTH OF SUBJECT FOLDER ##
        for root, dirs, files in sorted(os.walk(path, topdown=True)):
            depth = root[len(path) :].count(os.path.sep)

            for file in files:
                if re.match("([a-z]|[A-Z]|[0-9])*.dcm$", file):
                    flag = flag & 1
                else:
                    flag = flag & 0
            if flag == 1:
                subject_depth = depth - 2
                if subject_depth < 0:
                    subject_depth = 0
                del dirs
                dirs = []
                dirs[:] = []
        for root, dirs, files in sorted(os.walk(path, topdown=True)):
            depth = root[len(path) :].count(os.path.sep)
            if subject_depth == depth:
                for subject_dir in dirs:
                    #subject_dir = "_".join(subject_dir.split('.')) 
                    #print("subject dir %s" % subject_dir)
                    path = root
                    custom_vars = []
                    custom_values = []

                    for x in range(0, num_cust_vars):
                        custom_values.append(os.path.basename(path))
                        path = os.path.dirname(path)
                        custom_vars.append(os.path.basename(path))
                        path = os.path.dirname(path)
                    custom_vars = custom_vars[::-1]
                    custom_values = custom_values[::-1]
                    file_list = glob(os.path.join(root, subject_dir) + "/*/*")
                    try:
                        ds = pydicom.dcmread(file_list[0])
                        subject_dir = "_".join(subject_dir.split('.')) #subject id changed from .xyz to _xyz

                        if ds.StudyDate != "" and ds.StudyTime != "":
                            experiment_id = (
                                subject_dir + "_" + ds.StudyDate + "_" + ds.StudyTime
                            )

                        else:
                            experiment_id = (
                                subject_dir
                                + "_"
                                + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            )
                        for var in custom_values:
                            experiment_id += "_" + var
                        try:
                            with xnat.connect(address, user, psw) as session:
                                zip_dst = shutil.make_archive(subject_dir, "zip", root)
                                project = session.classes.ProjectData(
                                    name=project_id, parent=session
                                )
                                subject = session.classes.SubjectData(
                                    parent=project, label=subject_dir
                                )
                                session.services.import_(
                                    zip_dst,
                                    overwrite="none",
                                    project=project_id,
                                    subject=subject_dir,
                                    experiment=experiment_id,
                                )
                                subject = project.subjects[subject_dir]
                                ########
                                exp = project.subjects[subject_dir].experiments[
                                    experiment_id
                                ]
                                ########
                                for i, element in enumerate(custom_vars):
                                    subject.fields[element] = custom_values[i]
                                    exp.fields[element] = custom_values[i]
                                os.remove(zip_dst)
                        except Exception as e:
#                            messagebox.showerror("XNAT Uploader error", e)
#                            session.disconnect()
                            messagebox.showerror("XNAT Uploader", e)
                            exc_type, exc_value, exc_traceback = sys.exc_info()
                            traceback.print_tb(exc_traceback)
                            session.disconnect()
                            sys.exit(1)
                    except Exception as errr:
                        messagebox.showerror("XNAT Uploader", errr)

        answer = messagebox.askyesno(
            "Bruker2Dicom", "Do you want to upload your Bruker data to XNAT?"
        )
                
        if answer is True:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            bruker_folder = filedialog.askdirectory(parent=root,initialdir="/home/xnat/Documents/Scan_XNAT",title='Please select Bruker directory')
            print(bruker_folder)
            session = xnat.connect(address, user, psw)
            rsc_label = 'bruker_data'
            project = session.classes.ProjectData(name=project_id, parent=session)
            resource = session.classes.ResourceCatalog(parent=project, label=rsc_label)
            try:
                zip_bruker = shutil.make_archive(os.path.basename(bruker_folder), 'zip', bruker_folder)
            except OSError:
                pass
            resource.upload(zip_bruker, project_id, overwrite=True, extract=True) 
            print('Uploaded')
            #os.remove(zip_bruker)
            
            session.disconnect()
#            except Exception as err:
#                    messagebox.showerror("XNAT Uploader", err)
#                    exc_type, exc_value, exc_traceback = sys.exc_info()
#                    traceback.print_tb(exc_traceback)
#                    session.disconnect()
#                    sys.exit(1)
        #

        ########
        messagebox.showinfo(
            "Bruker2Dicom", "DICOM images have been successfully imported to XNAT!"
        )

        os._exit(0)

    except Exception as error:
        messagebox.showerror("XNAT Uploader", error)
        sys.exit(1)
        #os._exit(1)
