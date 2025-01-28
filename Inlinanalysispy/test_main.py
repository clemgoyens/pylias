#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 14:43:01 2025

@author: clemence
"""

# Example usage
if __name__ == "__main__":
    # Example configuration and instrument data
    cfg = {
        'instruments2run': [['Instrument1'], ['Instrument2']]  # List of instruments
    }

    instruments = {
        'Instrument1': {
            'data': pd.DataFrame([[1, 2], [3, 4]]),  # Example data
            'raw': {
                'tsw': pd.DataFrame([[1], [2]]),
                'diw': pd.DataFrame([[3], [4]])
            },
            'bin': {
                'tsw': pd.DataFrame([[5], [6]]),
                'diw': pd.DataFrame([[7], [8]])
            },
            'qc': {
                'tsw': pd.DataFrame([[9], [10]]),
                'diw': pd.DataFrame([[11], [12]])
            },
            'suspect': {
                'tsw': pd.DataFrame([[13], [14]]),
                'diw': pd.DataFrame([[15], [16]])
            },
            'bad': {
                'tsw': pd.DataFrame([[17], [18]]),
                'diw': pd.DataFrame([[19], [20]])
            },
            'prod': {
                'prod1': pd.DataFrame([[21, 22], [23, 24]]),
                'prod2': pd.DataFrame([[25, 26], [27, 28]])
            }
        },
        'Instrument2': {
            'data': pd.DataFrame([[29, 30], [31, 32]]),
            'raw': {
                'tsw': pd.DataFrame([[33], [34]]),
                'diw': pd.DataFrame([[35], [36]])
            },
            'bin': {
                'tsw': pd.DataFrame([[37], [38]]),
                'diw': pd.DataFrame([[39], [40]])
            },
            'qc': {
                'tsw': pd.DataFrame([[41], [42]]),
                'diw': pd.DataFrame([[43], [44]])
            },
            'suspect': {
                'tsw': pd.DataFrame([[45], [46]]),
                'diw': pd.DataFrame([[47], [48]])
            },
            'bad': {
                'tsw': pd.DataFrame([[49], [50]]),
                'diw': pd.DataFrame([[51], [52]])
            }
            # No prod field for this instrument
        }
    }

    manager = InstrumentManager(cfg, instruments)
    manager.check_data_status()