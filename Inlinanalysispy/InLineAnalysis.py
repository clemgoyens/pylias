import configparser
import importlib

# Placeholder class for InLineAnalysis
class InLineAnalysis:
    def __init__(self, config_path):
        self.cfg, self.instruments = self.load_config(config_path)
        

        
    def load_config(self, config_path):
        # Load configuration from the given file (placeholder logic)
        config = configparser.ConfigParser()

        # Read the configuration file
        config.read(config_path)

        cfg = {}
        instruments = {}


        try:
            # Load metadata from the [meta] section
            if 'meta' in config:
                cfg['meta'] = {
                    'investigators': config.get('meta', 'investigators'),
                    'affiliations': config.get('meta', 'affiliations'),
                    'emails': config.get('meta', 'emails', fallback='NA'),
                    'experiment': config.get('meta', 'experiment', fallback='NA'),
                    'cruise': config.get('meta', 'cruise', fallback='NA'),
                    'station': config.get('meta', 'station', fallback='NA'),
                    'documents': config.get('meta', 'documents', fallback='NA'),
                    'calibration_files': config.get('meta', 'calibration_files', fallback='NA'),
                    'data_type': config.get('meta', 'data_type', fallback='flow_thru'),
                    'data_status': config.get('meta', 'data_status', fallback='preliminary'),
                    'measurement_depth': config.getint('meta', 'measurement_depth', fallback=2)
                }
            else:
                print("Warning: No [meta] section found in the configuration file.")
            
            # Load general process settings from the [process] section
            if 'process' in config:
                cfg['days2run'] = config.get('process', 'days2run')
                cfg['instruments2run'] = config.get('process', 'instruments2run').split(',')
                cfg['write'] = config.getboolean('process', 'write')
                cfg['parallel'] = config.getint('process', 'parallel')
                cfg['skip_instruments'] = config.get('process', 'skip').split(',')
            else:
                print("Warning: No [process] section found in the configuration file.")
                
            # Load sync delay from the [sync] section
            if 'sync' in config:
                cfg['sync_delay_flow'] = config.getint('sync', 'delay_FLOW', fallback=10)
            else:
                print("Warning: No [sync] section found in the configuration file.")
            
            # Load QC mode from the [qc] section
            if 'qc' in config:
                cfg['qc_mode'] = config.get('qc', 'mode', fallback='default')
            else:
                print("Warning: No [qc] section found in the configuration file.")
                
            # Accessing calibration settings from the [calibrate] section
            if 'calibrate' in config:
                cfg['calibrate']={}
                cfg['calibrate']['compute_dissolved'] = config.getboolean('calibrate', 'compute_dissolved', fallback=True)
                cfg['calibrate']['skip'] = config.get('calibrate', 'skip')
                cfg['calibrate']['min_nb_pts_per_cluster'] = config.get('calibrate', 'min_nb_pts_per_cluster')
                cfg['calibrate']['time_weight_for_cluster'] = config.get('calibrate', 'time_weight_for_cluster')
                cfg['calibrate']['TSG_source'] = config.get('calibrate', 'TSG_source')
                cfg['calibrate']['CDOM_source'] = config.get('calibrate', 'CDOM_source')
                cfg['calibrate']['interpolation_method'] = config.get('calibrate', 'interpolation_method')
                cfg['calibrate']['di_method'] = config.get('calibrate', 'di_method')
                cfg['calibrate']['scattering_correction'] = config.get('calibrate', 'scattering_correction')
                cfg['calibrate']['compute_ad_aphi'] = config.getboolean('calibrate', 'compute_ad_aphi', fallback=True)
            
            
            else:
                print("Warning: No [calibrate] section found in the configuration file.")
            
            # Initialize each instrument (for the [instruments] section)
            
            # Parse sections for instruments
            for section in config.sections():
                # Check if the section starts with "instruments]["
                if section.startswith("instruments]["):
                    # Extract the instrument name (e.g., sensor1, sensor2)
                    instrument_name = section.split("][")[-1]
            
                    # Parse the instrument-specific configuration
                    instruments[instrument_name] = {
                        'model': config.get(section, 'model', fallback=None),
                        'TSG_source': config.getboolean(section, 'TSG_source', fallback=False),
                        'boat': config.get(section, 'boat', fallback=None),
                        'logger': config.get(section, 'logger', fallback=None),
                        'sn': config.get(section, 'sn', fallback=None),
                        'path_raw': config.get(section, 'path_raw', fallback=None),
                        'path_wk': config.get(section, 'path_wk', fallback=None),
                        'path_prod': config.get(section, 'path_prod', fallback=None),
                        'path_ui': config.get(section, 'path_ui', fallback=None),
                        'view_varname': config.get(section, 'view_varname', fallback=None),
                        'temperature_variable': config.get(section, 'temperature_variable', fallback=None),
                        'device_file': config.get(section, 'device_file', fallback=None),
                        'prefix': config.get(section, 'prefix', fallback=None),

                    }

        except KeyError as e:
            print(f"Error: Missing key in the config file: {e}")
        except Exception as e:
            print(f"Error while loading config: {e}")
            
        return cfg, instruments


    def ReadRaw(self):
        
        # Maybe this piece of code needs to go outside as instrument classes should be called
        # even if raw data is not read
        for instrument_name in self.cfg['instruments2run']:
            try:
                # Dynamically import the instrument class from the /instruments directory
                instrument_module = importlib.import_module(f'instruments.{instrument_name}')
                # Get the class from the module
                instrument_class = getattr(instrument_module, instrument_name)
                # Initialize the instrument class with the corresponding configuration
                self.instruments[instrument_name] = instrument_class(self.instruments[instrument_name])
                print(f"Initialized instrument: {instrument_name}")
            except ModuleNotFoundError:
                raise ValueError(f"Instrument module '{instrument_name}' not found in the instruments directory.")
            except AttributeError:
                raise ValueError(f"Instrument class '{instrument_name}' not found in the module '{instrument_name}.py'.")
        
        """Pre-Process: Read raw data for each instrument."""
        for instrument_name in self.cfg['instruments2run']:
            if instrument_name not in self.instruments:
                raise ValueError(f'Instrument2run "{instrument_name}" does not match any instrument name in the cfg file: '
                                 f'{", ".join(self.instrument.keys())}')
            else:
                print(f'READ RAW: {instrument_name}')
                self.instruments[instrument_name].read_raw(self.cfg['days2run'], self.cfg['force_import'], True)



    def CheckDataStatus(self):
        print('---------------------------------------------------------------------------------------------+')
        print('Instrument |   Data   |   Raw    |   Bin    |   QC     | Suspect  |   Bad    |    Prod       |')
        print('-----------+----------+----------+----------+----------+----------+----------+---------------+')

        for instrument_name in self.cfg['instruments2run']:

            print(self.instruments[instrument_name])
            
            sdata = self.instruments[instrument_name].data.shape
            
            try:
                sraw = self.instruments[instrument_name].raw['tsw'].shape[0] + self.instruments[instrument_name].raw['diw'].shape[0]
            except AttributeError:
                sraw = 0
            
            try:
                sbin = self.instruments[instrument_name].bin['tsw'].shape[0] + self.instruments[instrument_name].bin['diw'].shape[0]
            except AttributeError:
                sbin = 0
            
            try:
                sqc = self.instruments[instrument_name].qc['tsw'].shape[0] + self.instruments[instrument_name].qc['diw'].shape[0]
            except AttributeError:
                sqc = 0
                
            try:
                sbad = self.instruments[instrument_name].bad['tsw'].shape[0] + self.instruments[instrument_name].bad['diw'].shape[0]
            except AttributeError:
                sbad = 0
                
            try:
                ssuspect = self.instruments[instrument_name].suspect['tsw'].shape[0] + self.instruments[instrument_name].suspect['diw'].shape[0]
            except AttributeError:
                ssuspect = 0
            
            sprod = []
            nprod = []

            # Check if 'prod' has any fields
            try:
                if 'prod' in self.instruments[instrument_name]:
                    for t in self.instruments[instrument_name].prod:
                        sprod.append(self.instruments[instrument_name].prod[t].shape)
                        nprod.append(t)
            except:
                "No products yet in {}".format(self.instruments[instrument_name])

            # Prepare the output
            output = f"{instrument_name:10s} | {sdata[0]:5d}x{sdata[1]:2d} | {sraw:5d} | {sbin:5d} | {sqc:5d} | {ssuspect:5d} | {sbad:5d} | "
            
            if not sprod:
                output += 'None          | '
            else:
                for k in range(len(sprod)):
                    output += f"{nprod[k]}({sprod[k][0]:3d}x{sprod[k][1]:2d}) | "

            print(output)
        
        print('---------------------------------------------------------------------------------------------+')
    

    def QCRef(self):
        import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class QCRef:
    def __init__(self, obj):
        self.obj = obj

    def run(self):
        if not hasattr(self.obj.instrument[self.obj.cfg.qcref.view].data, 'dt') or len(self.obj.instrument[self.obj.cfg.qcref.view].data.dt) == 0:
            raise ValueError(f"{self.obj.cfg.qcref.view} data table is empty. Make sure to view the instrument you are trying to process or load your data before running QCRef.")

        mode = self.obj.cfg.qcref.mode
        if mode == 'ui':
            # Round datetime to the nearest second
            flow_data = self.obj.instrument['FLOW'].data
            flow_data['dt'] = np.floor(flow_data['dt']).astype('datetime64[s]')

            # Remove duplicate entries
            _, unique_indices = np.unique(flow_data['dt'], return_index=True)
            duplicate_indices = np.setdiff1d(np.arange(len(flow_data['dt'])), unique_indices)
            flow_data = np.delete(flow_data, duplicate_indices, axis=0)

            # Remove invalid entries
            valid_indices = np.isfinite(flow_data['dt'])
            flow_data = flow_data[valid_indices]

            # GUI-based selection for QC
            fig, ax1 = plt.subplots()
            ax1.set_title('Switch position QC:\nSelect total (t; red) and filtered (f; green) sections.\nPress q to save and quit (close graph to cancel and quit)', fontsize=18)
            ax1.set_ylabel('Switch position', color='k')
            ax1.plot(
                self.obj.instrument[self.obj.cfg.qcref.reference].data.dt,
                self.obj.instrument[self.obj.cfg.qcref.reference].data[self.obj.instrument[self.obj.cfg.qcref.reference].view.varname],
                'k-', linewidth=2
            )
            ax2 = ax1.twinx()
            ax2.scatter(
                self.obj.instrument[self.obj.cfg.qcref.view].data.dt,
                self.obj.instrument[self.obj.cfg.qcref.view].data[self.obj.instrument[self.obj.cfg.qcref.view].view.varname][:, self.obj.instrument[self.obj.cfg.qcref.view].view.varcol],
                label=self.obj.instrument[self.obj.cfg.qcref.view].view.varname
            )

            plt.legend(fontsize=14)
            plt.show()

            # Save selections to a file
            user_selection = {'total': [], 'filtered': []}  # Placeholder for selections from GUI
            save_path = os.path.join(self.obj.instrument[self.obj.cfg.qcref.reference].path.ui, 'QCRef_UserSelection.npy')
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            np.save(save_path, user_selection)

        elif mode == 'load':
            print(f"QCRef LOAD: {self.obj.cfg.qcref.reference}")
            load_path = os.path.join(self.obj.instrument[self.obj.cfg.qcref.reference].path.ui, 'QCRef_UserSelection.npy')
            if os.path.exists(load_path):
                file_selection = np.load(load_path, allow_pickle=True).item()
                days2run = self.obj.cfg.days2run

                # Filter selections based on days2run
                if 'total' in file_selection and len(file_selection['total']) > 0:
                    file_selection['total'] = [entry for entry in file_selection['total'] if not (entry[1] < min(days2run) or entry[0] > max(days2run))]
                if 'filtered' in file_selection and len(file_selection['filtered']) > 0:
                    file_selection['filtered'] = [entry for entry in file_selection['filtered'] if not (entry[1] < min(days2run) or entry[0] > max(days2run))]

                self.obj.instrument[self.obj.cfg.qcref.reference].apply_user_input(file_selection['total'], 'total')
                self.obj.instrument[self.obj.cfg.qcref.reference].apply_user_input(file_selection['filtered'], 'filtered')

        elif mode == 'skip':
            print("WARNING: Reference is not QC.")
        else:
            raise ValueError("Unknown mode.")

        


    
    def calibrate(self):
        # Iterate through instruments to be calibrated (obj.cfg['instruments2run'])
        for instrument_name in self.cfg['instruments2run']:
            if instrument_name in self.cfg['calibrate']['skip']:
                print(f'CALIBRATE: Skip {instrument_name} (copy data to next level)')
                self.instrument[instrument_name]['prod']['a'] = self.instrument[instrument_name]['qc']['tsw']
            else:
                print(f'CALIBRATE: {instrument_name}')

                # Handle instrument class extraction for certain instruments
                if any(key in instrument_name for key in ['AC', 'LISSTTau', 'LISSTTAU', 'LISST-Tau', 'TAU', 'CSTAR', 'BB', 'BB3', 'HBB']):
                    instrument_class = []
                    for instrument in self.instrument:
                        class_name = type(self.instrument[instrument]).__name__  # Get class name
                        instrument_class.append({'instrument': instrument, 'class': class_name})
                
                # Handle CDOM source selection for certain instruments
                if any(key in instrument_name for key in ['AC', 'LISSTTau', 'LISSTTAU', 'LISST-Tau', 'TAU', 'CSTAR']):
                    if (self.cfg['calibrate'][instrument_name]['interpolation_method'] == 'CDOM' and 
                        self.cfg['calibrate'][instrument_name]['CDOM_source']):
                        
                        # Find CDOM table name
                        cdom_tblname = list(self.instrument[self.cfg['calibrate'][instrument_name]['CDOM_source']]['prod'].keys())
                        if not cdom_tblname:
                            # Find another CDOM source from available classes
                            self.cfg['calibrate'][instrument_name]['CDOM_source'] = next(
                                (inst['instrument'] for inst in instrument_class if inst['class'] == 'CD' and
                                 inst['instrument'] != self.cfg['calibrate'][instrument_name]['CDOM_source']),
                                None
                            )
                        else:
                            # Check if the time matches for the CDOM source
                            time_match = (self.instrument[self.cfg['calibrate'][instrument_name]['CDOM_source']]['prod'][cdom_tblname[0]]['dt'] >= min(self.cfg['days2run']) and 
                                          self.instrument[self.cfg['calibrate'][instrument_name]['CDOM_source']]['prod'][cdom_tblname[0]]['dt'] < max(self.cfg['days2run']) + 1)
                            if not any(time_match):
                                self.cfg['calibrate'][instrument_name]['CDOM_source'] = next(
                                    (inst['instrument'] for inst in instrument_class if inst['class'] == 'CD' and
                                     inst['instrument'] != self.cfg['calibrate'][instrument_name]['CDOM_source']),
                                    None
                                )
                        cdom_tblname = list(self.instrument[self.cfg['calibrate'][instrument_name]['CDOM_source']]['prod'].keys())
                        if not cdom_tblname:
                            print('No CDOM data available for CDOM interpolation: using linear interpolation')
                        cdom_source = self.instrument.get(self.cfg['calibrate'][instrument_name].get('CDOM_source'))
                    else:
                        cdom_source = None

                # Handle TSG source selection for calibration
                if any(key in instrument_name for key in ['AC', 'LISSTTau', 'LISSTTAU', 'LISST-Tau', 'TAU', 'CSTAR', 'BB', 'BB3', 'HBB']):
                    if self.cfg['calibrate'][instrument_name].get('TSG_source'):
                        tsg_tblname = list(self.instrument[self.cfg['calibrate'][instrument_name]['TSG_source']]['prod'].keys())
                        if not tsg_tblname:
                            self.cfg['calibrate'][instrument_name]['TSG_source'] = next(
                                (inst['instrument'] for inst in instrument_class if inst['class'] == 'TSG' and
                                 inst['instrument'] != self.cfg['calibrate'][instrument_name]['TSG_source']),
                                None
                            )
                        else:
                            # Check if the time matches for the TSG source
                            time_match = (self.instrument[self.cfg['calibrate'][instrument_name]['TSG_source']]['prod'][tsg_tblname[0]]['dt'] >= min(self.cfg['days2run']) and
                                          self.instrument[self.cfg['calibrate'][instrument_name]['TSG_source']]['prod'][tsg_tblname[0]]['dt'] < max(self.cfg['days2run']) + 1)
                            if not any(time_match):
                                self.cfg['calibrate'][instrument_name]['TSG_source'] = next(
                                    (inst['instrument'] for inst in instrument_class if inst['class'] == 'TSG' and
                                     inst['instrument'] != self.cfg['calibrate'][instrument_name]['TSG_source']),
                                    None
                                )
                        tsg_tblname = list(self.instrument[self.cfg['calibrate'][instrument_name]['TSG_source']]['prod'].keys())
                        if not tsg_tblname:
                            print('No TSG data available for T/S correction: S/T are assumed to be constant')
                        tsg_source = self.instrument.get(self.cfg['calibrate'][instrument_name].get('TSG_source'))
                    else:
                        tsg_source = None

                # Call the calibration function based on the instrument model
                instrument_model = self.instrument[instrument_name]['model']
                if instrument_model == 'AC9':
                    self.instrument[instrument_name].calibrate(self.cfg['days2run'], 
                                                              self.cfg['calibrate'][instrument_name]['compute_dissolved'],
                                                              self.cfg['calibrate'][instrument_name]['interpolation_method'],
                                                              cdom_source,
                                                              self.instrument[self.cfg['calibrate'][instrument_name].get('FLOW_source')],
                                                              self.cfg['calibrate'][instrument_name]['di_method'],
                                                              self.cfg['calibrate'][instrument_name]['scattering_correction'],
                                                              self.cfg['calibrate'][instrument_name]['compute_ad_aphi'],
                                                              tsg_source,
                                                              self.cfg['min_nb_pts_per_cluster'],
                                                              self.cfg['time_weight_for_cluster'])
                elif instrument_model == 'ACS':
                    self.instrument[instrument_name].calibrate(self.cfg['days2run'],
                                                              self.cfg['calibrate'][instrument_name]['compute_dissolved'],
                                                              self.cfg['calibrate'][instrument_name]['interpolation_method'],
                                                              cdom_source,
                                                              self.instrument[self.cfg['calibrate'][instrument_name].get('FLOW_source')],
                                                              self.cfg['calibrate'][instrument_name]['di_method'],
                                                              self.cfg['calibrate'][instrument_name]['scattering_correction'],
                                                              self.cfg['calibrate'][instrument_name]['compute_ad_aphi'],
                                                              tsg_source,
                                                              self.cfg['min_nb_pts_per_cluster'],
                                                              self.cfg['time_weight_for_cluster'])
                elif instrument_model in ['BB', 'BB3', 'HBB']:
                    self.instrument[instrument_name].calibrate(self.cfg['days2run'],
                                                              self.cfg['calibrate'][instrument_name]['compute_dissolved'],
                                                              self.instrument[self.cfg['calibrate'][instrument_name].get('TSG_source')],
                                                              self.instrument[self.cfg['calibrate'][instrument_name].get('FLOW_source')],
                                                              self.cfg['calibrate'][instrument_name]['di_method'],
                                                              self.cfg['calibrate'][instrument_name]['filt_method'])
                elif instrument_model == 'FL':
                    self.instrument[instrument_name].calibrate(self.cfg['days2run'],
                                                              self.cfg['calibrate'][instrument_name]['compute_dissolved'],
                                                              self.instrument[self.cfg['calibrate'][instrument_name].get('FLOW_source')],
                                                              self.cfg['calibrate'][instrument_name]['di_method'],
                                                              self.cfg['calibrate'][instrument_name]['filt_method'])
                elif instrument_model == 'CD':
                    self.instrument[instrument_name].calibrate(self.cfg['calibrate'][instrument_name]['compute_dissolved'])
                elif instrument_model in ['LISST', 'LISST100X', 'LISST100x', 'LISST200X', 'LISST200x']:
                    self.instrument[instrument_name].calibrate(self.cfg['days2run'],
                                                              self.cfg['calibrate'][instrument_name]['compute_dissolved'],
                                                              self.instrument[self.cfg['calibrate'][instrument_name].get('FLOW_source')],
                                                              self.cfg['calibrate'][instrument_name]['di_method'])
                elif instrument_model in ['LISSTTau', 'LISSTTAU', 'LISST-Tau', 'TAU']:
                    self.instrument[instrument_name].calibrate(self.cfg['days2run'],
                                                              self.cfg['calibrate'][instrument_name]['compute_dissolved'],
                                                              self.cfg['calibrate'][instrument_name]['interpolation_method'],
                                                              cdom_source,
                                                              self.instrument[self.cfg['calibrate'][instrument_name].get('FLOW_source')],
                                                              self.cfg['calibrate'][instrument_name]['di_method'])
                else:
                    self.instrument[instrument_name].calibrate()
                    
                    
                    

