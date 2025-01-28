#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 15:35:50 2025

@author: clemence
"""

import os
from scipy.io import loadmat
from lib.i_read import i_read
from lib.import_inlinino_base import import_inlinino_acs

class ACS:
    """
    ACS class to handle processing and calibration of ACS instrument data.
    """

    def __init__(self, cfg):
        """
        Initialize an instance of the ACS class.
        :param cfg: Configuration dictionary with required keys.
        """
        self.cfg=cfg

        self.device_file = self.cfg.get('device_file', '')
        if not self.device_file:
            raise ValueError('Missing field device_file.')

        self.lambda_ref = self.cfg.get('lambda_reference', [])
        self.lambda_c = []
        self.lambda_a = []
        self.cal_param = {}
        self.modelG50 = None
        self.modelmphi = None
        self.logger = self.cfg.get('logger', 'Compass_2.1rc_scheduled')


    def read_device_file(self):
        """
        Reads the device file to set wavelengths and calibration parameters.
        """
        # Placeholder for the actual import function
        self.lambda_c, self.lambda_a, self.cal_param = self.import_acs_device_file(self.device_file)
        if not self.lambda_ref:
            self.lambda_ref = self.lambda_a

    def load_htjsetal2021_model(self):
        """
        Loads models for G50 and mphi from Haëntjens et al. 2021.
        """
        self.modelG50 = loadmat('HTJS20_LinearRegression_5features.mat')['model_G50']
        self.modelmphi = loadmat('HTJS20_LinearRegression_5P-mphi.mat')['model_mphi']

    def read_raw(self, days2run, force_import, write):
        """
        Reads raw data using the configured logger.
        :param days2run: List of days to process.
        :param force_import: Force re-import of data.
        :param write: Whether to write processed data.
        """
        self.read_device_file()

        if self.logger == 'Inlinino_base':
            self.data = i_read(import_inlinino_acs, self.cfg["path_raw"], self.cfg["path_wk"], 
                                    self.cfg["prefix"], days2run, 'Inlinino')
        else:
            raise ValueError(f'FTH: Unknown logger: {self.logger}')


    def read_raw_di(self, days2run, force_import, write):
        """
        Reads raw deionized water (DI) data.
        """
        self.read_device_file()

        di_path = self.cfg['path'].get('di', self.cfg['path_raw'])
        logger = self.cfg['di_cfg'].get('logger', 'InlininoACScsv')
        prefix = self.cfg['di_cfg'].get('prefix', f'DIW_ACS_{self.sn}_')

        self.raw = {
            'diw': self.import_data_with_method(logger, days2run, force_import, write, prefix=prefix)
        }

    def calibrate(self, days2run, compute_dissolved, interpolation_method, CDOM, SWT, di_method,
                  scattering_corr, compute_ad_aphi, TSG, min_nb_pts_per_cluster, time_weight_for_cluster):
        """
        Performs calibration based on the specified parameters.
        """
        lambda_params = {'ref': self.lambda_ref, 'a': self.lambda_a, 'c': self.lambda_c}
        SWT_constants = {'SWITCH_FILTERED': SWT.SWITCH_FILTERED, 'SWITCH_TOTAL': SWT.SWITCH_TOTAL}

        self.load_htjsetal2021_model()

        if interpolation_method == 'linear':
            self.prod = self.process_acs_linear(days2run, compute_dissolved, SWT_constants, lambda_params,
                                                di_method, scattering_corr, compute_ad_aphi)
        elif interpolation_method == 'CDOM':
            if not CDOM or not hasattr(CDOM, 'qc') or not CDOM.qc.get('tsw'):
                raise ValueError('No CDOM data loaded: required for CDOM interpolation.')
            self.prod = self.process_acs_cdom(days2run, compute_dissolved, SWT_constants, lambda_params,
                                              CDOM, di_method, scattering_corr, compute_ad_aphi,
                                              TSG, min_nb_pts_per_cluster, time_weight_for_cluster)
        else:
            raise ValueError('Method not supported.')

    # Helper methods
    @staticmethod
    def ensure_directory(path):
        """Ensures the existence of a directory."""
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def import_data_with_method(self, method_name, *args, **kwargs):
        """Placeholder for dynamic import methods."""
        # Replace with actual data import logic.
        pass

    def import_acs_device_file(self, device_file):
        """Placeholder for the ACS device file importer."""
        # Replace with actual logic to parse the device file.
        return [], [], {}

    def process_acs_linear(self, *args, **kwargs):
        """Placeholder for linear interpolation processing."""
        pass

    def process_acs_cdom(self, *args, **kwargs):
        """Placeholder for CDOM interpolation processing."""
        pass
