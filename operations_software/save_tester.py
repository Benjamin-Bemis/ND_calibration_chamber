# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 13:52:24 2026

@author: Calibration Chamber
"""

# This is a test script
import numpy as np
import os
import ni_functions as ni
import te_functions as te
from scipy.io import savemat
import time
import plc_functions as plc
import pyfiglet as figlet
import threading

# Timing Variables
laser_pretrig = 3              # Pretrigger time in seconds
camera_pretrig = 2             # Pretrigger time in seconds
delay = 10                     # Delay time in seconds before collection
measure_duration = 2           # Pressure measurement duration in seconds
sample_rate = int(1e3)         # Sampling rate for omega sensor in hz

trigger_channel = "port1/line0"
omega_channel = "ai0"
mks_channel = "ai3"
channels = {"omega_channel" : "ai0", "mks_channel" : "ai3"}

press_set_pts = np.arange(0,4)
temp_set_pts = np.arange(0,2)

ni.initialize(sample_rate, measure_duration) # initializes pressure variables
te.initialize(measure_duration) # initializes pressure variables


for y in temp_set_pts:
    for x in press_set_pts:
        print(f"Outer loop: {y} , Inner loop: {x}")
        device_name = ni.local_sys()
        
        # threads
        thread1 = threading.Thread(target = ni.pressure_read, args = (device_name, channels, trigger_channel, sample_rate, measure_duration))
        thread2 = threading.Thread(target = te.therm_read_interval, args = (measure_duration,))
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        
        print("Collection has ended:")
        print("="*50)
    
    
        # update values ##########################
        ni.update()
        te.update()    
        print(ni.ni_vars.all_pressure_weightedAvg_kpa)
        

ni.ni_vars.all_pressure_weightedAvg_kpa = np.reshape(ni.ni_vars.all_pressure_weightedAvg_kpa, [len(press_set_pts),len(temp_set_pts)])
ni.ni_vars.all_pressure_weighted_uncert_kpa = np.reshape(ni.ni_vars.all_pressure_weighted_uncert_kpa, [len(press_set_pts),len(temp_set_pts)])
ni.ni_vars.all_times_omega = np.reshape( ni.ni_vars.all_times_omega, [len(press_set_pts),len(temp_set_pts),sample_rate*measure_duration])

# Reshape
# Reshaping the pressure dataset (rehapes to p_pts X t_points X time)
        
ni.ni_vars.all_pressure_weightedAvg_kpa = np.reshape(ni.ni_vars.all_pressure_weightedAvg_kpa, [len(press_set_pts),len(temp_set_pts)])
ni.ni_vars.all_pressure_weighted_uncert_kpa = np.reshape(ni.ni_vars.all_pressure_weighted_uncert_kpa, [len(press_set_pts),len(temp_set_pts)])
ni.ni_vars.all_times_omega = np.reshape( ni.ni_vars.all_times_omega, [len(press_set_pts),len(temp_set_pts),sample_rate*measure_duration])
ni.ni_vars.all_pressure_omega = np.reshape( ni.ni_vars.all_pressure_omega, [len(press_set_pts),len(temp_set_pts),sample_rate*measure_duration])
ni.ni_vars.all_pressure_mks = np.reshape( ni.ni_vars.all_pressure_mks, [len(press_set_pts),len(temp_set_pts),sample_rate*measure_duration])


# Reshaping the te dataset (rehapes to p_pts X t_points X time)

te.te_vars.all_avg_temp = np.reshape(te.te_vars.all_avg_temp, [len(press_set_pts),len(temp_set_pts)])
te.te_vars.all_temps_te = np.reshape(te.te_vars.all_temps_te, [len(press_set_pts),len(temp_set_pts), int(measure_duration/0.2)])
te.te_vars.all_times_te = np.reshape(te.te_vars.all_times_te, [len(press_set_pts),len(temp_set_pts), int(measure_duration/0.2)])

        