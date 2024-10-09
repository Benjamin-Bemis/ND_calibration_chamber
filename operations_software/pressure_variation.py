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

Version: 1.1
Updated: 2/15/2024
"""
"""
To Do:
    See if stanza highlighted needs to be deleted
    Double check
"""



import numpy as np
import os
from ni_functions import ni
from scipy.io import savemat
import plc_functions as plc
import pyfiglet as figlet
import matplotlib.pyplot as plt

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
                
                
                press_set_pts = np.arange(low_press, high_press+interval, step=interval) # this is the vector of the pressure set points of the regulator
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
device_name = ni.local_sys()
# ==============================================================================
# plc variables (Fill these with the correct registries, i.e. 0 = 400000, 1 = 400001, etc.)
laser = 1           #Modbus register on the plc for the laser was 2
camera = 2          #Modbus register on the plc for the camera was 1
register = laser
# ==============================================================================

# =====================================================
# Initializing the save variables
all_times_omega_array = np.array([])
all_pressure_omega_array =  np.array([])
all_pressure_mean_omega_array =  np.array([])
all_voltage_omega_array =  np.array([])
all_voltage_omega_mean_array = np.array([])
total_time = np.array([])
new_time = 0
# =====================================================

delay = 10                                                                      # Delay time in seconds
pause = np.linspace(1,delay,delay)                                              # Initializing the array to be printed out during the delay print out

for p in press_set_pts:
    OmegaDic, elapsed_time = plc.run_PLC_Controller(ni, p, device_name, omega_channel, trigger_channel, sample_rate, measure_duration, register)
    new_time = new_time + elapsed_time/60
    total_time = np.append(total_time, new_time)
    
    all_times_omega_array = np.append(all_times_omega_array, OmegaDic['all_times_omega_array'])
    all_pressure_omega_array = np.append(all_pressure_omega_array, OmegaDic['all_pressure_omega_array'])
    all_pressure_mean_omega_array = np.append(all_pressure_mean_omega_array, OmegaDic['all_pressure_mean_omega_array'])
    all_voltage_omega_array = np.append(all_voltage_omega_array, OmegaDic['all_voltage_omega_array'])
    all_voltage_omega_mean_array = np.append(all_voltage_omega_mean_array, OmegaDic['all_voltage_omega_mean_array'])
    
    f = plt.figure(1)
    f.clear()
    oscillations = round(np.max(OmegaDic['all_pressure_omega_array'])-np.min(OmegaDic['all_pressure_omega_array']),4)
    plt.plot(all_times_omega_array, all_pressure_omega_array)
    plt.xlabel('time, mins')
    string = 'pressure| range: '+ str(oscillations)
    plt.ylabel(string)
    plt.title('time vs pressure')
    
g = plt.figure(2)
g.clear()
plt.plot(total_time, press_set_pts)
plt.xlabel('time, minutes')
plt.ylabel('set pressure, kPa')
plt.title('system accuracy for pressure readings')
error = [abs(press_set_pts[idx] - value) for idx, value in enumerate(all_pressure_mean_omega_array)]
plt.errorbar(total_time, press_set_pts, yerr = error, xerr = None, marker = 'o')

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
    
# # Saving the various arrays from the data collection as .mat files
# savemat(os.path.join(savepath, "omega.mat"), {"pressure_kpa": all_pressure_omega_array,"pressure_kpa_mean":all_pressure_mean_omega_array,"time": all_times_omega_array,"voltage_raw":all_voltage_omega_array,"p_setpoints": press_set_pts})
# print("="*50)
# print(f"Data has been saved to this directory: {savepath}")
# print("="*50)
# print("\n")
