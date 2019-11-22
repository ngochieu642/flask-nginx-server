import pandas as pd
import numpy as np

def fromString_toInt64(inputTimeString):
    '''
    Converts a time string to int64
    '''
    timeStamp = pd.to_datetime(inputTimeString)
    time64 = np.datetime64(timeStamp)
    return (time64.astype('uint64') / 1e6).astype('uint32')

def time2Int(timeStamp):
    '''
    This function convert TimeStamp to uint32
    '''
    time64 = np.datetime64(timeStamp)
    return (time64.astype('uint64') / 1e6).astype('uint32')