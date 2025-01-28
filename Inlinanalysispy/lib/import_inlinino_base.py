#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 11:10:55 2025

@author: clemence
"""
import numpy as np
import re
import pandas as pd

def import_inlinino_flow(f):

    df=pd.read_csv(f, header=0, skiprows=1)
    df.columns=["time", "Switch", "Flow(0)"]
    df["Flow(0)"]=df["Flow(0)"].astype(float)
    df["Switch"]=df["Switch"].replace({"True": 1, "False": 0})
    df.index=pd.to_datetime(df.time)
    df=df.drop("time", axis=1)
    df=df.resample('1min').mean() #, origin=df.index[0]).mean()
    df.sort_index(inplace=True)

    return(df)                

def import_inlinino_acs(f,saturationthreshold=34, fillsatvalues=False):
    # % Example: [ data, lambda_a, lambda_c ] = importInlininoACScsv( filename, verbose )

    df=pd.read_csv(f, header=0)
    c_wv=np.array(df.c[0].split("=")[1].split(" ")).astype(float)
    a_wv=np.array(df.a[0].split("=")[1].split(" ")).astype(float)

    time_acs=pd.to_datetime(df.time[1:])

    cvals=pd.DataFrame([np.array(re.sub(r"\[|\]","",re.sub("inf", "99999", df.c[i])).split(), dtype=float) for i in range(1, len(df.c))])
    avals=pd.DataFrame([np.array(re.sub(r"\[|\]","",re.sub("inf", "99999", df.a[i])).split(), dtype=float) for i in range(1, len(df.a))])



    if fillsatvalues is True:
        print("WARNING: values above {} will be filled with interpolated data!!".format(saturationthreshold))

        # Step 1: Identify values above the threshold
        above_threshold = cvals > saturationthreshold

        # Step 2: Replace values above the threshold with NaN
        df_with_nans = cvals.mask(above_threshold)

        # Step 3: Interpolate missing values row-wise (axis=1)
        # We use method='linear' for linear interpolation
        cvals = df_with_nans.interpolate(method='linear', axis=1, limit_direction='both')
        
        # ABSORPTION#
        
        # Step 1: Identify values above the threshold
        above_threshold = avals > saturationthreshold
    
        # Step 2: Replace values above the threshold with NaN
        df_with_nans = avals.mask(above_threshold)
    
        # Step 3: Interpolate missing values row-wise (axis=1)
        # We use method='linear' for linear interpolation
        avals = df_with_nans.interpolate(method='linear', axis=1, limit_direction='both')

    else:
        cvals = pd.DataFrame(np.where((0 <= cvals) & (cvals <= saturationthreshold), cvals, np.nan))
        avals = pd.DataFrame(np.where((0 <= avals) & (avals <= saturationthreshold), avals, np.nan))

    avals.index=time_acs
    avals.columns=a_wv
    cvals.index=time_acs
    cvals.columns=c_wv
    flagbool=df.flag_outside_calibration_range[1:]
    flagbool.index=time_acs
    
    df_combined = pd.concat([avals, cvals, flagbool], axis=1)


    return df_combined