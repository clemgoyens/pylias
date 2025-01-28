from datetime import datetime, timedelta

def ReadRaw(self):
    print("Reading raw data...")


def CheckDataStatus(self):
    print("Checking data status...")


def SpectralQC(self, instrument, levels, save_plots=False, variables=None):
    print(f"Performing spectral QC on {instrument} at levels {levels}.")


def QCRef(self):
    print("Performing QC reference.")


def Split(self):
    print("Splitting data into fsw and tsw.")


def AutoQC(self, level):
    print(f"Performing Auto QC at level {level}.")


def Flag(self):
    print("Flagging data...")


def Write(self, level, option):
    print(f"Writing {level} data with option {option}.")


def Calibrate(self):
    print("Calibrating data...")


def visProd_timeseries(self):
    print("Visualizing product time series.")
