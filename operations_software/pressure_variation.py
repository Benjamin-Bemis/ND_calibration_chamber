# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 13:01:27 2024
Pressure only mode for calibration chamber
@author: Luke Denn

This script initializes and operates the Notre Dame Modular Benchtop Vacuum 
Chamber (MoBVaC) to be operated in PSP AUTO mode. This script modulates
pressure only within the chamber. Camera and Lasers MUST be 
triggered manually (This will be updated soon).  

Please see psp_calibration_controls as the parent code that this code is based
on

Version: 2.0
Updated: 1/22/2026
"""



import numpy as np
import os
from ni_functions import ni
from scipy.io import savemat
import plc_functions as plc
import pyfiglet as figlet

# Timing Variables
laser_pretrig = 3              # Pretrigger time in seconds
camera_pretrig = 2             # Pretrigger time in seconds
delay = 10                     # Delay time in seconds before collection
measure_duration = 2         # Pressure measurement duration in seconds; was 2
sample_rate = int(1e3)         # Sampling rate for omega sensor in hz

# File Export Path
folderPath = os.path.dirname(__file__)
chamberPath = os.path.dirname(folderPath)
savepath = os.path.join(chamberPath, 'LabTesting')

print(figlet.figlet_format("MoBVaC"))                                          # ASCII print out of the chamber name
print(50*"=")
print(figlet.figlet_format("PSP Auto"))     


# Pressure in kpa
while True:
    try:
        init_press_choice = input("How would you like your pressure profile to be generated? Linspace, Manual, or Vector: \n")
        match init_press_choice:
            case"Vector":
                low_press = int(input("Input the lowest pressure in kPa: \n" )) #These must be int for the linspace command
                high_press = int(input("Input the highest pressure in kPa: \n"))
                interval = int(input("Input the interval or step: \n"))
                
                
                press_set_pts = np.arange(low_press, high_press+1, step=interval) # this is the vector of the pressure set points of the regulator
                print(f"The pressure range to be used is {press_set_pts} \n")
            case "Linspace":
                low_press = int(input("Input the lowest pressure in kPa: \n" )) #These must be int for the linspace command
                high_press = int(input("Input the highest pressure in kPa: \n"))
                num_points = int(input("Input the number of points inbetween: \n"))
                
                
                press_set_pts = np.linspace(low_press, high_press, num=num_points) # this is the vector of the pressure set points of the regulator
                print(f"The pressure range to be used is {press_set_pts} \n")
            case "Manual":
                low_press = int(input("Input the lowest pressure in kPa: \n"))
                press_set_pts = [low_press]
                while True:
                    try:
                        additional_pt = float(input("Input additional points or hit enter to end: \n"))
                        press_set_pts.append(additional_pt)
                    except ValueError:
                        print(f"The pressure range to be used is {press_set_pts} \n")
                        break
                                 
            case _:
                print("You have imput an invalid profile.")
        break
    except ValueError:
        print("Nothing entered. Exiting Script \n")
        
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
        
# ==============================================================================  
    
# General setup
# DAQ setup
trigger_channel = "port1/line0"
omega_channel = "ai0"
mks_channel = "ai3"
# mks transducer
channels = {"omega_channel" : "ai0",
            "mks_channel" : "ai3"}


# ==============================================================================
# plc variables (Fill these with the correct registries, i.e.  0 = 400001, 1 = 400002, etc.)
laser = 1           #Modbus register on the plc for the laser 1
camera = 2          #Modbus register on the plc for the camera is 2
register = laser
# ==============================================================================

total_time = np.array([])
new_time = 0

delay = 10                                                                      # Delay time in seconds
pause = np.linspace(1,delay,delay)                                              # Initializing the array to be printed out during the delay print out

# Kulite Balancing - comment in when dealing with Kulites:
    #############################
# mid_range_pressure = (press_set_pts[-1] - press_set_pts[0])/2 + press_set_pts[0]
# DataDic, elapsed_time = plc.run_PLC_Controller(ni, mid_range_pressure, device_name, channels, trigger_channel, sample_rate, measure_duration, register)

# while True:
#     try:
#         move_on = float(input("press enter after kulite is balanced and ready \n"))
#     except ValueError:
#         print('moving on: \n')
#         break
###########################################

ni.initialize() # initializes variables

for p in enumerate(press_set_pts):
    elapsed_time = plc.run_PLC_Controller(ni, p, channels, trigger_channel, sample_rate, measure_duration, register)

    new_time = new_time + elapsed_time/60
    total_time = np.append(total_time, new_time)

# Saving the various arrays from the data collection as .mat files
savemat(os.path.join(savepath, "omega.mat"), {"pressure_kpa": ni.all_pressure_omega,
                                              "pressure_kpa_mean": ni.all_pressure_mean_omega,
                                              "time": ni.all_times_omega,
                                              "voltage_raw": ni.all_voltage_omega,
                                              "p_setpoints": press_set_pts,
                                              "voltage_raw_mean" : ni.all_voltage_omega_mean,
                                              })
                                              
savemat(os.path.join(savepath, "mks.mat"), {
                                              "pressure_mks_kpa": ni.all_pressure_mks,
                                              "pressure_kpa_mks_mean": ni.all_pressure_mean_mks,
                                              "mks_time": ni.all_times_mks,
                                              "voltage_mks_raw": ni.all_voltage_mks,
                                              "voltage_raw_mks_mean" : ni.all_voltage_mks_mean
                                              })

savemat(os.path.join(savepath, "pressure.mat"), {
                                              "all_pressure_kpa": ni.all_pressure_weightedAvg_kpa,
                                              "all_pressure_uncert": ni.all_pressure_weighted_uncert_kpa,
                                              "time": ni.all_times_omega,
                                              })

print("="*50)
print(f"Data has been saved to this directory: {savepath}")
print("="*50)
print("\n")

# #=============================================================================
# #       Completed block for automated camera and laser triggering
# time_elapse = 0
# # print("Turn on the Laser! and prep the camera")
# start = time.time()
# while time_elapse < delay:
#     print(f"You have {(delay)-time_elapse} seconds till collection begins")
#     print(50*"=")
#     time.sleep(1)
#     time_elapse = int(time.time()-start)
#     if delay - time_elapse == laser_pretrig:
#         # plc.ttl_pulse_on(laser,status = "on")
#         print("Laser triggered. \n")
#     elif delay - time_elapse == camera_pretrig:
#             # plc.ttl_pulse(camera, status = "on")
#             print("Camera triggered. \n")

#     # Turning off the camera and the laser
#     # plc.ttl_pulse(laser, status = "off")
#     # plc.ttl_pulse(camera, status = "off")
#     #==============================================================================
