#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 16:28:03 2025

@author: clemence
"""

import numpy as np
import pandas as pd
from datetime import datetime
from lib.i_read import i_read
from lib.import_inlinino_base import import_inlinino_flow
# Assuming that FLOW is the base class for this instrument
class FLOW:
    SAMPLING_FREQUENCY = 1  # Hz, equivalent to the MATLAB constant

    def __init__(self, cfg):
        self.cfg = cfg
        # Initialization based on the config
        self.logger = cfg.get('logger', 'FlowControl')
        self.view_spd_variable = cfg.get('view', {}).get('spd_variable', 'spd')

        # Set defaults based on logger
        if self.logger == 'FlowControl_old':
            self.SWITCH_FILTERED = 0
            self.SWITCH_TOTAL = 1
        else:
            self.SWITCH_FILTERED = 1
            self.SWITCH_TOTAL = 0

        self.split_mode = 'None'  # Default Split method
  
        # Initialize attributes as dictionaries
        self.data = None  # Example: could be a NumPy array or DataFrame
        self.raw = {
            'tsw': None,  # Placeholder, replace with actual data
            'diw': None
        }
        self.bin = {
            'tsw': None,
            'diw': None
        }
        self.qc = {
            'tsw': None,
            'diw': None
        }
        self.bad = {
            'tsw': None,
            'diw': None
        }
        self.suspect = {
            'tsw': None,
            'diw': None
        }
            
  

    def read_raw(self, days2run, force_import, write):
        """Pre-Process: Read raw data for FTH."""
        if self.logger == 'Inlinino_base':
            self.data = i_read(import_inlinino_flow, self.cfg["path_raw"], self.cfg["path_wk"], 
                                    self.cfg["prefix"], days2run, 'Inlinino')
        else:
            raise ValueError(f'FTH: Unknown logger: {self.logger}')


    def apply_user_input(self, user_selection, mode):
        """Correct part of switch data based on user input."""
        print('User input processing...')
        for start, end in user_selection:
            dt_st = datetime.fromtimestamp(start)  # Start date
            dt_end = datetime.fromtimestamp(end)  # End date
            dt = np.arange(dt_st, dt_end, np.timedelta64(1, 's') * (1 / self.SAMPLING_FREQUENCY))

            if not self.data.empty:
                self.data['dt'] = pd.to_datetime(self.data['dt'], unit='s')
                self.data = self.data.loc[~self.data['dt'].duplicated()]
            else:
                raise ValueError(f'{self.model} raw data not loaded')

            # Interpolate flow rate data
            spd_vars = [col for col in self.data.columns if 'spd' in col]
            interp_spd = np.full((len(dt), len(spd_vars)), np.nan)

            for i, spd_var in enumerate(spd_vars):
                interp_spd[:, i] = np.interp(dt, self.data['dt'].values, self.data[spd_var].values)

            # Remove existing data within the selection period
            self.data = self.data.loc[~self.data['dt'].between(start, end)]

            # Adjust the dataframe to include interpolated data
            varnam = ['dt', 'swt', 'spd1', 'spd2']
            if len(varnam) == 3:
                varnam = ['dt', 'swt', 'spd1', 'spd2']
                self.data['spd2'] = np.nan

            # Append the new data based on the mode
            if mode == 'total':
                new_data = pd.DataFrame(np.column_stack([dt, np.ones_like(dt) * self.SWITCH_TOTAL, interp_spd]), columns=varnam)
                self.data = pd.concat([self.data, new_data])
            elif mode == 'filtered':
                new_data = pd.DataFrame(np.column_stack([dt, np.ones_like(dt) * self.SWITCH_FILTERED, interp_spd]), columns=varnam)
                self.data = pd.concat([self.data, new_data])
            else:
                raise ValueError('Unknown mode.')

        self.data = self.data.sort_values(by='dt')
        print('Done')

    # Additional methods like i_read, import_flow_control, etc., should be defined here or inherited from the base class

