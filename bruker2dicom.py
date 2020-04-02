#!/home/xnat/anaconda3/envs/py3/bin/python3.7
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 14:05:21 2018

@author: Sara Zullino
"""

import os, re
import numpy as np
import datetime
import dateutil.parser
from pydicom.dataset import Dataset, FileDataset
import pydicom.uid
from read_visupars import read_visupars_parameters
from cest_dict import add_cest_dict
from read_method import read_method_parameters

try:
    import tkinter as tk  # python v3
    from tkinter import messagebox

except ImportError:
    import Tkinter as tk  # python v2
    from Tkinter import *


def bruker2dicom(folder_to_convert, master):

    # Tag entries for cest acquisition
    add_cest_dict()

    a = "1"
    c = "visu_pars"
    d = "2dseq"
    e = "method"
    f = "acqp"
    g = "reco"
    res = []
    parameters = 0

    for root, dirs, files in sorted(os.walk(folder_to_convert, topdown=True)):
        for dir in dirs:
            res = os.path.join(root)
            dirs[:] = []  # Don't recurse any deeper
            visu_pars_file = os.path.abspath(os.path.join(res, a, c))
            dseq_file = os.path.abspath(os.path.join(res, a, d))
            reco_file = os.path.abspath(os.path.join(res, a, g))
            method_file = os.path.abspath(os.path.join(os.path.dirname(res), e))
            acqp_file = os.path.abspath(os.path.join(os.path.dirname(res), f))
            if os.path.exists(dseq_file):
                with open(visu_pars_file, "r"):
                    parameters = read_visupars_parameters(visu_pars_file)
                with open(reco_file, "r"):
                    reco_parameters = read_method_parameters(reco_file)
                with open(method_file, "r"):
                    method_parameters = read_method_parameters(method_file)
                with open(acqp_file, "r"):
                    acqp_parameters = read_visupars_parameters(acqp_file)
            else:
                break
            filename_little_endian = "MRIm"

            img_type = parameters.get("VisuCoreWordType")
            img_endianness = parameters.get("VisuCoreByteOrder")
            img_frames = parameters.get("VisuCoreFrameCount")
            img_dims = parameters.get("VisuCoreSize")
            core_ext = parameters.get("VisuCoreExtent")

            slope = parameters.get("VisuCoreDataSlope")
            intercept = parameters.get("VisuCoreDataOffs")

            # Check endianness and precision
            if img_type == "_32BIT_SGN_INT" and img_endianness == "littleEndian":
                data_precision = np.dtype("<i4")
            elif img_type == "_32BIT_SGN_INT" and img_endianness == "bigEndian":
                data_precision = np.dtype(">i4")
            elif img_type == "_16BIT_SGN_INT" and img_endianness == "littleEndian":
                data_precision = np.dtype("<i2")
            elif img_type == "_16BIT_SGN_INT" and img_endianness == "bigEndian":
                data_precision = np.dtype(">i2")
            else:
                messagebox.showerror(
                    "Error!", "Image data precision is neither 16 nor 32 bit!"
                )
                os._exit(0)
                
            raw_data = open(dseq_file, "rb")
            img_data_precision = np.fromfile(raw_data, dtype=data_precision)
            raw_data.close()

            head2, _ = os.path.split(res)
            os.chdir(head2)

            if img_type == "_16BIT_SGN_INT" and img_endianness == "littleEndian":

                # img = np.array(img_data_precision,np.uint16)

                if np.size(slope) == 1:
                    img_data_corrected = img_data_precision * slope
                    img_data_corrected += intercept
                else:
                    img_data_corrected = img_data_precision * slope[0]
                    img_data_corrected += intercept[0]

                factor = ((2 ** 16) - 1) / (np.amax(img_data_corrected))

                img_float = img_data_corrected * factor

                img = np.array(img_float, np.uint16)

            # if 32 bit, slope and intercept correction
            elif img_type == "_32BIT_SGN_INT" and img_endianness == "littleEndian":

                if np.size(slope) == 1:
                    img_data_corrected = img_data_precision * slope
                    img_data_corrected += intercept
                else:
                    img_data_corrected = img_data_precision * slope[0]
                    img_data_corrected += intercept[0]

                factor = ((2 ** 16) - 1) / (np.amax(img_data_corrected))

                img_float = img_data_corrected * factor

                img = np.array(img_float, np.uint16)

            else:
                messagebox.showerror(
                    "Error!",
                    "The image you are trying to convert is neither 16 bit nor 32 bit!",
                )
                os._exit(0)
            # Populate required values for file meta information

            file_meta = Dataset()
            file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
            file_meta.MediaStorageSOPInstanceUID = parameters.get("VisuUid")
            file_meta.ImplementationClassUID = "1.2.276.0.7230010.3.0.3.5.3"
            file_meta.ImplementationVersionName = 'OFFIS_DCMTK_353'

            # Create the FileDataset instance (initially no data elements, but file_meta supplied)
            ds = FileDataset(filename_little_endian, {}, file_meta=file_meta, preamble=b"\0" * 128)
            ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

            # Add the data elements --  Check DICOM standard
            ds.ImageType = ["ORIGINAL", "PRIMARY", "OTHER"]

            # if ('treated' in root):
            #    appendix='treated'
            # elif ('untreated' in root):
            #    appendix='untreated'

            # patient_type=re.findall('/[^/]*trea[^/]*/[^/]*/',root)
            # if len(patient_type)!=0:
            #    group=patient_type[0].split('/')[1]
            #    timepoint=patient_type[0].split('/')[2]
            #    ds.PatientName = parameters.get("VisuSubjectName")+'_'+group+'_'+timepoint
            # else:
            #    ds.PatientName= parameters.get("VisuSubjectName")

            ds.PatientName = parameters.get("VisuSubjectName")
            # head_ID, tail_ID = os.path.split(head2)
            head_ID, _ = os.path.split(head2)
            ds.PatientID = parameters.get("VisuSubjectId")
            ds.PatientSex = parameters.get("VisuSubjectSex")
            ds.PatientWeight = parameters.get("VisuSubjectWeight")
            ds.BirthDate = parameters.get("VisuSubjectBirthDate")
            ds.ReferringPhysicianName = parameters.get("VisuStudyReferringPhysician")
            if parameters.get("VisuCreatorVersion") == "5.1":
                studydate = parameters.get("VisuStudyDate").date()
                studytime = parameters.get("VisuStudyDate").time()
                ds.StudyDate = studydate.strftime("%Y%m%d")
                ds.StudyTime = studytime.strftime("%H%M%S")
                acquisitiondate = parameters.get("VisuAcqDate").date()
                acquisitiontime = parameters.get("VisuAcqDate").time()
                ds.AcquisitionDate = acquisitiondate.strftime("%Y%m%d")
                ds.AcquisitionTime = acquisitiontime.strftime("%H%M%S")
                VisuAcqImagePhaseEncDir = parameters.get("VisuAcqImagePhaseEncDir")
                if np.size(VisuAcqImagePhaseEncDir) == 1:
                    ds.InPlanePhaseEncodingDirection = parameters.get("VisuAcqImagePhaseEncDir").split("_")[0]
                else:
                    ds.InPlanePhaseEncodingDirection = parameters.get("VisuAcqImagePhaseEncDir")[0].split("_")[0]
                if ds.InPlanePhaseEncodingDirection == "row":
                    acqmat = np.pad(parameters.get("VisuAcqSize"), 1, "constant")
                    ds.AcquisitionMatrix = list(np.array(acqmat, dtype=int))
                elif ds.InPlanePhaseEncodingDirection == "col":
                    acqmat = np.insert(parameters.get("VisuAcqSize"), 1, [0, 0])
                    ds.AcquisitionMatrix = list(np.array(acqmat, dtype=int))
            else:
                s = parameters.get("VisuStudyDate")
                date = re.sub("\ |\<|\>", "", s)
                studydate = dateutil.parser.parse(date)
                ds.StudyDate = studydate.strftime("%Y%m%d")
                ds.StudyTime = studydate.strftime("%H%M%S")
                t = parameters.get("VisuAcqDate")
                acqdate = re.sub("\ |\<|\>", "", t)
                acquisitiondate = dateutil.parser.parse(acqdate)
                ds.AcquisitionDate = acquisitiondate.strftime("%Y%m%d")
                ds.AcquisitionTime = acquisitiondate.strftime("%H%M%S")
            ds.Modality = str("MR")
            ds.ScanningSequence = str("RM")
            ds.SequenceVariant = str("None")
            sequencename = " ".join(parameters.get("VisuAcqSequenceName")).split("_")
            ds.SequenceName = " ".join(sequencename)
            if "_" in parameters.get("VisuAcquisitionProtocol"):
                protocol = parameters.get("VisuAcquisitionProtocol").split("_")
                ds.ProtocolName = " ".join(protocol)
                ds.SeriesDescription = " ".join(protocol)
            elif "-" in parameters.get("VisuAcquisitionProtocol"):
                protocol = parameters.get("VisuAcquisitionProtocol").split("-")
                ds.ProtocolName = " ".join(protocol)
                ds.SeriesDescription = " ".join(protocol)
            else:
                ds.ProtocolName = " ".join(parameters.get("VisuAcquisitionProtocol"))
                ds.SeriesDescription = " ".join(parameters.get("VisuAcquisitionProtocol"))

            if np.size(parameters.get("VisuAcqRepetitionTime")) > 1:
                ds.RepetitionTime = list(parameters.get("VisuAcqRepetitionTime"))
            else:
                ds.RepetitionTime = parameters.get("VisuAcqRepetitionTime")
            if np.size(parameters.get("VisuAcqEchoTime")) > 1:
                ds.EchoTime = list(parameters.get("VisuAcqEchoTime"))
            else:
                ds.EchoTime = parameters.get("VisuAcqEchoTime")           
            ds.AcquisitionDuration=parameters.get("VisuAcqScanTime")   
            ds.NumberOfAverages = parameters.get("VisuAcqNumberOfAverages")
            ds.ImagingFrequency = parameters.get("VisuAcqImagingFrequency")
            ds.ImagedNucleus = parameters.get("VisuAcqImagedNucleus")
            ds.NumberOfPhaseEncodingSteps = parameters.get("VisuAcqPhaseEncSteps")
            ds.EchoTrainLength = parameters.get("VisuAcqEchoTrainLength")
            ds.EchoTraiLength = parameters.get("VisuAcqEchoTrainLength")
            ds.PixelBandwidth = parameters.get("VisuAcqPixelBandwidth")
            ds.FlipAngle = parameters.get("VisuAcqFlipAngle")
            ds.PatientPosition = parameters.get("VisuSubjectPosition")
            ds.PatientOrientation = method_parameters.get("PVM_SPackArrReadOrient")[0][1:]
            ds.StudyID = parameters.get("VisuStudyId")
            institution = parameters.get("VisuInstitution")
            ds.InstitutionName = " ".join(institution)
            ds.Manufacturer = parameters.get("ORIGIN")
            ds.SeriesInstanceUID = parameters.get("VisuUid")
            ds.FrameOfReferenceUID = parameters.get("VisuUid") + '.6.15.18'
            ds.SOPInstanceUID = parameters.get("VisuUid")
            ds.StudyInstanceUID = parameters.get("VisuStudyUid")
            ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
            ds.StationName = parameters.get("VisuStation")
            ds.AcquisitionNumber = "1"
            ds.InstanceNumber = "1"
            ds.MRAcquisitionType = str(parameters.get("VisuCoreDim")) + "D"
            ds.SoftwareVersions = (str(parameters.get("VisuCreator")) + " " + \
                                   str(parameters.get("VisuCreatorVersion")))
            ds.ImagePositionPatient = list(map(str, parameters.get("VisuCorePosition")[0]))
            ds.ImageOrientationPatient = list(map(str, parameters.get("VisuCoreOrientation")[0][0:6]))
            ds.SliceLocation = list(map(str, parameters.get("VisuCorePosition")[0]))[2]
            ds.SliceThickness = parameters.get("VisuCoreFrameThickness")
            ds.ImagesInAcquisition = parameters.get("VisuCoreFrameCount")
            ds.NumberOfFrames = parameters.get("VisuCoreFrameCount")
            nframes = parameters.get("VisuCoreFrameCount")

            gamma = 42.5756
            Bo = round(ds.ImagingFrequency / gamma)
            ds.MagneticFieldStrength = Bo

            # Image pixel module with the tags starting with 0028.
            # This group is responsible for describing how to read the pixels
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"
            ds.PixelRepresentation = 0  # unsigned (0)
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.Columns = int(img_dims[0])
            ds.Rows = int(img_dims[1])
            ds.PixelSpacing = [core_ext[0]/img_dims[0], core_ext[1]/img_dims[1]]
            ds.WindowCenterWidthExplanation = "MinMax"
            # PixelData contains the raw bytes exactly as found in the file
            ds.PixelData = img.tobytes()
            ds[0x7FE0, 0x0010].VR = "OW"
            # The dicom_dict entry for LargestImagePixelValue uses an ambiguous VR (Value Representation).
            # It can either be an unsigned short integer (US) or a signed short integer (SS).
            # In order to properly write the data to the file,
            # you have to explicitly tell it which one you want to use.
            ds.WindowWidth = int(np.amax(img) + 1)
            ds.WindowCenter = int((np.amax(img) + 1) / 2)
            ds[0x0028, 0x1050].VR = "DS"
            ds[0x0028, 0x1051].VR = "DS"
            ds.SmallestImagePixelValue = int(np.amin(ds.pixel_array))
            ds.LargestImagePixelValue = int(np.amax(ds.pixel_array))
            ds[0x0028, 0x0106].VR = "US"
            ds[0x0028, 0x0107].VR = "US"

            # Set creation date/time
            dt = datetime.datetime.now()
            ds.InstanceCreationDate = dt.strftime("%Y%m%d")
            timeStr = dt.strftime("%H%M%S")
            ds.InstanceCreationTime = timeStr

            ds.NumberOfSlices = acqp_parameters.get("NSLICES")

            # Write dicom in separate slices only if number of slices is greater than 1
            if nframes == 1:
                head2, _ = os.path.split(res)
                _, tail3 = os.path.split(head2)
                ds.SeriesNumber = tail3
                ds.RescaleSlope = factor
                ds.RescaleIntercept = str(np.array(intercept, dtype=float))
                os.chdir(head2)
                outfile = "%s%s.dcm" % (filename_little_endian, str(1))
                ds.is_little_endian = True
                ds.is_implicit_VR = False
                ds.save_as(outfile)

            else:
                count = 1
                k = 0
                ii = 0
                for layer in ds.pixel_array:

                    layer = np.reshape(layer, int(img_dims[0]) * int(img_dims[1]))

                    # Populate required values for file meta information
                    file_meta_temp = Dataset()
                    file_meta_temp.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
                    file_meta_temp.MediaStorageSOPInstanceUID = parameters.get("VisuUid") + ".%s" % (k)
                    file_meta_temp.ImplementationClassUID = "1.2.276.0.7230010.3.0.3.5.3"
                    file_meta_temp.ImplementationVersionName = 'OFFIS_DCMTK_353'

                    # Create the FileDataset instance (initially no data elements, but file_meta supplied)
                    ds_temp = FileDataset(filename_little_endian, {}, file_meta=file_meta_temp, \
                                          preamble=b"\0" * 128)

                    ds_temp.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

                    # Add the data elements --  Check DICOM standard
                    ds_temp.ImageType = ["ORIGINAL", "PRIMARY", "OTHER"]

                    # patient_type=re.findall('/[^/]*trea[^/]*/[^/]*/',root)
                    # if len(patient_type)!=0:
                    #    group=patient_type[0].split('/')[1]
                    #    timepoint=patient_type[0].split('/')[2]
                    #    ds.PatientName = parameters.get("VisuSubjectName")+'_'+group+'_'+timepoint
                    # else:
                    # ds.PatientName= parameters.get("VisuSubjectName")
                    ds_temp.PatientName = parameters.get("VisuSubjectName")
                    ds_temp.PatientID = parameters.get("VisuSubjectId")
                    ds_temp.PatientSex = parameters.get("VisuSubjectSex")
                    ds_temp.PatientWeight = parameters.get("VisuSubjectWeight")
                    ds_temp.BirthDate = parameters.get("VisuSubjectBirthDate")
                    ds_temp.ReferringPhysiciansName = parameters.get("VisuStudyReferringPhysician")
                    if parameters.get("VisuCreatorVersion") == "5.1":
                        studydate = parameters.get("VisuStudyDate").date()
                        studytime = parameters.get("VisuStudyDate").time()
                        ds_temp.StudyDate = studydate.strftime("%Y%m%d")
                        ds_temp.StudyTime = studytime.strftime("%H%M%S")
                        acquisitiondate = parameters.get("VisuAcqDate").date()
                        acquisitiontime = parameters.get("VisuAcqDate").time()
                        ds_temp.AcquisitionDate = acquisitiondate.strftime("%Y%m%d")
                        ds_temp.AcquisitionTime = acquisitiontime.strftime("%H%M%S")
                        ds_temp.InPlanePhaseEncodingDirection = parameters.get("VisuAcqImagePhaseEncDir")[0].split("_")[0]
                        ds_temp.Columns = int(img_dims[0])
                        ds_temp.Rows = int(img_dims[1])
                        if ds_temp.InPlanePhaseEncodingDirection == "row":  # check pixel spacing
                            acqmat = np.pad(parameters.get("VisuAcqSize"), 1, "constant")
                            ds_temp.AcquisitionMatrix = list(np.array(acqmat, dtype=int))
                            ds_temp.PixelSpacing = [core_ext[0] / img_dims[0], core_ext[1] / img_dims[1]]
                            pixel_spacing = [
                                core_ext[0] / img_dims[0],
                                core_ext[1] / img_dims[1],
                            ]
                            ds_temp.PixelSpacing = pixel_spacing[::-1]
                        elif ds_temp.InPlanePhaseEncodingDirection == "col":
                            acqmat = np.insert(parameters.get("VisuAcqSize"), 1, [0, 0])
                            ds_temp.AcquisitionMatrix = list(np.flip(np.array(acqmat, dtype=int), 0))
                            ds_temp.PixelSpacing = [
                                core_ext[1] / img_dims[1],
                                core_ext[0] / img_dims[0],
                            ]
                    elif parameters.get("VisuCreatorVersion") == "6.0.1":

                        s = parameters.get("VisuStudyDate")
                        date = re.sub("\ |\<|\>", "", s)
                        studydate = dateutil.parser.parse(date)
                        ds_temp.StudyDate = studydate.strftime("%Y%m%d")
                        ds_temp.StudyTime = studydate.strftime("%H%M%S")
                        t = parameters.get("VisuAcqDate")
                        acqdate = re.sub("\ |\<|\>", "", t)
                        acquisitiondate = dateutil.parser.parse(acqdate)
                        ds_temp.AcquisitionDate = acquisitiondate.strftime("%Y%m%d")
                        ds_temp.AcquisitionTime = acquisitiondate.strftime("%H%M%S")
                        ds_temp.InPlanePhaseEncodingDirection = parameters.get("VisuAcqGradEncoding")
                        if parameters.get("VisuAcqGradEncoding")[0] == "read_enc":
                            ds_temp.Columns = int(img_dims[0])
                            ds_temp.Rows = int(img_dims[1])
                            acqmat = np.pad(parameters.get("VisuAcqSize"), 1, "constant")
                            ds_temp.AcquisitionMatrix = list(np.array(acqmat, dtype=int))
                            ds_temp.PixelSpacing = [
                                core_ext[1] / img_dims[1],
                                core_ext[0] / img_dims[0],
                            ]
                        elif parameters.get("VisuAcqGradEncoding")[0] == "phase_enc":
                            ds_temp.Columns = int(img_dims[1])
                            ds_temp.Rows = int(img_dims[0])
                            acqmat = np.insert(parameters.get("VisuAcqSize"), 1, [0, 0])
                            ds_temp.AcquisitionMatrix = list(np.flip(np.array(acqmat, dtype=int), 0))  # check
                            ds_temp.PixelSpacing = [
                                core_ext[0] / img_dims[0],
                                core_ext[1] / img_dims[1],
                            ]

                    ds_temp.StudyID = parameters.get("VisuStudyId")
                    ds_temp.SeriesNumber = os.path.basename(head2)
                    ds_temp.Modality = str("MR")
                    ds_temp.ScanningSequence = str("RM")
                    ds_temp.SequenceVariant = str("None")
                    sequencename = " ".join(parameters.get("VisuAcqSequenceName")).split("_")
                    ds_temp.SequenceName = " ".join(sequencename)
                    if "_" in parameters.get("VisuAcquisitionProtocol"):
                        protocol = parameters.get("VisuAcquisitionProtocol").split("_")
                        ds_temp.ProtocolName = " ".join(protocol)
                        ds_temp.SeriesDescription = " ".join(protocol)
                    elif "-" in parameters.get("VisuAcquisitionProtocol"):
                        protocol = parameters.get("VisuAcquisitionProtocol").split("-")
                        ds_temp.ProtocolName = " ".join(protocol)
                        ds_temp.SeriesDescription = " ".join(protocol)
                    else:
                        ds_temp.ProtocolName = " ".join(parameters.get("VisuAcquisitionProtocol"))
                        ds_temp.SeriesDescription = " ".join(parameters.get("VisuAcquisitionProtocol"))
                   
                    if np.size(parameters.get("VisuAcqRepetitionTime"))>1 and np.size(parameters.get("VisuAcqRepetitionTime"))==nframes:
                            ds_temp.RepetitionTime=str(np.array(parameters.get("VisuAcqRepetitionTime"),dtype=int)[k]) 
                    elif np.size(parameters.get("VisuAcqRepetitionTime"))>1 and np.size(parameters.get("VisuAcqRepetitionTime"))!=nframes:
                        r_step =  int(nframes/np.size(parameters.get("VisuAcqRepetitionTime")))
                        repetition_time = []
                        for t in range(0,np.size(parameters.get("VisuAcqRepetitionTime"))):
                            for kk in range(0,r_step):
                                    repetition_time.append(parameters.get("VisuAcqRepetitionTime")[t])  
                        ds_temp.RepetitionTime=str(np.array(repetition_time,dtype=float)[k])                           
                    else:
                        ds_temp.RepetitionTime=parameters.get("VisuAcqRepetitionTime")  
                            
                    if np.size(parameters.get("VisuAcqEchoTime"))>1 and np.size(parameters.get("VisuAcqEchoTime"))==nframes:
                        ds_temp.EchoTime=str(np.array(parameters.get("VisuAcqEchoTime"),dtype=float)[k])
                    elif np.size(parameters.get("VisuAcqEchoTime"))>1 and np.size(parameters.get("VisuAcqEchoTime"))!=nframes:
                        e_step =  int(nframes/np.size(parameters.get("VisuAcqEchoTime")))
                        echo_time = []
                        for t in range(0,np.size(parameters.get("VisuAcqEchoTime"))):
                            for kk in range(0,e_step):
                                echo_time.append(parameters.get("VisuAcqEchoTime")[t])  
                        ds_temp.EchoTime=str(np.array(echo_time,dtype=float)[k])                           
                    else:
                        ds_temp.EchoTime=parameters.get("VisuAcqEchoTime") 

                    ds_temp.AcquisitionDuration=parameters.get("VisuAcqScanTime") 
                    ds_temp.NumberOfAverages = str(parameters.get("VisuAcqNumberOfAverages"))
                    ds_temp.ImagingFrequency = parameters.get("VisuAcqImagingFrequency")
                    ds_temp.ImagedNucleus = parameters.get("VisuAcqImagedNucleus")
#                    z1 = parameters.get("VisuCorePosition")[0]
#                    z2 = parameters.get("VisuCorePosition")[1]
#                    spacing = abs(z1)-abs(z2)
#                    ds_temp.SpacingBetweenSlices = round(spacing[2],1)
                    ds_temp.NumberOfPhaseEncodingSteps = parameters.get("VisuAcqPhaseEncSteps")
                    ds_temp.EchoTrainLength = parameters.get("VisuAcqEchoTrainLength")
                    ds_temp.EchoTraiLength = parameters.get("VisuAcqEchoTrainLength")
                    ds_temp.PixelBandwidth = parameters.get("VisuAcqPixelBandwidth")
                    ds_temp.FlipAngle = str(parameters.get("VisuAcqFlipAngle"))
                    ds_temp.PatientPosition = parameters.get("VisuSubjectPosition")
                    ds_temp.PatientOrientation = method_parameters.get(
                        "PVM_SPackArrReadOrient"
                    )[0][1:]
                    ds_temp.StationName = parameters.get("VisuStation")
                    ds_temp.InstitutionName = " ".join(
                        parameters.get("VisuInstitution")
                    )
                    ds_temp.Manufacturer = parameters.get("ORIGIN")
                    ds_temp.SeriesInstanceUID = parameters.get("VisuUid")
                    ds_temp.FrameOfReferenceUID = parameters.get("VisuUid") + '.6.15.18'
                    ds_temp.StudyInstanceUID = parameters.get("VisuStudyUid")
                    ds_temp.SOPInstanceUID = parameters.get("VisuUid") + ".%s" % (k)
                    ds_temp.SOPClassUID = "1.2.840.10008.5.1.4.1.1.4"
                    ds_temp.AcquisitionNumber = count
                    ds_temp.InstanceNumber = count
                    ds_temp.MRAcquisitionType = str(parameters.get("VisuCoreDim")) + "D"
                    ds_temp.SoftwareVersions = str(parameters.get("VisuCreator")) + " " + str(parameters.get("VisuCreatorVersion"))
                    ds_temp.PercentPhaseFieldOfView = "100"
                    ds_temp.MagneticFieldStrength = Bo
                    if parameters.get("VisuCoreOrientation").shape[0] == 1:
                        ds_temp.ImagePositionPatient = list(map(str, parameters.get("VisuCorePosition")[0]))
                        ds_temp.ImageOrientationPatient = list(map(str, parameters.get("VisuCoreOrientation")[0][0:6]))
                        ds_temp.SliceThickness = parameters.get("VisuCoreFrameThickness")
                        ds_temp.NumberOfFrames = 1
                        ds_temp.ImagesInAcquisition = nframes
                        ds_temp.SliceLocation = parameters.get("VisuCorePosition")[0][2]
                    elif parameters.get("VisuCoreOrientation").shape[0] != nframes:
                        p = int(nframes / parameters.get("VisuCorePosition").shape[0])
                        visucoreposition = np.tile(parameters.get("VisuCorePosition"), (p, 1))
                        visucoreorientation = np.tile(parameters.get("VisuCoreOrientation"), (p, 1))
                        ds_temp.ImagePositionPatient = list(map(str, visucoreposition[ii]))
                        ds_temp.ImageOrientationPatient = list(map(str, visucoreorientation[ii][0:6]))
                        ds_temp.SliceThickness = parameters.get("VisuCoreFrameThickness")
                        ds_temp.NumberOfFrames = 1
                        ds_temp.ImagesInAcquisition = nframes
                        ds_temp.SliceLocation = list(map(str, visucoreposition[ii]))[2]
                    else:
                        ds_temp.ImagePositionPatient = list(map(str, parameters.get("VisuCorePosition")[k]))
                        ds_temp.ImageOrientationPatient = list(map(str, parameters.get("VisuCoreOrientation")[k][0:6]))
                        ds_temp.SliceThickness = parameters.get("VisuCoreFrameThickness")
                        ds_temp.NumberOfFrames = 1
                        ds_temp.ImagesInAcquisition = nframes
                        ds_temp.SliceLocation = list(map(str, parameters.get("VisuCorePosition")[k]))[2]

                    # Image pixel module with the tags starting with 0028.
                    # This group is responsible for describing how to read the pixels
                    ds_temp.SamplesPerPixel = 1
                    ds_temp.PhotometricInterpretation = "MONOCHROME2"
                    ds_temp.PixelRepresentation = 0
                    ds_temp.BitsAllocated = 16
                    ds_temp.BitsStored = 16
                    ds_temp.HighBit = 15
                    ds_temp.WindowCenterWidthExplanation = "MinMax"
                    ds_temp.PixelData = layer
                    ds_temp[0x7FE0, 0x0010].VR = "OW"
                    ds_temp.WindowWidth = int(np.amax(img) + 1)
                    ds_temp.WindowCenter = int((np.amax(img) + 1) / 2)
                    ds_temp[0x0028, 0x1050].VR = "DS"
                    ds_temp[0x0028, 0x1051].VR = "DS"
                    ds_temp.SmallestImagePixelValue = int(np.amin(layer))
                    ds_temp.LargestImagePixelValue = int(np.amax(layer))
                    ds_temp[0x0028, 0x0106].VR = "US"
                    ds_temp[0x0028, 0x0107].VR = "US"
                    ds_temp.RescaleSlope = factor
                    for j in range(0, nframes - 1):
                        ds_temp.RescaleIntercept = str(parameters.get("VisuCoreDataOffs")[j])

                    # Set creation date/time
                    dt = datetime.datetime.now()
                    ds_temp.InstanceCreationDate = dt.strftime("%Y%m%d")
                    timeStr = dt.strftime("%H%M%S")
                    ds_temp.InstanceCreationTime = timeStr

                    ds_temp.NumberOfSlices = acqp_parameters.get("NSLICES")

                    string2 = str(reco_parameters.get("RECO_fov"))
                    vect2 = re.findall("[0-9]+", string2)
                    vect2.pop(0)
                    vect3 = []
                    for elem in vect2:
                        vect3.append(float(elem))
                    ds_temp.ReconstructionFieldOfView = vect3

                    # DCE acquisition
                    if "mic flash DCE" in ds_temp.ProtocolName:
                        NRepetitions = method_parameters.get("PVM_NRepetitions")
                        enc_matrix = str(method_parameters.get("PVM_EncMatrix"))                            
                        enc_step = float(re.findall('[0-9]+',enc_matrix)[1])
                        total_scan_time = ds_temp.RepetitionTime * NRepetitions * enc_step
                        scan_time_step = int(ds_temp.RepetitionTime * enc_step) # in ms
                        vect4 = []
                        scan_time=0
                        step = int(nframes/NRepetitions)
                        for t in range(0,NRepetitions):
                            scan_time = scan_time + scan_time_step
                            for kk in range(0,step):
                                vect4.append(scan_time)                            
                        ds_temp.TriggerTime = np.array(vect4)[k]

                    # DWI acquisition
                    if "diffusion" in ds_temp.ProtocolName:
                        string = str(method_parameters.get("PVM_DwBvalEach"))
                        b_values = re.findall("[0-9]+", string)
                        b_values.pop(0)
                        b_values.insert(0, "0")
                        bvalues = []
                        for elem in b_values:
                            bvalues.append(float(elem))
                        vect3 = []
                        step = int(nframes / len(b_values))
                        for t in range(0, len(b_values)):
                            for kk in range(0, step):
                                vect3.append(bvalues[t])
                        ds_temp.DiffusionBValue = np.array(vect3)[k]

                        # overwrite corresponding tag got from visupars with new info?
                        # Numero esperimenti diffusione
                        # method_parameters.get("PVM_DwNDiffExp")

                    # CEST acquisition
                    # Add new tag entries for 7T
                    if ("cest" in ds_temp.ProtocolName and ds_temp.MagneticFieldStrength == 7
                        and method_parameters.get("PVM_MagTransOnOff") == "On"):  # or 'wasabi':
                        ds_temp.Creator = method_parameters.get("OWNER")
                        # MODIFICA 03 MAY:
                        # Added try catch to make it work with "method".
                        try:
                            ds_temp.ChemicalExchangeSaturationType = method_parameters.get("Method")
                        except:
                            ds_temp.ChemicalExchangeSaturationType = method_parameters.get("method")
                        ds_temp.SamplingType = "CEST"
                        if ds_temp.InstitutionName == "Bracco Imaging":
                            ds_temp.PulseShape = method_parameters.get("PVM_MagTransPulse1Enum")  # train
                            ds_temp.PulseLength = method_parameters.get("PVM_MagTransPulse1")[0]  # train
                        else:
                            ds_temp.PulseShape = method_parameters.get("PVM_MagTransPulseEnum")  # train
                            ds_temp.PulseLength = method_parameters.get("PVM_MagTransPulse")[0]
                        ds_temp.B1Saturation = method_parameters.get("PVM_MagTransPower")  # train
                        ds_temp.PulseNumber = method_parameters.get("PVM_MagTransPulsNumb")  # train
                        ds_temp.SaturationLength = ds_temp.PulseDuration * ds_temp.PulseNumber
                        if "train" in method_parameters.get("Method"):
                            tau_p = float(method_parameters.get("PVM_MagTransPulse")[0])
                            tau_d = float(method_parameters.get("PVM_MagTransInterDelay"))
                            n = int(method_parameters.get("PVM_MagTransPulsNumb"))
                            # method_parameters.get("PVM_MagTransModuleTime") #the result of this two lines should be the same
                            # magtransmoduletime = (tau_p + tau_d) * n
                            ds_temp.DutyCycle = tau_p / (tau_p + tau_d) * 100
                            ds_temp.SaturationLength = method_parameters.get("PVM_MagTransModuleTime")
                        else:
                            ds_temp.DutyCycle = "100"
                        ds_temp.MeasurementNumber = acqp_parameters.get("ACQ_O2_list_size")
                        ds_temp.RecoveryTime = int(ds_temp.RepetitionTime) - int(ds_temp.PulseDuration)
                        if np.size(acqp_parameters.get("ACQ_O2_list"))>1 and np.size(acqp_parameters.get("ACQ_O2_list"))==nframes:
                            ds_temp.SaturationOffsetHz = acqp_parameters.get('ACQ_O2_list')[k]
                            ds_temp.SaturationOffsetPpm = acqp_parameters.get('ACQ_O2_list')[k]/ds_temp.ImagingFrequency 
                        elif np.size(acqp_parameters.get("ACQ_O2_list"))>1 and np.size(acqp_parameters.get("ACQ_O2_list"))!=nframes:
                            f_step =  int(nframes/np.size(acqp_parameters.get("ACQ_O2_list")))
                            sat_freq = []
                            for t in range(0,np.size(acqp_parameters.get("ACQ_O2_list"))):
                                for kk in range(0,f_step):
                                    sat_freq.append(acqp_parameters.get("ACQ_O2_list")[t])  
                            ds_temp.SaturationOffsetHz=str(np.array(sat_freq,dtype=float)[k]) 
                            sat_freq_ppm = sat_freq[k]/ds_temp.ImagingFrequency
                            ds_temp.SaturationOffsetPpm = sat_freq_ppm
                        else:
                            ds_temp.SaturationOffsetHz = acqp_parameters.get('ACQ_O2_list')                               
                            ds_temp.SaturationOffsetPpm = acqp_parameters.get('ACQ_O2_list')/ds_temp.ImagingFrequency 

                    # Add new tag entries for 3T
                    elif (
                        "CEST" in ds_temp.ProtocolName
                        or "cest" in ds_temp.SequenceName
                        and "BioSpec" in ds_temp.StationName
                        and ds_temp.MagneticFieldStrength == 3
                    ):
                        att_db = float(method_parameters.get("CestPulse")[3])
                        if att_db > 100 and img_frames <= 10:
                            pass
                        else:
                            # Add_dict_entries (new_dict_items)
                            ds_temp.Creator = method_parameters.get("OWNER")
                            ds_temp.ChemicalExchangeSaturationType = method_parameters.get("Method")
                            ds_temp.PulseShape = str(method_parameters.get("CestPulseEnum"))  # train
                            ds_temp.PulseLength = method_parameters.get("CestPulse")[0]  # train
                            ds_temp.RecoveryTime = int(ds_temp.RepetitionTime) + int(ds_temp.PulseDuration)
                            if "TRAIN" in method_parameters.get("Method"):
                                # att_db = method_parameters.get("CestPulse")[3] #need to convert this in uT
                                tau_p = float(method_parameters.get("CestPulse")[0])
                                tau_d = float(method_parameters.get("Delay5"))
                                n = acqp_parameters.get("L")[3]
                                magtransmoduletime = (tau_p + tau_d) * n
                                ds_temp.SaturationLength = magtransmoduletime
                                ds_temp.PulseNumber = acqp_parameters.get("L")[3]
                                ds_temp.DutyCycle = method_parameters.get("DutyCycle")
                            else:
                                ds_temp.PulseNumber = 1  # CW
                                ds_temp.SaturationLength = ds_temp.PulseDuration * ds_temp.PulseNumber
                                ds_temp.DutyCycle = "100"

                            ds_temp.MeasurementNumber = acqp_parameters.get("ACQ_O2_list_size")
                            if np.size(acqp_parameters.get("ACQ_O2_list")) > 1:
                                ds_temp.SaturationOffsetHz = acqp_parameters.get("ACQ_O2_list")[k]
                                sat_freq = acqp_parameters.get("ACQ_O2_list")[k]/ds_temp.ImagingFrequency
                                ds_temp.SaturationOffsetPpm = sat_freq
                            else:
                                ds_temp.SaturationOffsetHz = acqp_parameters.get("ACQ_O2_list")
                                ds_temp.SaturationOffsetPpm = acqp_parameters.get("ACQ_O2_list")/ ds_temp.ImagingFrequency

                    outfile = "%s%s.dcm" % (filename_little_endian, str(count))

                    # Save dicoms in separate slices
                    os.chdir(head2)
                    ds_temp.is_little_endian = True
                    ds_temp.is_implicit_VR = False
                    ds_temp.save_as(outfile)
                    count += 1
                    k += 1
                    ii += 1

    if parameters:
        # if "parameters" in globals() or "parameters" in locals():
        master.progress.stop()
        master.root.withdraw()
        #messagebox.showinfo("Success!", "DICOM files have been successfully created!")
    else:
        master.progress.stop()
        master.root.withdraw()
        messagebox.showerror(
            "Error!",
            "Bruker files have not been found in the chosen folder/subfolders!",
        )
        os._exit(1)

    return
