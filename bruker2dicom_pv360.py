#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 15:23:32 2020

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

def bruker2dicom_pv360(folder_to_convert, master):
    
    #Tag entries for cest acquisition
    add_cest_dict()        
    
    a = '1'
    c = 'visu_pars'
    d = '2dseq'
    e = 'method'
    f = 'acqp'
    g = 'reco'
    res = []
    parameters=0
    
    for root,dirs,files in sorted(os.walk(folder_to_convert, topdown=True)):
        for dir in dirs:
            res = os.path.join(root) 
            dirs[:] = [] # Don't recurse any deeper
            visu_pars_file = os.path.abspath(os.path.join(res,a,c))
            dseq_file = os.path.abspath(os.path.join(res,a,d))
            reco_file = os.path.abspath(os.path.join(res,a,g))
            method_file = os.path.abspath(os.path.join(os.path.dirname(res),e))
            acqp_file = os.path.abspath(os.path.join(os.path.dirname(res),f))
            if os.path.exists(dseq_file):
                with open(visu_pars_file, 'r'):
                    parameters = read_visupars_parameters(visu_pars_file)
                with open(reco_file, 'r'):
                    reco_parameters = read_method_parameters(reco_file)
                with open(method_file, 'r'):
                    method_parameters = read_method_parameters(method_file)
                with open(acqp_file, 'r'):
                    acqp_parameters = read_visupars_parameters(acqp_file)                    
            else:
                break
                                                       
            filename_little_endian = 'Im'
        
            img_type = parameters.get("VisuCoreWordType")
            img_endianness = parameters.get("VisuCoreByteOrder")                
            core_ext = parameters.get("VisuCoreExtent")
            
            if isinstance(parameters.get("VisuCoreDataSlope"), str) and isinstance(parameters.get("VisuCoreDataOffs"), str):
                slope = float(parameters.get("VisuCoreDataSlope")[parameters.get("VisuCoreDataSlope").find('(') \
                                                            + 1 : parameters.get("VisuCoreDataSlope").find(')')])
                intercept = float(parameters.get("VisuCoreDataOffs")[parameters.get("VisuCoreDataOffs").find('(') \
                                                            + 1 : parameters.get("VisuCoreDataOffs").find(')')])   
            else:
                slope = parameters.get("VisuCoreDataSlope")
                intercept = parameters.get("VisuCoreDataOffs")
        
                
            # Check endianness and precision
            if img_type == '_32BIT_SGN_INT' and img_endianness == 'littleEndian':
                data_precision = np.dtype('<i4')
            elif img_type == '_32BIT_SGN_INT' and img_endianness == 'bigEndian':
                data_precision = np.dtype('>i4')
            elif img_type == '_16BIT_SGN_INT' and img_endianness == 'littleEndian':
                data_precision = np.dtype('<i2')
            elif img_type == '_16BIT_SGN_INT' and img_endianness == 'bigEndian':
                data_precision = np.dtype('>i2')
            else:
                print('The image data precision is neither 16 bit nor 32 bit!')
            
            raw_data = open(dseq_file, 'rb')
            img_data_precision = np.fromfile(raw_data, dtype=data_precision)
#                output = open("img_data_precision","wb")
#                output.write(img_data_precision)
#                output.close()
#                del output
            raw_data.close()
                        
            head2,tail2 = os.path.split(res)                       
            os.chdir(head2)
                
            if img_type == '_16BIT_SGN_INT' and img_endianness == 'littleEndian':            
                
                #img = np.array(img_data_precision,np.uint16) 
                
                if np.size(slope)==1:
                    img_data_corrected = img_data_precision*slope
                    img_data_corrected +=  intercept
                else:
                    img_data_corrected = img_data_precision*slope[0]
                    img_data_corrected +=  intercept[0]
                    
                factor = ((2**16)-1)/(np.amax(img_data_corrected))
             
                img_float = img_data_corrected * factor
#                    output = open("img_float","wb")
#                    output.write(img_float)
#                    output.close()
#                    del output
                
                # cast at the very end
                img = np.array(img_float,np.uint16)
#                    output = open("img","wb")
#                    output.write(img)
#                    output.close()
#                    del output
    
                # reconstruct the 32 bit signed image back
#                    img_data_corrected2 = img/factor
#                    output = open("img_data_corrected2","wb")
#                    output.write(img_data_corrected2)
#                    output.close()
#                    del output
                
#                    img_data_precision_float2 = img_data_corrected2/slope
#                    output = open("img_data_precision_float2","wb")
#                    output.write(img_data_precision_float2)
#                    output.close()
#                    del output
                
#                    img_data_precision2 = np.array(img_data_precision_float2,np.int32) 
#                    output = open("img_data_precision2","wb")
#                    output.write(img_data_precision2)
#                    output.close()
#                    del output
                    
            # if 32 bit, slope and intercept correction                        
            elif img_type == '_32BIT_SGN_INT' and img_endianness == 'littleEndian': 
                
                if np.size(slope)==1:
                    img_data_corrected = img_data_precision*slope
                    img_data_corrected +=  intercept
                else:
                    img_data_corrected = img_data_precision*slope[0]
                    img_data_corrected +=  intercept[0]
                    
                factor = ((2**16)-1)/(np.amax(img_data_corrected))
             
                img_float = img_data_corrected * factor
#                    output = open("img_float","wb")
#                    output.write(img_float)
#                    output.close()
#                    del output
                
                # cast at the very end
                img = np.array(img_float,np.uint16)
#                    output = open("img","wb")
#                    output.write(img)
#                    output.close()
#                    del output

#                    # reconstruct the 32 bit signed image back
#                    img_data_corrected2 = img/factor
#                    output = open("img_data_corrected2","wb")
#                    output.write(img_data_corrected2)
#                    output.close()
#                    del output
#                    
#                    img_data_precision_float2 = img_data_corrected2/slope[0]
#                    output = open("img_data_precision_float2","wb")
#                    output.write(img_data_precision_float2)
#                    output.close()
#                    del output
#                    
#                    img_data_precision2 = np.array(img_data_precision_float2,np.int32) 
#                    output = open("img_data_precision2","wb")
#                    output.write(img_data_precision2)
#                    output.close()
#                    del output

            else:
                messagebox.showerror(
                    "Error!",
                    "The image you are trying to convert is neither 16 bit nor 32 bit!",
                )
                os._exit(0)
                                       
            # Populate required values for file meta information
            file_meta = Dataset()
        
            file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
            file_meta.MediaStorageSOPInstanceUID = parameters.get("VisuUid")
            file_meta.ImplementationClassUID = '1.2.276.0.7230010.3.0.3.6.3'
            file_meta.ImplementationVersionName = 'OFFIS_DCMTK_363'
     
            # Create the FileDataset instance (initially no data elements, but file_meta supplied)
            ds = FileDataset(filename_little_endian, {}, file_meta=file_meta, preamble=b"\0"*128)                  
            ds.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
                           
            # Add the data elements --  Check DICOM standard
            
            head_ID, tail_ID = os.path.split(head2)
            
            # Patient Module of created SOP instances
            ds.PatientName = parameters.get("VisuSubjectName") 
            ds.PatientID = parameters.get("VisuSubjectId")
            ds.PatientBirthDate = parameters.get("VisuSubjectBirthDate")
            ds.PatientSex = parameters.get("VisuSubjectSex")
            ds.PatientComments = parameters.get("VisuSubjectComment")
            ds.PatientSpeciesDescription = parameters.get("VisuSubjectType")  
            ds.PatientBreedDescription = None
            ds.PatientBreedCodeSequence = None
            ds.ResponsiblePerson = None
            ds.BreedRegistrationSequence = None
            ds.ResponsibleOrganization = ' '.join(parameters.get("VisuInstitution"))
            
            # Study Module of created SOP instances
            ds.StudyInstanceUID = parameters.get("VisuStudyUid") 
            VisuStudyDate = parameters.get("VisuStudyDate")
            StudyDate=re.sub('\ |\<|\>', '', VisuStudyDate )
            StudyDate = dateutil.parser.parse(StudyDate)
            ds.StudyDate = StudyDate.strftime("%Y%m%d")
            ds.StudyTime = StudyDate.strftime("%H%M%S")
            ds.ReferringPhysicianName = ' '.join(parameters.get('VisuStudyReferringPhysician'))
            ds.StudyID = parameters.get("VisuStudyId")
            ds.AccessionNumber = ''
            ds.StudyDescription = parameters.get("VisuStudyDescription")
                           
            # Patient Study Module of created SOP instances
            ds.PatientWeight = parameters.get("VisuSubjectWeight")
            
            # General Series Module of created SOP instances
            ds.Modality=str('MR')
            ds.SeriesInstanceUID = parameters.get("VisuUid")
            VisuSeriesDate = parameters.get("VisuSeriesDate")
            SeriesDate = re.sub('\ |\<|\>', '', VisuSeriesDate )
            SeriesDate = dateutil.parser.parse(SeriesDate)
            ds.SeriesDate = SeriesDate.strftime("%Y%m%d")
            ds.SeriesTime = SeriesDate.strftime("%H%M%S")
            if '_' in parameters.get('VisuAcquisitionProtocol'):
                protocol = parameters.get('VisuAcquisitionProtocol').split('_')
                ds.ProtocolName=' '.join(protocol)
                ds.SeriesDescription=' '.join(protocol)
            elif '-' in parameters.get('VisuAcquisitionProtocol'):
                protocol = parameters.get('VisuAcquisitionProtocol').split('-')
                ds.ProtocolName = ' '.join(protocol)
                ds.SeriesDescription=' '.join(protocol)
            else:
                ds.ProtocolName = ' '.join(parameters.get('VisuAcquisitionProtocol'))
                ds.SeriesDescription = ' '.join(parameters.get('VisuAcquisitionProtocol'))
            ds.PatientPosition = parameters.get("VisuSubjectPosition")
            ds.AnatomicalOrientationType = parameters.get("VisuSubjectType")
            
            # Frame Of Reference Module of created SOP instances
            ds.FrameOfReferenceUID = parameters.get("VisuUid") + '.0'
            ds.PositionReferenceIndicator = ' ' 
            
            # General Equipment Module of created SOP instances
            ds.Manufacturer = ' '.join(parameters.get("VisuManufacturer"))
            ds.InstitutionName = ' '.join(parameters.get("VisuInstitution"))
            ds.ManufacturerModelName = parameters.get("VisuStation")
            ds.DeviceSerialNumber = parameters.get('VisuSystemOrderNumber')
            ds.SoftwareVersions = str(parameters.get("VisuCreator")) + ' ' + str(parameters.get("VisuCreatorVersion"))   
            
            # Image Pixel Module of created SOP instances                
            ds.SamplesPerPixel = 1
            ds.PhotometricInterpretation = "MONOCHROME2"
            img_dims = parameters.get("VisuCoreSize")
            if parameters.get("VisuAcqGradEncoding")[0] == 'read_enc':
                ds.Columns = int(img_dims[0])
                ds.Rows = int(img_dims[1])
            elif parameters.get("VisuAcqGradEncoding")[0] == 'phase_enc':
                ds.Columns = int(img_dims[1])
                ds.Rows = int(img_dims[0])                                                                                        
            ds.BitsAllocated = 16
            ds.BitsStored = 16
            ds.HighBit = 15
            ds.PixelRepresentation = 0 # unsigned (0)
            ds.PixelData = img.tobytes() # PixelData contains the raw bytes exactly as found in the file
            ds[0x7FE0,0x0010].VR = 'OW'
            # The dicom_dict entry for LargestImagePixelValue uses an ambiguous VR (Value Representation). 
            # It can either be an unsigned short integer (US) or a signed short integer (SS).
            # In order to properly write the data to the file,
            # you have to explicitly tell it which one you want to use. 
            ds.WindowCenterWidthExplanation = 'MinMax'
            ds.WindowWidth = int(np.amax(img)+1)
            ds.WindowCenter = int((np.amax(img)+1)/2)
            ds[0x0028,0x1050].VR = 'DS'  
            ds[0x0028,0x1051].VR = 'DS'   
            ds.SmallestImagePixelValue = int(np.amin(img))
            ds.LargestImagePixelValue = int(np.amax(img))
            ds[0x0028,0x0106].VR = 'US'  
            ds[0x0028,0x0107].VR = 'US'
            
            # SOP Common Module of created SOP instances
            ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
            ds.SOPInstanceUID = parameters.get("VisuUid") + '.0'
            dt = datetime.datetime.now()
            ds.InstanceCreationDate = dt.strftime('%Y%m%d')
            timeStr = dt.strftime('%H%M%S')  
            ds.InstanceCreationTime = timeStr
            ds.TimezoneOffsetFromUTC = '+0100'
            ds.InstanceNumber = '1' 
            
            # General Image Module in create MR image SOP class
            ds.ImageType = 'ORIGINAL\PRIMARY\OTHER'   
            ds.AcquisitionNumber = '1' 
            VisuAcqDate = parameters.get("VisuAcqDate")
            AcqDate = re.sub('\ |\<|\>', '', VisuAcqDate)
            AcqDate = dateutil.parser.parse(AcqDate)
            ds.AcquisitionDate = AcqDate.strftime("%Y%m%d")
            ds.AcquisitionTime = AcqDate.strftime("%H%M%S")
            ds.ImagesInAcquisition = parameters.get("VisuCoreFrameCount")
            ds.RealWorldValueMappingSequence = None
            ds.RealWorldValueFirstValueMapped = int(np.amin(img))
            ds.RealWorldValueLastValueMapped = int(np.amax(img))
            ds.RealWorldValueIntercept = np.array(intercept,dtype=float)
            ds.RealWorldValueSlope = slope
            ds.LUTExplanation = 'PixelUnit'
            ds.LUTLabel = 'PixelUnit'
            ds.MeasurementUnitsCodeSequence = None
            
            # Image Plane Module in created MR Image SOP class
            if parameters.get("VisuAcqGradEncoding")[0] == 'read_enc':                                        
                ds.PixelSpacing = [core_ext[1]/img_dims[1], core_ext[0]/img_dims[0]]
            elif parameters.get("VisuAcqGradEncoding")[0] == 'phase_enc':
                ds.PixelSpacing = ([core_ext[0]/img_dims[0],core_ext[1]/img_dims[1]])       
            ds.ImagePositionPatient = list(map(str,parameters.get("VisuCorePosition")[0]))
            ds.ImageOrientationPatient = list(map(str,parameters.get("VisuCoreOrientation")[0][0:6]))
            ds.SliceLocation = list(map(str,parameters.get("VisuCorePosition")[0]))[2]
            ds.SliceThickness = parameters.get("VisuCoreFrameThickness")
            
            # MR Image Module in created MR Image SOP class
            ds.ScanningSequence = str('RM')
            ds.SequenceVariant = parameters.get('VisuAcqSpoiling')
            sequencename = ' '.join(parameters.get("VisuAcqSequenceName")).split('_')
            ds.SequenceName = ' '.join(sequencename)
            ds.ScanOptions = None
            ds.MRAcquisitionType = str(parameters.get("VisuCoreDim")) + 'D'                                            
            if np.size(parameters.get("VisuAcqRepetitionTime"))>1:
                ds.RepetitionTime = list(parameters.get("VisuAcqRepetitionTime"))
            else:
                ds.RepetitionTime = parameters.get("VisuAcqRepetitionTime")
            if np.size(parameters.get("VisuAcqEchoTime")) > 1:
                ds.EchoTime = list(parameters.get("VisuAcqEchoTime"))
            else:
                ds.EchoTime = parameters.get("VisuAcqEchoTime")    
            ds.EchoTrainLength = parameters.get('VisuAcqEchoTrainLength')
            ds.InversionTime = parameters.get('VisuAcqInversionTime')
            ds.NumberOfAverages = parameters.get("VisuAcqNumberOfAverages")
            ds.ImagingFrequency = parameters.get("VisuAcqImagingFrequency")
            ds.ImagedNucleus = parameters.get("VisuAcqImagedNucleus")                   
            ds.MagneticFieldStrength = parameters.get('VisuMagneticFieldStrength')
#                z1 = parameters.get("VisuCorePosition")[0]
#                z2 = parameters.get("VisuCorePosi tion")[1]
#                spacing = abs(z1)-abs(z2)
#                ds_temp.SpacingBetweenSlices = abs(round(spacing[2],1))
            ds.NumberOfPhaseEncodingSteps = parameters.get("VisuAcqPhaseEncSteps")
            ds.PercentPhaseFieldOfView = '100' 
            ds.PixelBandwidth = parameters.get("VisuAcqPixelBandwidth")
            ds.ReceiveCoilName = ' '.join(parameters.get("VisuCoilReceiveName"))                  
            ds.InPlanePhaseEncodingDirection = parameters.get("VisuAcqGradEncoding")
            if parameters.get("VisuAcqGradEncoding")[0] == 'read_enc':
                acqmat = np.pad(parameters.get("VisuAcqSize"),1,'constant')
                ds.AcquisitionMatrix = list(np.array(acqmat,dtype=int))                                          
            elif parameters.get("VisuAcqGradEncoding")[0] == 'phase_enc':
                acqmat = np.insert(parameters.get("VisuAcqSize"),1,[0,0])
                ds.AcquisitionMatrix = list(np.flip(np.array(acqmat,dtype=int),0))  #check                                                                        
            ds.FlipAngle=parameters.get("VisuAcqFlipAngle")
 
            # Enhanced MR Image Module created in Enhanced MR Image Sop class
            ds.AcquisitionDuration = parameters.get("VisuAcqScanTime") 

            # Other tags  
            ds.PatientOrientation = method_parameters.get("PVM_SPackArrReadOrient")[0][1:]               
            ds.NumberOfFrames = parameters.get("VisuCoreFrameCount")
            nframes = parameters.get("VisuCoreFrameCount")
            ds.NumberOfSlices = acqp_parameters.get("NSLICES")
                   
    #        # Uncomment you want to save all the slices in one dicom file
    #        head2, tail2 = os.path.split(res)
    #        os.chdir(res)
    #        ds.save_as(filename_little_endian)
                           
            # Write dicom in separate slices only if number of slices is greater than 1                     
            if nframes==1:
                head2,tail2 = os.path.split(res)
                head3,tail3 = os.path.split(head2)
                ds.SeriesNumber=tail3
                ds.RescaleSlope =  factor
                ds.RescaleIntercept = str(np.array(intercept,dtype=float))
                os.chdir(head2)
                outfile = "%s%s.dcm" % (filename_little_endian, str(1))
                ds.is_little_endian = True
                ds.is_implicit_VR = False
                ds.save_as(outfile)
            
            else:
                count=1 
                k=0
                ii=0
                for layer in ds.pixel_array:                        
                    
                    layer = np.reshape(layer,int(img_dims[0])*int(img_dims[1]))
                        
                    # Populate required values for file meta information
                    file_meta_temp = Dataset()     
                    file_meta_temp.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
                    file_meta_temp.MediaStorageSOPInstanceUID = parameters.get("VisuUid") + ".%s" % (k)
                    file_meta_temp.ImplementationClassUID = '1.2.276.0.7230010.3.0.3.6.3'
                    file_meta_temp.ImplementationVersionName = 'OFFIS_DCMTK_363'
               
                    # Create the FileDataset instance (initially no data elements, but file_meta supplied)
                    ds_temp = FileDataset(filename_little_endian, {}, file_meta=file_meta_temp, preamble=b"\0" * 128)
                    
                    ds_temp.file_meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian
                                                                                                                               
                    # Add the data elements --  Check DICOM standard
                   
                    head_ID, tail_ID = os.path.split(head2)
                    
                    # Patient Module of created SOP instances
                    ds_temp.PatientName = parameters.get("VisuSubjectName") 
                    ds_temp.PatientID = parameters.get("VisuSubjectId")
                    ds_temp.PatientBirthDate = parameters.get("VisuSubjectBirthDate")
                    ds_temp.PatientSex  =parameters.get("VisuSubjectSex")
                    ds_temp.PatientComments = parameters.get("VisuSubjectComment")                                                
                    ds_temp.PatientSpeciesDescription = parameters.get("VisuSubjectType")    
                    ds_temp.PatientBreedDescription = None
                    ds_temp.PatientBreedCodeSequence = None
                    ds_temp.ResponsiblePerson = None
                    ds_temp.BreedRegistrationSequence = None
                    ds_temp.ResponsibleOrganization = ' '.join(parameters.get("VisuInstitution"))
                    
                    # Study Module of created SOP instances
                    ds_temp.StudyInstanceUID =parameters.get("VisuStudyUid") 
                    ds_temp.StudyDate = StudyDate.strftime("%Y%m%d")
                    ds_temp.StudyTime= StudyDate.strftime("%H%M%S")
                    ds_temp.ReferringPhysicianName = ' '.join(parameters.get('VisuStudyReferringPhysician'))
                    ds_temp.StudyID = parameters.get("VisuStudyId")
                    ds_temp.AccessionNumber = ''
                    ds_temp.StudyDescription = parameters.get("VisuStudyDescription")
                    
                    # Patient Study Module of created SOP instances
                    ds_temp.PatientWeight = parameters.get("VisuSubjectWeight")
                    
                    # General Series Module of created SOP instances
                    ds_temp.Modality = str('MR')
                    ds_temp.SeriesInstanceUID = parameters.get("VisuUid")
                    ds_temp.SeriesNumber = os.path.basename(head2) 
                    VisuSeriesDate = parameters.get("VisuSeriesDate")
                    SeriesDate = re.sub('\ |\<|\>', '', VisuSeriesDate )
                    SeriesDate = dateutil.parser.parse(SeriesDate)
                    ds_temp.SeriesDate = SeriesDate.strftime("%Y%m%d")
                    ds_temp.SeriesTime = SeriesDate.strftime("%H%M%S")
                    if '_' in parameters.get('VisuAcquisitionProtocol'):
                        protocol = parameters.get('VisuAcquisitionProtocol').split('_')
                        ds_temp.ProtocolName=' '.join(protocol)
                        ds_temp.SeriesDescription=' '.join(protocol)
                    elif '-' in parameters.get('VisuAcquisitionProtocol'):
                        protocol = parameters.get('VisuAcquisitionProtocol').split('-')
                        ds_temp.ProtocolName = ' '.join(protocol)
                        ds_temp.SeriesDescription=' '.join(protocol)
                    else:
                        ds_temp.ProtocolName = ' '.join(parameters.get('VisuAcquisitionProtocol'))
                        ds_temp.SeriesDescription = ' '.join(parameters.get('VisuAcquisitionProtocol'))
                    ds_temp.PatientPosition = parameters.get("VisuSubjectPosition")
                    ds_temp.AnatomicalOrientationType = parameters.get("VisuSubjectType")
                    
                    # Frame Of Reference Module of created SOP instances
                    ds_temp.FrameOfReferenceUID = parameters.get("VisuUid") + ".%s" % (k)
                    ds_temp.PositionReferenceIndicator = ' ' 

                    # General Equipment Module of created SOP instances
                    ds_temp.Manufacturer = ' '.join(parameters.get("VisuManufacturer"))
                    ds_temp.InstitutionName = ' '.join(parameters.get("VisuInstitution"))
                    ds_temp.ManufacturerModelName = parameters.get("VisuStation")
                    ds_temp.DeviceSerialNumber = parameters.get('VisuSystemOrderNumber')
                    ds_temp.SoftwareVersions = str(parameters.get("VisuCreator")) + ' ' + str(parameters.get("VisuCreatorVersion"))  
                   
                    # Image Pixel Module of created SOP instances               
                    ds_temp.PixelData = layer
                    ds_temp[0x7FE0,0x0010].VR = 'OW' 
                    ds_temp.SamplesPerPixel = 1
                    ds_temp.PhotometricInterpretation = "MONOCHROME2"
                    if parameters.get("VisuAcqGradEncoding")[0] == 'read_enc':
                        ds_temp.Columns = int(img_dims[0])
                        ds_temp.Rows = int(img_dims[1])
                    elif parameters.get("VisuAcqGradEncoding")[0] == 'phase_enc':
                        ds_temp.Columns = int(img_dims[1])
                        ds_temp.Rows = int(img_dims[0])
                    ds_temp.BitsAllocated = 16
                    ds_temp.BitsStored = 16
                    ds_temp.HighBit = 15
                    ds_temp.PixelRepresentation = 0 
                    # The dicom_dict entry for LargestImagePixelValue uses an ambiguous VR (Value Representation). 
                    # It can either be an unsigned short integer (US) or a signed short integer (SS).
                    # In order to properly write the data to the file,
                    # you have to explicitly tell it which one you want to use. 
                    ds.WindowCenterWidthExplanation = 'MinMax'
                    ds_temp.WindowWidth = int(np.amax(img)+1)
                    ds_temp.WindowCenter = int((np.amax(img)+1)/2)
                    ds_temp[0x0028,0x1050].VR = 'DS'  
                    ds_temp[0x0028,0x1051].VR = 'DS'                                                                                                                                         
                    ds_temp.SmallestImagePixelValue = int(np.amin(layer))
                    ds_temp.LargestImagePixelValue = int(np.amax(layer))
                    ds_temp[0x0028,0x0106].VR = 'US'  
                    ds_temp[0x0028,0x0107].VR = 'US' 
                    
                    # SOP Common Module of created SOP instances
                    ds_temp.SOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
                    ds_temp.SOPInstanceUID = parameters.get("VisuUid") + ".%s" % (k)
                    dt = datetime.datetime.now()
                    ds_temp.InstanceCreationDate = dt.strftime('%Y%m%d')
                    timeStr = dt.strftime('%H%M%S')
                    ds_temp.InstanceCreationTime = timeStr 
                    ds_temp.TimezoneOffsetFromUTC = '+0100'
                    ds_temp.InstanceNumber = count 
                    
                    # General Image Module in create MR image SOP class
                    ds_temp.ImageType = 'ORIGINAL\PRIMARY\OTHER' 
                    ds_temp.AcquisitionNumber = k
                    ds_temp.AcquisitionDate = AcqDate.strftime("%Y%m%d")
                    ds_temp.AcquisitionTime = AcqDate.strftime("%H%M%S")
                    ds_temp.ImagesInAcquisition = parameters.get("VisuCoreFrameCount")
                    ds_temp.RealWorldValueMappingSequence = None
#                        ds_temp.RealWorldValueFirstValueMapped = int(np.amin(layer))
#                        ds_temp.RealWorldValueLastValueMapped =  len(np.amax(layer))
                    if isinstance(parameters.get("VisuCoreDataSlope"), str) and isinstance(parameters.get("VisuCoreDataOffs"), str): 
                        ds_temp.RealWorldValueIntercept =  float(parameters.get("VisuCoreDataOffs")[parameters.get("VisuCoreDataOffs").find('(') \
                                        + 1 : parameters.get("VisuCoreDataOffs").find(')')]) 
                        ds_temp.RealWorldValueSlope = float(parameters.get("VisuCoreDataSlope")[parameters.get("VisuCoreDataSlope").find('(') \
                                        + 1 : parameters.get("VisuCoreDataSlope").find(')')])  
                    else:                                                                      
                        for j in range(0,nframes-1):
                            ds_temp.RealWorldValueIntercept = parameters.get("VisuCoreDataOffs")[j]  
                            ds_temp.RealWorldValueSlope = parameters.get("VisuCoreDataSlope")[j]                      
                    ds_temp.LUTExplanation = 'PixelUnit'
                    ds_temp.LUTLabel = 'PixelUnit'
                    ds_temp.MeasurementUnitsCodeSequence = None
                    
                    # Image Plane Module in created MR Image SOP class
                    if parameters.get("VisuAcqGradEncoding")[0] == 'read_enc':                                         
                        ds_temp.PixelSpacing = [core_ext[1]/img_dims[1],core_ext[0]/img_dims[0]]
                    elif parameters.get("VisuAcqGradEncoding")[0] == 'phase_enc':
                        ds_temp.PixelSpacing = ([core_ext[0]/img_dims[0],core_ext[1]/img_dims[1]])  
                    if parameters.get("VisuCoreOrientation").shape[0] == 1:
                        ds_temp.ImagePositionPatient = list(map(str,parameters.get("VisuCorePosition")[0]))
                        ds_temp.ImageOrientationPatient = list(map(str,parameters.get("VisuCoreOrientation")[0][0:6]))
                        ds_temp.SliceThickness = parameters.get("VisuCoreFrameThickness")
                        ds_temp.SliceLocation = parameters.get("VisuCorePosition")[0][2]
                    elif parameters.get("VisuCoreOrientation").shape[0] != nframes:
                        p = int(nframes/parameters.get("VisuCorePosition").shape[0])
                        visucoreposition = np.tile(parameters.get("VisuCorePosition"),(p,1))
                        o = int(nframes/parameters.get("VisuCoreOrientation").shape[0])
                        visucoreorientation = np.tile(parameters.get("VisuCoreOrientation"),(p,1))
                        ds_temp.ImagePositionPatient = list(map(str,visucoreposition[ii]))
                        ds_temp.ImageOrientationPatient = list(map(str,visucoreorientation[ii][0:6]))
                        ds_temp.SliceThickness = parameters.get("VisuCoreFrameThickness")
                        ds_temp.SliceLocation = list(map(str,visucoreposition[ii]))[2] 
                    else:                           
                        ds_temp.ImagePositionPatient = list(map(str,parameters.get("VisuCorePosition")[k]))
                        ds_temp.ImageOrientationPatient = list(map(str,parameters.get("VisuCoreOrientation")[k][0:6]))                                                                         
                        ds_temp.SliceThickness = parameters.get("VisuCoreFrameThickness")                                 
                        ds_temp.SliceLocation = list(map(str,parameters.get("VisuCorePosition")[k]))[2]
                    
                    # MR Image Module in created MR Image SOP class
                    ds_temp.ScanningSequence = str('RM')
                    ds_temp.SequenceVariant = parameters.get('VisuAcqSpoiling')
                    ds_temp.SequenceName = ' '.join(sequencename)
                    ds_temp.ScanOptions = ' '
                    ds_temp.MRAcquisitionType = str(parameters.get("VisuCoreDim")) + 'D'
                    if np.size(parameters.get("VisuAcqRepetitionTime")) > 1 and np.size(parameters.get("VisuAcqRepetitionTime")) == nframes:
                        ds_temp.RepetitionTime = str(np.array(parameters.get("VisuAcqRepetitionTime"),dtype=int)[k]) 
                    elif np.size(parameters.get("VisuAcqRepetitionTime")) > 1 and np.size(parameters.get("VisuAcqRepetitionTime")) != nframes:
                        r_step =  int(nframes/np.size(parameters.get("VisuAcqRepetitionTime")))
                        repetition_time = []
                        for t in range(0,np.size(parameters.get("VisuAcqRepetitionTime"))):
                            for kk in range(0,r_step):
                                 repetition_time.append(parameters.get("VisuAcqRepetitionTime")[t])  
                        ds_temp.RepetitionTime = str(np.array(repetition_time,dtype=float)[k])                           
                    else:
                        ds_temp.RepetitionTime = parameters.get("VisuAcqRepetitionTime")                
                    if np.size(parameters.get("VisuAcqEchoTime")) > 1 and np.size(parameters.get("VisuAcqEchoTime")) == nframes:
                        ds_temp.EchoTime = str(np.array(parameters.get("VisuAcqEchoTime"),dtype=float)[k])
                    elif np.size(parameters.get("VisuAcqEchoTime")) > 1 and np.size(parameters.get("VisuAcqEchoTime")) != nframes:
                        e_step =  int(nframes/np.size(parameters.get("VisuAcqEchoTime")))
                        echo_time = []
                        for t in range(0,np.size(parameters.get("VisuAcqEchoTime"))):
                            for kk in range(0,e_step):
                                 echo_time.append(parameters.get("VisuAcqEchoTime")[t])  
                        ds_temp.EchoTime = str(np.array(echo_time,dtype=float)[k])                           
                    else:
                        ds_temp.EchoTime = parameters.get("VisuAcqEchoTime")   
                    ds_temp.EchoTrainLength = parameters.get('VisuAcqEchoTrainLength')
                    ds_temp.InversionTime = parameters.get('VisuAcqInversionTime')
                    ds_temp.NumberOfAverages = str(parameters.get("VisuAcqNumberOfAverages"))
                    ds_temp.ImagingFrequency=parameters.get("VisuAcqImagingFrequency")
                    ds_temp.ImagedNucleus=parameters.get("VisuAcqImagedNucleus")
                    ds_temp.MagneticFieldStrength = parameters.get('VisuMagneticFieldStrength')
#                        z1 = parameters.get("VisuCorePosition")[0]
#                        z2 = parameters.get("VisuCorePosition")[1]
#                        spacing = abs(z1)-abs(z2)
#                        ds_temp.SpacingBetweenSlices = abs(round(spacing[2],1))
                    ds_temp.NumberOfPhaseEncodingSteps=parameters.get("VisuAcqPhaseEncSteps")
                    ds_temp.PercentPhaseFieldOfView = '100' 
                    ds_temp.PixelBandwidth = parameters.get("VisuAcqPixelBandwidth")
                    ds_temp.ReceiveCoilName = ' '.join(parameters.get("VisuCoilReceiveName"))
                    ds_temp.InPlanePhaseEncodingDirection = parameters.get("VisuAcqGradEncoding")
                    if parameters.get("VisuAcqGradEncoding")[0] == 'read_enc':
                        acqmat=np.pad(parameters.get("VisuAcqSize"),1,'constant')
                        ds_temp.AcquisitionMatrix=list(np.array(acqmat,dtype=int))                                          
                        ds_temp.PixelSpacing = [core_ext[1]/img_dims[1],core_ext[0]/img_dims[0]]
                    elif parameters.get("VisuAcqGradEncoding")[0] == 'phase_enc':
                        acqmat=np.insert(parameters.get("VisuAcqSize"),1,[0,0])
                        ds_temp.AcquisitionMatrix = list(np.flip(np.array(acqmat,dtype=int),0))  #check                                                                        
                        ds_temp.PixelSpacing = ([core_ext[0]/img_dims[0],core_ext[1]/img_dims[1]])                      
                    ds_temp.FlipAngle = str(parameters.get("VisuAcqFlipAngle"))       
          
                    # Enhanced MR Image Module created in Enhanced MR Image Sop class
                    ds_temp.AcquisitionDuration = parameters.get("VisuAcqScanTime")                                                   
                    
                    # Other Tags
                    ds_temp.PatientOrientation = method_parameters.get("PVM_SPackArrReadOrient")[0]
                    ds_temp.NumberOfFrames = 1
                    ds_temp.NumberOfSlices = acqp_parameters.get("NSLICES")                       
                    ds_temp.RescaleSlope = factor      
                    if isinstance(parameters.get("VisuCoreDataSlope"), str) and isinstance(parameters.get("VisuCoreDataOffs"), str): 
                        ds_temp.RescaleIntercept =  parameters.get("VisuCoreDataOffs")[parameters.get("VisuCoreDataOffs").find('(') \
                                        + 1 : parameters.get("VisuCoreDataOffs").find(')')]        
                    else:                                                                      
                        for j in range(0,nframes-1):
                            ds_temp.RescaleIntercept = str(parameters.get("VisuCoreDataOffs")[j])                       
                        

                    #####
                    
                    
                    string2 = str(reco_parameters.get("RECO_fov"))
                    vect2 = re.findall('[0-9]+',string2)
                    vect2.pop(0)
                    vect3 = []
                    for elem in vect2:
                        vect3.append(float(elem))
                    ds_temp.ReconstructionFieldOfView = vect3

                    # DCE acquisition
                    if "DCE FLASH" in ds_temp.ProtocolName or "DCE" in ds_temp.ProtocolName:
                        NRepetitions = method_parameters.get("PVM_NRepetitions")
                        enc_matrix = str(method_parameters.get("PVM_EncMatrix"))                            
                        enc_step = float(re.findall('[0-9]+',enc_matrix)[1])
                        total_scan_time = ds_temp.RepetitionTime * NRepetitions * enc_step
                        scan_time_step = int(ds_temp.RepetitionTime * enc_step) # in ms
                        vect4 = []
                        scan_time = 0
                        step = int(nframes/NRepetitions)
                        for t in range(0,NRepetitions):
                            scan_time = scan_time + scan_time_step
                            for kk in range(0,step):
                                vect4.append(scan_time)                            
                        ds_temp.TriggerTime = np.array(vect4)[k]
                                            
                    # DWI acquisition
                    if "diffusion" in ds_temp.ProtocolName or "EPI" in ds_temp.ProtocolName:
                        string = str(method_parameters.get("PVM_DwBvalEach"))
                        b_values = re.findall('[0-9]+',string)
                        #b_values.pop(0)
                        b_values.insert(0,'0')
                        bvalues = []
                        for elem in b_values:
                            bvalues.append(float(elem))
                        vect3 = []
                        step = int(nframes/len(b_values))
                        for t in range(0,len(b_values)):
                            for kk in range(0,step):
                                 vect3.append(bvalues[t])                           
                        ds_temp.DiffusionBValue = np.array(vect3)[k]      
                            # overwrite corresponding tag got from visupars with new info?
                            
                        #method_parameters.get("PVM_DwNDiffExp")
                    # CEST acquisition                                                                           
                    if "cest" in ds_temp.ProtocolName and method_parameters.get("PVM_SatTransOnOff") == 'On':
                        ds_temp.Creator = method_parameters.get("OWNER")
                        ds_temp.ChemicalExchangeSaturationType = method_parameters.get("Method")
                        ds_temp.SamplingType = method_parameters.get("PVM_SatTransType")
                        ds_temp.PulseShape = method_parameters.get("PVM_SatTransPulseEnum") 
                        ds_temp.PulseLength = method_parameters.get("PVM_SatTransPulse")[0]                                   
                        ds_temp.B1Saturation = method_parameters.get("PVM_SatTransPulseAmpl_uT")                           
                        ds_temp.PulseNumber = method_parameters.get("PVM_SatTransNPulses")                                                                  
                        # train module needs to be checked
                        if 'train' in method_parameters.get("Method"):
                            tau_p = float(method_parameters.get("PVM_SatTransPulse")[0])
                            tau_d = float(method_parameters.get("PVM_SatTransInterPulseDelay"))
                            n = int(method_parameters.get("PVM_SatTransNPulses"))
                            #method_parameters.get("PVM_SatTransModuleTime") #the result of this two lines should be the same
                            #magtransmoduletime = (tau_p + tau_d) * n
                            ds_temp.InterpulseDelay = tau_d
                            ds_temp.DutyCycle = tau_p/(tau_p + tau_d) * 100      
                            ds_temp.SaturationLength = method_parameters.get("PVM_SatTransModuleTime")
                        else:
                            ds_temp.DutyCycle = '100' 
                            ds_temp.SaturationLength = ds_temp.PulseLength * ds_temp.PulseNumber                                                                
                        NSatFreq = method_parameters.get('PVM_NSatFreq')
                        if NSatFreq != None:
                            f_step =  int(nframes/NSatFreq)
                            ds_temp.MeasurementNumber = NSatFreq
                            ds_temp.RecoveryTime = int(ds_temp.RepetitionTime) - int(ds_temp.PulseLength)
                            freq_list = method_parameters.get('PVM_SatTransFreqValues') # frequency list is formatted differently for CEST Off and On, need to distinguish both cases
                            if  method_parameters.get("PVM_SatTransFreqUnit") == 'unit_ppm' and "  " in freq_list[0]: #CEST ON 
                                freq_list = freq_list[0].split("  ")
                                while '' in freq_list:
                                    freq_list.remove('')
                                [elem.strip(' ') for elem in freq_list]
                                sat_freq_ppm = np.array(freq_list, dtype=float)   
                                if NSatFreq > 1 and NSatFreq == nframes:
                                    ds_temp.SaturationOffsetPpm = sat_freq_ppm[k]
                                    ds_temp.SaturationOffsetHz =  sat_freq_ppm[k] * ds_temp.ImagingFrequency 
                                elif NSatFreq > 1 and NSatFreq != nframes:                            
                                    SatFreqPpm = []
                                    for t in range(0, NSatFreq):
                                        for kk in range(0, f_step):
                                           SatFreqPpm.append(sat_freq_ppm[t])                                   
                                    ds_temp.SaturationOffsetPpm = str(np.array(SatFreqPpm,dtype=float)[k]) 
                                    sat_freq_hz = SatFreqPpm[k] * ds_temp.ImagingFrequency 
                                    ds_temp.SaturationOffsetHz = sat_freq_hz  
                                ### Tags for CEST ON only  
                                ds_temp.PulseLength2 = method_parameters.get("PVM_SatTransPulseLength2")
                                ds_temp.ReadoutTime = (ds_temp.RepetitionTime - ds_temp.PulseLength - (ds_temp.PulseLength2 * (f_step - 1))) / f_step
                            elif method_parameters.get("PVM_SatTransFreqUnit") == 'unit_ppm' and " " in freq_list[0]: # CEST OFF   
                                freq_list = freq_list[0].split(" ")
                                while '' in freq_list:
                                    freq_list.remove('')
                                [elem.strip(' ') for elem in freq_list]
                                sat_freq_ppm = np.array(freq_list, dtype=float) 
                                SatFreqPpm = []
                                for t in range(0, NSatFreq):
                                    for kk in range(0, f_step):
                                        SatFreqPpm.append(sat_freq_ppm[t])                                   
                                ds_temp.SaturationOffsetPpm = str(np.array(SatFreqPpm,dtype=float)[k]) 
                                sat_freq_hz = SatFreqPpm[k] * ds_temp.ImagingFrequency 
                                ds_temp.SaturationOffsetHz = sat_freq_hz 
                                ### Not tested
                            elif method_parameters.get("PVM_SatTransFreqUnit") == 'unit_hz' and "  " in freq_list[0]: #CEST ON 
                                freq_list = freq_list[0].split("  ")
                                while '' in freq_list:
                                    freq_list.remove('')
                                [elem.strip(' ') for elem in freq_list]
                                sat_freq_hz = np.array(freq_list, dtype=float)   
                                if NSatFreq > 1 and NSatFreq == nframes:
                                    ds_temp.SaturationOffsetHz = sat_freq_hz[k]
                                    ds_temp.SaturationOffsetPpm =  sat_freq_hz[k] * ds_temp.ImagingFrequency 
                                elif NSatFreq > 1 and NSatFreq != nframes:                            
                                    SatFreqHz = []
                                    for t in range(0, NSatFreq):
                                        for kk in range(0, f_step):
                                           SatFreqHz.append(sat_freq_hz[t])                                   
                                    ds_temp.SaturationOffsetHz = str(np.array(SatFreqHz,dtype=float)[k]) 
                                    sat_freq_ppm = SatFreqHz[k] * ds_temp.ImagingFrequency 
                                    ds_temp.SaturationOffsetPpm = sat_freq_ppm  
                                ### Tags for CEST ON only  
                                ds_temp.PulseLength2 = method_parameters.get("PVM_SatTransPulseLength2")
                                ds_temp.ReadoutTime = (ds_temp.RepetitionTime - ds_temp.PulseLength - (ds_temp.PulseLength2 * (f_step - 1))) / f_step
                            elif method_parameters.get("PVM_SatTransFreqUnit") == 'unit_hz' and " " in freq_list[0]: # CEST OFF   
                                freq_list = freq_list[0].split(" ")
                                while '' in freq_list:
                                    freq_list.remove('')
                                [elem.strip(' ') for elem in freq_list]
                                sat_freq_hz = np.array(freq_list, dtype=float) 
                                SatFreqHz= []
                                for t in range(0, NSatFreq):
                                    for kk in range(0, f_step):
                                        SatFreqHz.append(sat_freq_hz[t])                                   
                                ds_temp.SaturationOffsetHz = str(np.array(SatFreqHz,dtype=float)[k]) 
                                sat_freq_ppm = SatFreqHz[k] * ds_temp.ImagingFrequency 
                                ds_temp.SaturationOffsetPpm = sat_freq_ppm  
                        elif NSatFreq == None and method_parameters.get("PVM_SatTransFreqUnit") == 'unit_ppm':
                            freq_list = method_parameters.get('PVM_SatTransFreqValues') # frequency list is formatted differently for CEST Off and On, need to distinguish both cases
                            freq_list = freq_list[0].split(" ")
                            while '' in freq_list:
                                freq_list.remove('')
                            [elem.strip(' ') for elem in freq_list]
                            sat_freq_ppm = np.array(freq_list, dtype=float)  
                            ds_temp.SaturationOffsetPpm = sat_freq_ppm[k]
                            ds_temp.SaturationOffsetHz =  sat_freq_ppm[k] * ds_temp.ImagingFrequency 
                        elif NSatFreq == None and method_parameters.get("PVM_SatTransFreqUnit") == 'unit_hz':
                            freq_list = method_parameters.get('PVM_SatTransFreqValues') # frequency list is formatted differently for CEST Off and On, need to distinguish both cases
                            freq_list = freq_list[0].split(" ")
                            while '' in freq_list:
                                freq_list.remove('')
                            [elem.strip(' ') for elem in freq_list]
                            sat_freq_hz = np.array(freq_list, dtype=float)  
                            ds_temp.SaturationOffsetHz = sat_freq_hz[k]
                            ds_temp.SaturationOffsetPpm =  sat_freq_hz[k] * ds_temp.ImagingFrequency                                               
                                                                                                              
                    outfile = "%s%s.dcm" % (filename_little_endian, str(count))
                    
                    # Save dicoms in separate slices
                    os.chdir(head2)
                    ds_temp.is_little_endian = True
                    ds_temp.is_implicit_VR = False
                    ds_temp.save_as(outfile)
                    count +=1
                    k +=1    
                    ii +=1
                        
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

