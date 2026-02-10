# -*- coding: utf-8 -*-
"""
Created on Tue Feb  3 14:01:39 2026

Author: Benjamin Bemis
Updated: 2/4/2026

Description: This script is used to calibrate the pressure response of a pressure regulator given a control voltage. 
"""

# Script to get the correct voltage - pressure setpoints

import numpy as np
import os
import ni_functions as ni
# import te_functions as te
from scipy.io import savemat
import time
import plc_functions as plc
import pyfiglet as figlet
import matplotlib.pyplot as plt



# File Export Path
test_series = "reg_calibration/"                               # Make sure to update this line with the name of the tests. Ex. "11_17_23_intensity_tests"
samples_loaded = "test_8/"                                                        # Names of the samples loaded into the calibration chamber
project_folder = "Lockheed_pro/"                                                # This is the folder generated to house all the export folders
base_folder = "C:/Users/Calibration Chamber/Desktop/Data/"
savepath = os.path.join(base_folder, (project_folder + test_series + samples_loaded))


# Initializes the directory for saving the data
if not os.path.exists(savepath):
    os.makedirs(savepath)                                                      # Recursively make all directories
    print(f"Directory: '{savepath}' created.")
    print("=" * 50)
    print("\n")
else:
    print(f"Directory: '{savepath}' already exists.")
    print("=" * 50)
    print("\n")
        


step = 0.25 # Voltage step size

pressures = []
v_cycle = np.array([])
v_percent_down = np.arange(23,12,-step)
v_percent_up = np.arange(12,23.25,step)
v_cycle = np.append(v_cycle,v_percent_down)
v_cycle = np.append(v_cycle,v_percent_up) # Cycles down and then back up through the given voltages. Allows for estimates of hystorisis


# Timing Variables
delay = 10                     # Delay time in seconds before collection
measure_duration = 2           # Pressure measurement duration in seconds
sample_rate = int(1e3)         # Sampling rate for omega sensor in hz

#============================================================================== 
    
# General setup
# DAQ setup
trigger_channel = "port1/line0"
omega_channel = "ai0"
mks_channel = "ai3"
channels = {"omega_channel" : "ai0", "mks_channel" : "ai3"}
# ==============================================================================
# plc variables (Fill these with the correct registries, i.e. 2 = 400001, 3 = 4000002 etc.)
trigger = 1           #Modbus register on the plc for the laser (Modbus Register: 400001)
# ttl_2 = 2          #Modbus register on the plc for the camera (Modbus Register: 400002)
# ==============================================================================


# =====================================================
# Initializing the save variables

ni.initialize() # initializes pressure variables

device_name = ni.local_sys()

for v in v_cycle:
    plc.set_pressure(v)
    if v < 15.5:
        time.sleep(6*delay)
    else:
        time.sleep(delay+5) # this is the time to wait for steady pressure readings. 
        
    ni.pressure_read(device_name, channels, trigger_channel, sample_rate,delay/2)
    
    # Updating output variables
    ni.ni_vars.all_times_omega = np.concatenate([ni.ni_vars.all_times_omega, ni.ni_vars.time_vector], axis=0)
    ni.ni_vars.all_pressure_omega = np.concatenate([ni.ni_vars.all_pressure_omega, ni.ni_vars.pressure_kpa], axis=0)
    ni.ni_vars.all_pressure_mean_omega = np.concatenate([ni.ni_vars.all_pressure_mean_omega, np.array([ni.ni_vars.pressure_kpa_mean])], axis=0)
    ni.ni_vars.all_voltage_omega = np.concatenate([ni.ni_vars.all_voltage_omega, ni.ni_vars.raw_voltage], axis=0)
    
    ni.ni_vars.all_times_mks = np.concatenate([ni.ni_vars.all_times_mks, ni.ni_vars.mks_time_vector], axis=0)
    ni.ni_vars.all_pressure_mks = np.concatenate([ni.ni_vars.all_pressure_mks, ni.ni_vars.mks_pressure_kpa], axis=0)
    ni.ni_vars.all_pressure_mean_mks = np.concatenate([ni.ni_vars.all_pressure_mean_mks, np.array([ni.ni_vars.mks_pressure_kpa_mean])], axis=0)
    ni.ni_vars.all_voltage_mks = np.concatenate([ni.ni_vars.all_voltage_mks, ni.ni_vars.mks_raw_voltage], axis=0)
    
    ni.ni_vars.all_pressure_combined_kpa = np.concatenate([ni.ni_vars.all_pressure_combined_kpa, np.array([ni.ni_vars.pressure_combined_kpa])], axis=0)
    ni.ni_vars.all_pressure_combined_sigma_kpa = np.concatenate([ni.ni_vars.all_pressure_combined_sigma_kpa,np.array([ni.ni_vars.pressure_combined_sigma_kpa])], axis=0)
    
    ni.ni_vars.all_voltage_omega_mean = np.concatenate([ni.ni_vars.all_voltage_omega_mean, np.array([np.mean(ni.ni_vars.raw_voltage)])], axis=0)
    ni.ni_vars.all_voltage_mks_mean = np.concatenate([ni.ni_vars.all_voltage_mks_mean, np.array([np.mean(ni.ni_vars.mks_raw_voltage)])], axis=0)
    

# Saving calibration to savepath    
savemat(os.path.join(savepath, "pressure.mat"), {
                                              "mean_omega_pressure_kpa": ni.ni_vars.all_pressure_mean_omega,
                                              "mean_mks_pressure_kpa": ni.ni_vars.all_pressure_mean_mks,
                                              "mean_combined_kpa": ni.ni_vars.all_pressure_combined_kpa,
                                              "mean_combined_sigma_kpa": ni.ni_vars.all_pressure_combined_sigma_kpa,
                                              "time": ni.ni_vars.all_times_omega,
                                              "set_voltage": v_cycle,
                                              })
print("="*50)
print(f"Data has been saved to this directory: {savepath}")
print("="*50)
print("\n")


# --- Visualization ---
plt.figure(figsize=(8, 5))
# plt.semilogx(pressure, voltage, 'b.-', label='Datasheet Points')
plt.plot(ni.ni_vars.all_pressure_mean_omega, v_cycle, 'bo-', label='Omega Points')
plt.plot(ni.ni_vars.all_pressure_mean_mks, v_cycle, 'go-', label='mks Points')
plt.plot(ni.ni_vars.all_pressure_combined_kpa, v_cycle, 'ro-', label='Combined')
plt.xlabel('Pressure (kPa)')
plt.ylabel('Voltage (V)')
plt.title('Voltage to Pressure Calibration')
plt.grid(True, which="both", ls="-", alpha=0.5)
plt.legend()
plt.show()

plt.figure(figsize=(8, 5))
# plt.semilogx(pressure, voltage, 'b.-', label='Datasheet Points')
plt.semilogx(ni.ni_vars.all_pressure_mean_omega, v_cycle, 'bo-', label='Omega Points')
plt.semilogx(ni.ni_vars.all_pressure_mean_mks, v_cycle, 'go-', label='mks Points')
plt.semilogx(ni.ni_vars.all_pressure_combined_kpa, v_cycle, 'ro-', label='Combined')
plt.xlabel('Pressure (kPa)')
plt.ylabel('Voltage (V)')
plt.title('Voltage to Pressure Calibration')
plt.grid(True, which="both", ls="-", alpha=0.5)
plt.legend()
plt.show()