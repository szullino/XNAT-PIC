# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:18:01 2018

@author: Sara Zullino
"""
from pydicom.datadict import DicomDictionary, keyword_dict


def add_cest_dict():
    # CEST acquisition
    # Create new tag entries
    new_dict_items = {
        0x10610010: (
            "LO",
            "1",
            "CEST Parameters Creator",
            "",
            "Creator",
        ),  # (data type, multiplicity, tag displayed name, tag keyword)
        0x10611001: (
            "LO",
            "1",
            "Chemical Exchange Saturation Type",
            "",
            "ChemicalExchangeSaturationType",
        ),
        0x10611002: ("LO", "1", "Pulse Type", "", "PulseType"),
        0x10611003: (
            "DS",
            "1",
            "B1 Saturation (μT)",
            "",
            "B1Saturation",
        ),  # (data type, multiplicity, tag displayed name, tag keyword)
        0x10611004: ("DS", "1", "Pulse Duration (ms)", "", "PulseDuration"),
        0x10611005: ("DS", "1", "Pulse Number", "", "PulseNumber"),
        0x10611006: ("DS", "1", "Saturation Length (ms)", "", "SaturationLength"),
        0x10611007: ("DS", "1", "Duty Cycle", "", "DutyCycle"),
        0x10611008: ("DS", "1", "Recovery Time (ms)", "", "RecoveryTime"),
        0x10611009: ("DS", "1", "Measurement Number", "", "MeasurementNumber"),
        0x10611010: ("DS", "1", "Saturation Offset (Hz)", "", "SaturationOffsetHz"),
        0x10611011: ("DS", "1", "Saturation Offset (ppm)", "", "SaturationOffsetPpm"),
        0x10611012: ("LO", "1", "Sampling Type", "", "SamplingType"),
        0x10611013: ('LO', '1', "M0 Option", '', 'M0Option'), 
        0x10611014: ('DS', '1', "M0 Recovery Time", '', 'M0RecoveryTime'),
        0x10611015: ('DS', '1', "Spoiling", '', 'Spoiling'),
        0x10611016: ('DS', '1', "B1 Definition", '', 'B1Definition'),
        0x10611017: ('DS', '1', "TX Reference Voltage", '', 'TxReferenceVoltage'),
    }

    # Update the dictionary itself
    DicomDictionary.update(new_dict_items)

    # Update the reverse mapping from name to tag
    new_names_dict = dict([(val[4], tag) for tag, val in new_dict_items.items()])

    keyword_dict.update(new_names_dict)
