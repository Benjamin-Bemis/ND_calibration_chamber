# -*- coding: utf-8 -*-
"""

@author: Benjamin Bemis Ph.D Student, 

This script initializes and operates the Notre Dame Modular Benchtop Vacuum Chamber (MoBVaC)

Manual Mode

Version: 0.1 (Ready for hardware test)
Updated: 1/10/2024

"""





"""
To-do list 

- test with chamber to see if any errors are through by the hardware

"""


# import matplotlib.pyplot as plt
import numpy as np
import os
import ni_functions as ni
import te_functions as te
from scipy.io import savemat
import time
import plc_functions as plc
import pyfiglet as figlet

''' 
Package install script

pip install pyModbusTCP
pip install pyfiglet

# Make sure to add this in later
# Note that ni_functions, te_functions, and plc_functions are written by the author
'''

#==============================================================================    
# User defined values: Parsed from the main script


# File Export Path
from argparse import ArgumentParser

parser = ArgumentParser()
print(parser)
parser.add_argument("savepath",type=str)
parser.add_argument("laser_pretrig", type=str)
parser.add_argument("camera_pretrig", type=str)
parser.add_argument("delay", type=str)
parser.add_argument("measure_duration", type=str)
parser.add_argument("sample_rate", type=str)
args = parser.parse_args()
savepath = args.savepath
laser_pretrig = int(args.laser_pretrig)
camera_pretrig = int(args.camera_pretrig)
delay = int(args.delay)
measure_duration = int(args.measure_duration)
sample_rate = int(args.sample_rate)

#============================================================================== 
# #==============================================================================    
# # User defined values: These will be implimented into the GUI eventually


# # File Export Path
# test_series = "PSP_characterization_4_2024/"                               # Make sure to update this line with the name of the tests. Ex. "11_17_23_intensity_tests"
# samples_loaded = "LAM_SIN/"                                                        # Names of the samples loaded into the calibration chamber
# data_folder = "Matlab_exports/"                                                # This is the folder generated to house all the export folders
# base_folder = "C:/Users/17409/OneDrive/Documents/Calibration Chamber Data/"
# savepath = os.path.join(base_folder, (data_folder + test_series + samples_loaded))
# # operation = "C:/Users/17409/Documents/GitHub/nd_research/calibration chamber/operations_software/"
# # os.path.join(operation)
# # Timing Variables
# laser_pretrig = 3              # Pretrigger time in seconds
# camera_pretrig = 2             # Pretrigger time in seconds
# delay = 10                     # Delay time in seconds before collection
# measure_duration = 2           # Pressure measurement duration in seconds
# sample_rate = int(1e3)         # Sampling rate for omega sensor in hz

# #============================================================================== 





#==============================================================================
print(figlet.figlet_format("MoBVaC"))                                          # ASCII print out of the chamber name
print("="*50)
print(figlet.figlet_format("Manual Mode"))
#==============================================================================

    
  
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
        
    
    
'''
Asking the user for the temperature and pressure
'''    
# Temp in Degree C
while True:
    try:
        temp = float(input("Enter the desired temperature (C) or hit the enter key for current temperature: "))
        break
    except ValueError:
        temp = te.set_temp(float(te.therm_read()))
    print(f"The set temperature is {temp} C.\n")

# Pressure in kpa
while True:
    try:
        press = float(input("Enter the desired pressure (kPa) or hit enter for atmospheric pressure: "))
        break
    except ValueError:
        press = float(100) # 1 bar or 100 kpa (Atmospheric Pressure)
    print(f"The set pressure is {press} kPa. \n")
    
    


    
# ==============================================================================  
    
# General setup
# DAQ setup
trigger_channel = "port1/line0"
omega_channel = "ai0"
device_name = ni.local_sys()
# ==============================================================================
# plc variables (Fill these with the correct registries, i.e. 0 = 400000, 1 = 400001, etc.)
laser = 1           #Modbus register on the plc for the laser
camera = 2          #Modbus register on the plc for the camera


# Establish connection to the TE Controller 

# ========================================================

# time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage = ni.omega_read(device_name, omega_channel, trigger_channel, sample_rate, measure_duration)
# print("="*50)
# print(pressure_kpa_mean)
# print("="*50)
# print("\n")

# =====================================================

# =====================================================
# Initializing the save variables
all_times_te = []
all_temps_te = []

all_times_omega_array = np.array([])
all_pressure_omega_array = np.array([])
all_pressure_mean_omega_array = np.array([])
all_voltage_omega_array = np.array([])
all_voltage_omega_mean_array = np.array([])
all_avg_temp = np.array([])

total_time = np.array([])
new_time = 0


print(f"Data for temperature setpoint: {temp} has been begun:")
print("="*50)
print("\n")
times,temps = te.set_output_ss_monitor(temp,interval=0.1,ss_length=2)         # Setting the temperature of the TE and monitoring for steady state contitions over the given length in minutes 


plc.run_PLC_Controller(press, device_name, omega_channel, trigger_channel, sample_rate, measure_duration)                                                    # This is the function that calls the plc to change the pressure from (0-1 Bar)
current_setpoint = plc.view_set_pressure()                             # Read the set pressure from the plc 
print(f"The pressure has been set to {current_setpoint} kPa.")
print("="*50)
print("\n")
time.sleep(15)
#=============================================================================
#       Completed block for automated camera and laser triggering

time_elapse = 0
# print("Turn on the Laser! and prep the camera")
start = time.time()
while time_elapse < delay:
    print(f"You have {(delay)-time_elapse} seconds till collection begins")
    print(50*"=")
    time.sleep(1)
    time_elapse = int(time.time()-start)
    if delay - time_elapse == laser_pretrig:
        plc.ttl_pulse(laser,status = "on")
        print("Laser triggered. \n")
    elif delay - time_elapse == camera_pretrig:
        plc.ttl_pulse(camera, status = "on")
        print("Camera triggered. \n")
      

print("Collection has begun:")
print("="*50)
temp_before_collection = te.therm_read()
time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage = ni.omega_read(device_name, omega_channel, trigger_channel, sample_rate, measure_duration)
temp_after_collection = te.therm_read()
print("Collection has ended:")
print("="*50)

# Turning off the camera and the laser
plc.ttl_pulse(laser, status = "off")
plc.ttl_pulse(camera, status = "off")
#==============================================================================



avg_temp_col = (temp_after_collection+temp_after_collection)/2
all_avg_temp.append(avg_temp_col)
avg_temp_array = np.array(all_avg_temp)

all_times_te.append(times)
all_temps_te.append(temps)
all_times_te_array = np.array(all_times_te)
all_temps_te_array = np.array(all_temps_te)
        
print(f"Data for temperature setpoint: {temp} has been collected")
print("="*50)
print("\n")
time.sleep(3)
    
te.output_enable("off")                                                        # Turns the TE off
print("The TE has been shutoff.")
print("="*50)
print("\n")
        
# Saving the various arrays from the data collection as .mat files       
savemat(os.path.join(savepath, "te.mat"), {"times_te": all_times_te_array, "temps_te": all_temps_te_array, "t_setpoint": temp})
savemat(os.path.join(savepath, "omega.mat"), {"pressure_kpa": all_pressure_omega_array,"pressure_kpa_mean":all_pressure_mean_omega_array,"time": all_times_omega_array,"avg_temp":avg_temp_array,"voltage_raw":all_voltage_omega_array,"p_setpoint": press})
print("="*50)
print(f"Data has been saved to this directory: {savepath}")
print("="*50)
print("\n")

# main()



