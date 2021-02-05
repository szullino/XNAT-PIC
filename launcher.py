#!/home/xnat/anaconda3/envs/py3/bin/python3.7
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 17:25:38 2019

@author: Sara Zullino, Alessandro Paglialonga
"""

import xnat
import os, re
import tkinter as tk
from tkinter import filedialog,messagebox
import threading
import shutil
from bruker2dicom import bruker2dicom
from bruker2dicom_pv360 import bruker2dicom_pv360
from include_patterns import include_patterns
from remove_empty_dirs import remove_empty_dirs
from restore_raw_dirs import restore_raw_dirs
from shutil import copytree
from functools import partial
from xnat_uploader import xnat_uploader
import platform
import pyAesCrypt
from list_cust_vars import list_cust_vars
import subprocess
from tkinter import ttk
from read_visupars import read_visupars_parameters
from read_method import read_method_parameters
import traceback
import sys

bufferSize = 64 * 1024
password = "worstsymmetricpasswordever19"


class xnat_pic_gui(tk.Frame):

    def __init__(self, master):

        self.root = master

        ### GET PRIMARY SCREEN RESOLUTION
        ### MADE FOR MULTISCREEN ENVIRONMENTS
        if (platform.system()=='Linux'):
            cmd_show_screen_resolution = subprocess.Popen("xrandr --query | grep -oG 'primary [0-9]*x[0-9]*'",\
                                                          stdout=subprocess.PIPE, shell=True)
            screen_output =str(cmd_show_screen_resolution.communicate()).split()[1]
            self.root.screenwidth, self.root.screenheight = re.findall("[0-9]+",screen_output)
        ###
        ###
        else :
            self.root.screenwidth=self.root.winfo_screenwidth()
            self.root.screenheight=self.root.winfo_screenheight()

        self.root.title("   XNAT-PIC   ~   Molecular Imaging Center   ~   University of Torino   ")
        self.root.resizable(False, False)
        self.root.width = 600
        self.root.height = 100
        self.x = (int(self.root.screenwidth) - self.root.width) / 2
        self.y = (int(self.root.screenheight)- self.root.height) / 3
        self.root.geometry("%dx%d+%d+%d" % (self.root.width, self.root.height, self.x, self.y))

        self.frame_main = tk.Frame(self.root)
        self.frame_main.pack()

        self.frame_labels = tk.Frame(self.frame_main)
        self.frame_labels.pack(side="left")
        self.frame_buttons = tk.Frame(self.frame_main)
        self.frame_buttons.pack(side="right")
        self.frame_progress = tk.Frame(self.frame_main)
        self.frame_progress.pack()
        self.frame_dialogs = tk.Frame(self.frame_main)
        self.frame_dialogs.pack()

        self.label_bruker_dicom = tk.Label(
            self.frame_labels,
            text="   Convert images from Bruker ParaVision format to DICOM standard  ",
            anchor="w",
        )
        self.label_bruker_dicom.pack(anchor="w", pady=3)
        self.label_aspect_dicom = tk.Label(
            self.frame_labels,
            text="   Convert images from Aspect Imaging to DICOM standard  ",
            anchor="w",
        )
        self.label_aspect_dicom.pack(anchor="w", pady=8)
        self.label_dicom_uploader = tk.Label(
            self.frame_labels,
            text="   Upload DICOM images to XNAT  ",
            anchor="w",
        )
        self.label_dicom_uploader.pack(anchor="w", pady=7)

        self.button1 = tk.Button(
            self.frame_buttons, text="  Bruker2DICOM  ", command=partial(self.bruker2dicom_conversion,self))

        self.button1.pack(padx=10, pady=0)
        self.button2 = tk.Button(self.frame_buttons, text="  Aspect2DICOM  ")
        self.button2.pack(padx=10, pady=1)
        self.button3 = tk.Button(
            self.frame_buttons, text="   Uploader   ", command=partial(self.xnat_dcm_uploader,self)
        )
        self.button3.pack(padx=10, pady=1)


    def _inprogress(self, text):

        self.frame_main.destroy()
        try:
            for element in self.stack_frames:
                element.destroy()
        except:
            pass
        self.root.width = 300
        self.root.height = 46
        self.x = (int(self.root.screenwidth) - self.root.width) / 2
        self.y = (int(self.root.screenheight)- self.root.height) / 3
        self.root.geometry("%dx%d+%d+%d" % (self.root.width, self.root.height, self.x, self.y))
        self.root.resizable(False, False)
        self.frame_main = tk.Frame(self.root)
        self.frame_main.pack(fill="x", side="top")

        self.button_conversion = tk.Button(self.frame_main, text=text)
        self.button_conversion["state"] = "disabled"
        self.button_conversion.pack(side="top", fill="x")

        self.progress = ttk.Progressbar(
            self.frame_main, orient=tk.HORIZONTAL, mode="indeterminate"
        )
        self.progress.pack(side="bottom", fill="x")
        self.progress.start()


    class bruker2dicom_conversion():
        def __init__(self,master):
            def start_conversion():

                master.root.withdraw()

                folder_to_convert = filedialog.askdirectory(
                    parent=master.root,
                    initialdir=os.path.expanduser("~"),
                    title="XNAT-PIC: Select project directory in Bruker ParaVision format",
                )

                if not folder_to_convert:
                    os._exit(1)
                master.root.deiconify()

                master.root.update()
                master.root.title("Bruker2DICOM")
                head, tail = os.path.split(folder_to_convert)
                project_foldername = tail.split('.',1)[0] + "_dcm"
                dst = os.path.join(head, project_foldername)

                master._inprogress("Conversion in progress")
                if os.path.isdir(dst):
                    master.progress.stop()
                    messagebox.showwarning(
                        "Destination folder already exists",
                        "Destination folder %s already exists and it won't be overridden \
                        by a new conversion. If you want to proceed with the conversion, please \
                        delete/move/rename the existing folder"
                        % dst,
                    )                            
                            
                a = "1"
                c = "visu_pars"
                e = "method"
                for root, dirs, files in sorted(os.walk(folder_to_convert, topdown=True)):
                    for dir in dirs:
                        res = os.path.join(root)
                        dirs[:] = []  # Don't recurse any deeper
                        visupars_file = os.path.abspath(os.path.join(res, a, c))
                        method_file = os.path.abspath(os.path.join(os.path.dirname(res), e))
                        #print(visupars_file)
                        #print(method_file)
                        if os.path.exists(visupars_file):
                            try:
                                with open(visupars_file, "r"):
                                    visupars_parameters = read_visupars_parameters(visupars_file)
                                    PV_version = visupars_parameters.get("VisuCreatorVersion")
                                    #print(visupars_file)
                                    #print(PV_version)
                                    del visupars_parameters
                            except Exception as e:
                                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                traceback.print_tb(exc_traceback)
                                sys.exit(1)
                        elif os.path.exists(method_file):
                            try:
                                with open(method_file, "r"):
                                    method_parameters = read_method_parameters(method_file)
                                    PV_version = method_parameters.get("TITLE")
                                    #print(method_file)
                                    #print(PV_version)
                                    del method_parameters
                            except Exception as e:
                                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                                exc_type, exc_value, exc_traceback = sys.exc_info()
                                traceback.print_tb(exc_traceback)
                                sys.exit(1)
                            
                ####################
                if PV_version == "360.1.1" or 'ParaVision 360' in PV_version:
                    try:                     
                        bruker2dicom_pv360(folder_to_convert, master)
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC - Bruker2DICOM", e)
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_tb(exc_traceback)
                        sys.exit(1)                
                else:
                    try:
                        bruker2dicom(folder_to_convert, master)
                    except Exception as e:
                        messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        traceback.print_tb(exc_traceback)
                        sys.exit(1)
                ####################

                ####################
                master.progress.stop()
                ####################

                # Copy the directory tree while keeping DICOM files only
                try:
                    copytree(
                        folder_to_convert, dst, ignore=include_patterns("*.dcm")
                    )
                except Exception as error:
                    messagebox.showerror("Error", str(error))
                # Remove DICOM files from Bruker raw directory
                restore_raw_dirs(folder_to_convert)
                # Remove empty directories
                remove_empty_dirs(dst)
                
                # # Source path  
                # source = dst
                  
                # # Destination path  
                
                # destination = os.path.join(head,'MR')

                # os.mkdir(destination)

                # # Move the content of  
                # # source to destination  
                # folder = os.listdir(source)
                # print(folder)
                # for f in folder:
                #     print(f)
                #     shutil.move(os.path.join(source,f), destination)
                # dest = shutil.move(destination, source) 
                
                flag = []

                ## FIND DEPTH OF SUBJECT FOLDER ##
                for root, dirs, files in sorted(os.walk(dst, topdown=True)):
                    depth = root[len(dst) :].count(os.path.sep)
                    for file in files:
                        if re.match("([^^]|[a-z]|[A-Z]|[0-9])*$", file):
                            flag = 1
                        else:
                            flag = 0
                    if flag == 1:
                        subject_depth = depth - 2
                        if subject_depth < 0:
                            subject_depth = 0
                        del dirs
                        dirs = []
                        dirs[:] = []
                for root, dirs, files in sorted(os.walk(dst, topdown=True)):
                    depth = root[len(dst) :].count(os.path.sep)
                    if subject_depth == depth:
                        for subject_name in dirs:
                            subject_dir = os.path.join(root,subject_name)
                            if os.path.exists(subject_dir) is True:
                                
                                destination = os.path.join(subject_dir,'MR')
                
                                os.mkdir(destination)
                
                                # Move the content of source to destination  
                                folder = os.listdir(subject_dir)
                                for f in folder:
                                    shutil.move(os.path.join(subject_dir,f), destination)

                answer = messagebox.askyesno(
                    "XNAT-PIC  ~  Uploader", "Do you want to upload your project to XNAT?"
                )
                # self.frame_main.destroy()
                if answer is True and os.path.isdir(dst) == True:
                    master.xnat_dcm_uploader(master,os.path.join(head,project_foldername))
                else:
                    os._exit(0)
            threading.Thread(target=start_conversion).start()

    class xnat_dcm_uploader():

        def __init__(self, master,home=""):
            self.home = os.path.expanduser("~")
            master.root.update()
            master.root.title("XNAT-PIC  ~  Uploader")
            master.root.deiconify()
            master.frame_main.destroy()
            master.root.width = 600
            master.root.height = 150
            master.x = (int(master.root.screenwidth) - master.root.width) / 2
            master.y = (int(master.root.screenheight)- master.root.height) / 3
            master.root.geometry("%dx%d+%d+%d" % (master.root.width, master.root.height, master.x, master.y))
            master.root.resizable(True, True)
            self.instantiate_frames(master)
            self.stack_frames = []
            self.stack_frames.append(self.frame_main)



            ''' XNAT ADDRESS '''

            self.label_address = tk.Label(
                self.frame_upload_labels, text="  XNAT web address  ", anchor="w"
            )
            self.label_address.grid(row=0, column=0, padx=1, ipadx=1)
            self.entry_address = tk.Entry(self.frame_upload_labels)
            self.entry_address.var = tk.StringVar()
            self.entry_address["textvariable"] = self.entry_address.var
            self.entry_address.var.trace_add("write", self.enable_connect_button)
            self.entry_address.grid(row=0, column=1)

            ''' XNAT USER '''
            self.label_user = tk.Label(
                self.frame_upload_labels, text="Username", anchor="w"
            )
            self.label_user.grid(row=1, column=0, padx=1)
            self.entry_user = tk.Entry(self.frame_upload_labels)
            self.entry_user.grid(row=1, column=1)
            self.entry_user.var = tk.StringVar()
            self.entry_user["textvariable"] = self.entry_user.var
            self.entry_user.var.trace_add("write", self.enable_connect_button)

            ''' XNAT PASSWORD '''

            self.label_psw = tk.Label(self.frame_upload_labels, text="Password", anchor="w")
            self.label_psw.grid(row=2, column=0, padx=1)
            self.entry_psw = tk.Entry(self.frame_upload_labels, show="*")
            self.entry_psw.grid(row=2, column=1)
            self.entry_psw.var = tk.StringVar()
            self.entry_psw["textvariable"] = self.entry_psw.var
            self.entry_psw.var.trace_add("write", self.enable_connect_button)

            ''' XNAT HTTP/HTTPS '''
            self.http = tk.StringVar()
            self.http.trace_add("write", self.enable_connect_button)

            ''' SAVE CREDENTIALS CHECKBOX '''
            self.remember = tk.IntVar()


            # BUTTONS
            self.button_connect = tk.Button(
                self.frame_upload_button,
                text="Login",
                state="disabled",
                command=partial(self.check_connection,master)
            )
            self.button_connect.grid(row=4, column=5, sticky="SE")
            self.button_http = tk.Radiobutton(
                self.frame_upload_button,
                text=" http:// ",
                variable=self.http,
                value="http://",
            )
            self.button_http.grid(row=0, column=0)
            self.button_http.select()
            self.button_https = tk.Radiobutton(
                self.frame_upload_button,
                text=" https:// ",
                variable=self.http,
                value="https://",
            )
            self.button_https.grid(row=0, column=1)

            self.btn_remember = tk.Checkbutton(
                self.frame_upload_button, text="Remember me", variable=self.remember
            )
            self.btn_remember.grid(row=0, column=2)
            self.load_saved_credentials()
            ###

        def load_saved_credentials(self):

            # REMEMBER CREDENTIALS
            try:
                home = os.path.expanduser("~")
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                decrypted_file = os.path.join(
                    home, "Documents", ".XNAT_login_file00000.txt"
                )
                pyAesCrypt.decryptFile(encrypted_file, decrypted_file, password, bufferSize)
                login_file = open(decrypted_file, "r")
                line = login_file.readline()
                self.entry_address.var.set(line[8:-1])
                line = login_file.readline()
                self.entry_user.var.set(line[9:-1])
                line = login_file.readline()
                self.entry_psw.var.set(line[9:-1])
                login_file.close()
                os.remove(decrypted_file)
                self.btn_remember.select()
            except Exception as error:
                pass

        def instantiate_frames(self,master):

            # # FRAMES
            self.frame_main = tk.Frame(master.root)
            # self.frame_main.pack()
            self.frame_main.grid(row=0, column=0)
            # # LABELS
            self.frame_upload_labels = tk.Frame(self.frame_main)
            # self.frame_upload_labels.pack(side="left")
            self.frame_upload_labels.grid(row=0, column=0, sticky="W")
            self.frame_upload_button = tk.Frame(self.frame_main)
            # self.frame_upload_button.pack(side="bottom",ipady=15,ipadx=5)
            self.frame_upload_button.grid(row=3, column=0)
            self.frame_upload_entries = tk.Frame(self.frame_main)

        def check_connection(self,master):
            self.entry_address_complete = self.http.get() + self.entry_address.var.get()
            #

            home = os.path.expanduser("~")
            try:
                session = xnat.connect(
                    self.entry_address_complete,
                    self.entry_user.var.get(),
                    self.entry_psw.var.get(),
                )
                if self.remember.get() == True:
                    self.save_credentials()
                else:
                    try:
                        os.remove(
                            os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                        )
                    except FileNotFoundError:
                        pass
                self.xnat_dcm_uploader_select_project(session,master)
            except xnat.exceptions.XNATLoginFailedError as err:
                messagebox.showerror("Error!", err)
            except Exception as error:
                messagebox.showerror("Error!", error)

        def enable_connect_button(self, *_):
            if (
                self.entry_address.var.get()
                and self.entry_user.var.get()
                and self.entry_psw.var.get()
                and self.http.get()
            ):
                self.button_connect["state"] = "normal"
            else:
                self.button_connect["state"] = "disabled"

        def save_credentials(self):

            home = os.path.expanduser("~")

            if os.path.exists(os.path.join(home, "Documents")):
                file = os.path.join(home, "Documents", ".XNAT_login_file.txt")
                login_file = open(file, "w+")
                login_file.write(
                    "Address:"
                    + self.entry_address.var.get()
                    + "\n"
                    + "Username:"
                    + self.entry_user.var.get()
                    + "\n"
                    + "Password:"
                    + self.entry_psw.var.get()
                    + "\n"
                    + "HTTP:"
                    + self.http.get()
                )
                login_file.close()
                # encrypt
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                pyAesCrypt.encryptFile(file, encrypted_file, password, bufferSize)
                # decrypt
                os.remove(file)

            # elif platform.system()=='Windows':
            #   login_file=open("/XNAT_login_file", "w+")
            #   login_file.write("Address:"+self.entry_address.var.get()+'\n'+"Username:"+self.entry_user.var.get()+'\n'+"Password:"+self.entry_psw.var.get()+'\n'+"HTTP:"+self.http.get())
            #   login_file.close()

        def enable_project_entry(self, *_):
            if self.newprj_var.get() == 1:
                self.entry_prjname["state"] = "normal"
                self.project_list["state"] = "disabled"
                self.label_prjname["state"] = "normal"
                self.label_choose_prj["state"] = "disabled"

            else:
                self.entry_prjname["state"] = "disabled"
                self.label_prjname["state"] = "disabled"
                self.project_list["state"] = "normal"
                self.label_choose_prj["state"] = "normal"

        def enable_next(self, *_):
            # # EXISTING PROJECT
            if self.newprj_var.get() == 0:
                if self.prj.get() in self.OPTIONS:
                    self.button_next["state"] = "normal"
                else:
                    self.button_next["state"] = "disabled"

            # # NEW PROJECT
            else:
                if self.entry_prjname.var.get():
                    self.button_next["state"] = "normal"
                else:
                    self.button_next["state"] = "disabled"

        def check_project_name(self,master):
            if self.entry_prjname.var.get().lower in self.OPTIONS:
                messagebox.showerror(
                    "Error!",
                    "Project ID %s already exists! Please, enter a different project ID"
                    % self.entry_prjname.var.get(),
                )
            else:
                self.xnat_dcm_uploader_select_custom_vars(master)

        def xnat_dcm_uploader_select_project(self,session,master):

            # # FRAME
            self.stack_frames[-1].grid_remove()
            self.frame_two = tk.Frame(master.root)
            # self.frame_two.pack(side="left")
            self.frame_two.grid()
            self.stack_frames.append(self.frame_two)

            master.root.width = 600
            master.root.height = 150
            master.x = (int(master.root.screenwidth) - master.root.width) / 2
            master.y = (int(master.root.screenheight)- master.root.height) / 3
            master.root.geometry("%dx%d+%d+%d" % (master.root.width, master.root.height, master.x, master.y))

            # # LABEL
            self.label_prjname = tk.Label(
                self.frame_two, text="  New project    ", anchor="w", state="disabled"
            )
            self.label_choose_prj = tk.Label(
                self.frame_two, text="  Select project in XNAT  ", anchor="w"
            )
            self.label_choose_prj.grid(row=2, column=0)
            self.label_prjname.grid(row=0, column=0, sticky="W", columnspan=1)
            # # ENTRY INSERT NEW PROJECT
            self.value = tk.StringVar()
            self.entry_prjname = tk.Entry(self.frame_two, state="disabled")
            self.value.set("  Project ID  ")
            self.entry_prjname.grid(row=0, column=1)
            self.entry_prjname.var = tk.StringVar()
            self.entry_prjname.var.set("  Project ID  ")
            self.entry_prjname["textvariable"] = self.entry_prjname.var

            # PROJECTS LIST

            self.OPTIONS = session.projects

            self.prj = tk.StringVar()
            self.project_list = tk.OptionMenu(self.frame_two, self.prj, *self.OPTIONS)
            self.project_list.grid(row=2, column=1)
            self.newprj_var = tk.IntVar()
            self.btn_newprj = tk.Checkbutton(self.frame_two, variable=self.newprj_var)
            self.btn_newprj.grid(row=0, column=0)
            self.newprj_var.trace_add("write", self.enable_project_entry)

            self.button_prev = tk.Button(
                self.frame_two, text="Back", command=partial(self.navigate_back,master)
            )
            self.button_prev.grid(row=4, column=0)
            self.button_next = tk.Button(
                self.frame_two, text="Next", command=partial(self.check_project_name,master), state="disabled"
            )
            self.button_next.grid(row=4, column=2)
            # TRACE PROJECT INSERTION

            self.newprj_var.trace_add("write", self.enable_next)
            self.entry_prjname.var.trace_add("write", self.enable_next)
            self.prj.trace_add("write", self.enable_next)

            session.disconnect()


        def navigate_back(self,master):
            self.stack_frames[-1].grid_remove()
            self.stack_frames.pop()
            self.stack_frames[-1].grid()

        def xnat_dcm_uploader_select_custom_vars(self,master):
            if self.newprj_var.get() == 1:
                self.project = self.entry_prjname.var.get()
            else:
                self.project = self.prj.get()

            self.stack_frames[-1].grid_remove()
            master.root.withdraw()

            self.folder_to_upload = filedialog.askdirectory(
                parent=master.root,
                initialdir=self.home,
                title="Please select project directory (DICOM only)",
            )
            if self.folder_to_upload==():
                os._exit(1)
            master.root.deiconify()
            head, tail = os.path.split(self.folder_to_upload)
            project_foldername = tail
            dst = os.path.join(head, project_foldername)
            project_id = self.project
            ##############
            self.frame_three = tk.Frame(master.root)
            self.stack_frames.append(self.frame_three)
            self.stack_frames[-1].grid()

            self.label_descr = tk.Label(
                self.frame_three,
                text="   Enter the number of custom variables \n(from 0 to 3)   ",
                anchor="w",
                state="normal",
            )
            # self.label_descr.pack(side="top",anchor="w")
            self.label_descr.grid(row=0, column=0)
            self.label_num_vars = tk.Entry(self.frame_three)
            # self.label_num_vars.pack()
            self.label_num_vars.grid(row=1, column=0)
            self.label_num_vars.var = tk.StringVar()
            self.label_num_vars["textvariable"] = self.label_num_vars.var
            self.label_num_vars.var.trace_add("write", self.enable_cust_vars_button)

            self.btn_add = tk.Button(
                self.frame_three,
                text="List Custom Variables",
                command=self.display_cust_vars_list,
                state="disabled",
            )
            # self.btn_add.pack(side="right")
            self.btn_add.grid(row=1, column=1)
            self.btn_next = tk.Button(
                self.frame_three, text="Next", command=partial(self.dicom2xnat,master)
            )
            # self.btn_next.pack(side="bottom")
            self.btn_next.grid(row=3, column=1)

            self.button_prev = tk.Button(
                self.frame_three, text="Back", command=partial(self.navigate_back,master)
            )
            # self.button_prev.pack(side="left")
            self.button_prev.grid(row=3, column=0)

        #        self.list_cust_vars=[]
        def display_cust_vars_list(self):
            try:
                self.frame_cst_vars.destroy()
            except:
                pass
            self.frame_cst_vars = tk.Frame(self.frame_three)
            self.frame_cst_vars_values = tk.Frame(self.frame_three)
            self.cust_vars, self.cust_vars_values = list_cust_vars(self.folder_to_upload)
            # self.folder_list=tk.OptionMenu(self.frame_three,self.folder,*(self.folders))
            # self.frame_cst_vars.pack(side="left")
            j = 2
            self.frame_cst_vars.grid(row=j, column=0)
            # self.frame_cst_vars_values.pack(side="right")
            self.frame_cst_vars_values.grid(row=j, column=1)
            # self.cust_vars=self.cust_vars[::-1]
            tk.Label(
                self.frame_cst_vars, text="Custom Variables", relief="raised", borderwidth=2
            ).grid(row=j, column=0)
            tk.Label(
                self.frame_cst_vars,
                text="Values",
                relief="raised",
                borderwidth=2,
            ).grid(row=j, column=1)
            for i in range(0, int(self.label_num_vars.get())):
                tk.Label(self.frame_cst_vars, text=self.cust_vars[i], borderwidth=2).grid(
                    row=j + i + 1, column=0
                )
                tk.Label(
                    self.frame_cst_vars, text=self.cust_vars_values[i], borderwidth=2
                ).grid(row=j + i + 1, column=1)

        def enable_cust_vars_button(self, *_):

            try:
                if re.match("^[0123]$", str(self.label_num_vars.var.get())):
                    self.btn_add["state"] = "normal"
                else:
                    self.btn_add["state"] = "disabled"
            except:
                pass

        def dicom2xnat(self,master):

            self.stack_frames[-1].grid_remove()
            if (not self.label_num_vars.var.get()):
                self.label_num_vars.var="0"
                num_vars = int(self.label_num_vars.var)
            else:
                num_vars = int(self.label_num_vars.get())
            master._inprogress("Upload in progress")
            xnat_uploader(
                self.folder_to_upload,
                self.project,
                num_vars,
                self.entry_address_complete,
                self.entry_user.var.get(),
                self.entry_psw.var.get(),
            )

            master.progress.stop()
            os._exit(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = xnat_pic_gui(root)
    root.mainloop()
