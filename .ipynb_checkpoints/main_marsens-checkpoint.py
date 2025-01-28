import numpy as np
import os
from datetime import datetime, timedelta


# Path setup
#os.chdir('/Users/gui/Documents/Python/InLineAnalysis/InLineAnalysis-master')

# Initialize InLineAnalysis
ila = InLineAnalysis('/home/clemence/02_JupyterNotebook/00_Flowthrough/Processing/Inlinanalysispy/cfg/Marsens_cfg.ini')

# Quick config update
ila.cfg['days2run'] = [datetime(2023, 8, 24) + timedelta(days=i) for i in range(1)]
ila.cfg['instruments2run'] = ['FLOW', 'SUVF6244', 'SBE384504970286', 'ACS3']
ila.cfg['parallel'] = float('inf')
ila.cfg['calibrate']['ACS3'] = {"compute_dissolved": False}

# 1. Import raw data
ila.cfg['force_import'] = False
ila.ReadRaw()
ila.CheckDataStatus()

# 2. Auto-synchronise
# Placeholders for Sync operations
print("Synchronizing instruments...")

# 3. QC Reference
ila.cfg['qc']['mode'] = 'load'
ila.cfg['qc']['remove_old'] = False
ila.QCRef()

# 4. Split fsw and tsw
ila.Split()
ila.CheckDataStatus()

# 5. Automatic QC
ila.AutoQC('raw')
ila.CheckDataStatus()

# 6. Bin data
ila.cfg['bin'] = {"skip": []}
print("Binning data...")
ila.CheckDataStatus()

# 7. Flagging
ila.Flag()
ila.CheckDataStatus()

# 8. Interactive QC
ila.cfg['qc']['mode'] = 'ui'
ila.cfg['qc']['global'] = {"view": ['ACS3'], "active": False}
ila.cfg['qc']['specific']['run'] = ['ACS3']
print("Running interactive QC...")
ila.CheckDataStatus()

# 9. Calibrate
ila.cfg['calibrate']['skip'] = ['FLOW', 'TSG', 'ALFA', 'NMEA', 'SBE384504970269', 'SBE384504970286']
ila.cfg['calibrate']['ACS3'] = {
    "filt_method": '25percentil',
    "interpolation_method": 'CDOM',
    "scattering_correction": 'Rottgers2013_semiempirical',
}
ila.Calibrate()
ila.CheckDataStatus()

# 10. Visualization
save_figures = False
ila.SpectralQC('AC', ['prod'], save_plots=save_figures)
ila.visProd_timeseries()

# 11. Write final data
ila.Write('prod', 'part')
ila.Write('raw', 'part')
ila.Write('bin', 'part')
ila.Write('qc', 'part')
