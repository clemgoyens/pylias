# -*- coding: utf-8 -*-

import os
import pandas as pd
from datetime import datetime, timedelta
import warnings
import pickle  # For saving/loading `.mat` equivalent files
import glob

def i_read(fun, dirname_in, dirname_out, prefix, dt, software, force=False, nowrite=False, verbose=False, 
          read_margin=True, postfix='', parallel_flag=-1, otherarg1=None, otherarg2=None):
    """
    Reads and processes data files based on specific criteria.

    Args:
        fun (function): Function to import and process data.
        dirname_in (str): Directory containing input files.
        dirname_out (str): Directory to save processed files.
        prefix (str): Prefix for file matching.
        dt (list): Start and end datetime objects for data import.
        software (str): Software type to handle different file conventions.
        force (bool): Force re-importing of data even if saved files exist.
        nowrite (bool): Do not write processed data to the output directory.
        verbose (bool): Print verbose output.
        read_margin (bool): Read an extra margin around the time range.
        postfix (str): File extension (e.g., '.csv', '.dat').
        parallel_flag (int): Number of parallel workers (-1 for all available).
        otherarg1, otherarg2: Additional arguments for the import function.

    Returns:
        pd.DataFrame: Processed data for the specified time range.
    """
    
    
    def ensure_directory(path):
        """Ensures the output directory exists."""
        if not os.path.exists(path):
            os.makedirs(path)

    def list_files_from_software(software, dir_in, prefix, dt, postfix):

        """Lists files based on the software type and datetime."""
        if software in {'WetView', 'Compass_2.1rc', 'Compass_2.1rc_scheduled'}:
            file_pattern = f"{prefix}*{postfix}.dat" if software != 'Compass_2.1rc_scheduled_bin' else f"{prefix}*{postfix}.bin"
        elif software == 'Inlinino':
            file_pattern = f"{prefix}*{dt.strftime('%Y%m%d')}*{postfix}.csv"
            print(file_pattern)
        else:
            raise ValueError(f"Software {software} not supported.")
        
        files2read=glob.glob("{}/{}".format(dir_in,file_pattern))
        print(files2read)
        
        return files2read

    def import_file(file, verbose=False):
        """Wrapper to handle import function calls with optional arguments."""
        if verbose:
            print(f"Processing file: {file}")
        if otherarg1 is not None and otherarg2 is not None:
            return fun(file, otherarg1, otherarg2, verbose)
        elif otherarg1 is not None:
            return fun(file, otherarg1, verbose)
        else:
            return fun(file, verbose)

    # Ensure output directory exists
    ensure_directory(dirname_out)

    # Floor datetime to start of the day
    start_dt = datetime(dt[0].year, dt[0].month, dt[0].day)
    end_dt = datetime(dt[1].year, dt[1].month, dt[1].day)

    gdata = pd.DataFrame()
    current_dt = start_dt

    while current_dt <= end_dt:
        # Construct output file name
        fn_out = os.path.join(dirname_out, f"{prefix}{current_dt.strftime('%Y%m%d')}{postfix}.pkl")

        if not force and os.path.exists(fn_out):
            # Load existing processed data
            if verbose:
                print(f"Loading existing file: {fn_out}")
            with open(fn_out, 'rb') as f:
                data = pickle.load(f)
        else:
            # Get list of files for the current date
            files = list_files_from_software(software, dirname_in, prefix, current_dt, postfix)
            if not files:
                warnings.warn(f"No files found for date {current_dt.strftime('%Y-%m-%d')}")
                current_dt += timedelta(days=1)
                continue

            # Import data in parallel
            if verbose:
                print(f"Processing files for {current_dt.strftime('%Y-%m-%d')}")
            data=[fun(i) for i in files]

            # Combine imported data
            data = pd.concat(data) #, ignore_index=True)
            

            # Save processed data if needed            import_inlinino_base(self.cfg["path_raw"])

            if nowrite is True:
                with open(fn_out, 'wb') as f:
                    pickle.dump(data, f)
                if verbose:
                    print(f"Saved file: {fn_out}")

        # Add data to global dataset
        gdata = pd.concat([gdata, data]) #, ignore_index=True)

        # Increment date
        current_dt += timedelta(days=1)

    # # Handle read margins if specified
    # if read_margin:
    #     margin_days = timedelta(days=1)
    #     if verbose:
    #         print("Reading margins...")
    #     pre_data = iRead(fun, dirname_in, dirname_out, prefix, [start_dt - margin_days], software, 
    #                      force, nowrite, verbose, False, postfix, parallel_flag, otherarg1, otherarg2)
    #     post_data = iRead(fun, dirname_in, dirname_out, prefix, [end_dt + margin_days], software, 
    #                       force, nowrite, verbose, False, postfix, parallel_flag, otherarg1, otherarg2)

    #     if not pre_data.empty:
    #         gdata = pd.concat([pre_data, gdata], ignore_index=True)
    #     if not post_data.empty:
    #         gdata = pd.concat([gdata, post_data], ignore_index=True)

    return gdata
