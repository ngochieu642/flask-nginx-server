import json
import numpy as np
import re
import math
import pandas as pd

from . import constant

def extractValue(eachRow):
    for (key, value) in eachRow.items():
        if key == constant.KW_DEVICE_TYPE and value == "PHOTO":
            data = json.loads(eachRow["data"])

            if "photo" in data.keys():
                return data["photo"]
            else:
                return np.nan
        elif key == constant.KW_DEVICE_TYPE and value == "LIGHT":
            data = json.loads(eachRow["data"])

            if "dimmers" in data.keys():
                if type(data["dimmers"]) is list:
                    return data["dimmers"][0]
                else:
                    return data["dimmers"]
            else:
                return np.nan


def getTime64(eachRow, listTime):
    """
    This function return average of value from values of a dict, if key is in listTime. If there
    were no values in eachRow, return None
    """
    listTime64 = []

    for (key, value) in eachRow.items():
        if key in listTime and not math.isnan(value):
            listTime64.append(value)

    if len(listTime64) == 0:
        return None
    else:
        return int(np.average(listTime64))


def int64_2_timeStamp(dataframe):
    """
    This function add column date to dataframe - get from time64 column
    """
    dataframe["date"] = pd.to_datetime(dataframe["time64"], unit="s")


def getDataframe_inRange(dataframe, start_time64, end_time64):
    """
    Get Dataframe that has time64 between start_time64 and end_time64
    """
    # Logs
    print("[data_utils.py]getDataframe_inRange start_time64: ", start_time64)
    print("[data_utils.py]getDataframe_inRange end_time64: ", end_time64)

    return dataframe.loc[
        (dataframe["time64"] >= start_time64) & (dataframe["time64"] <= end_time64)
    ]


def getListOf_time64(listOfNames):
    """
    This functions get all the columns started with time64's name
    """
    list_time64 = []

    for eachName in listOfNames:
        if re.match("^time64", eachName):
            list_time64.append(eachName)
    return list_time64
