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
import ni_functions as ni
from scipy.io import savemat
import time
import plc_functions as plc
import pyfiglet as figlet
import matplotlib.pyplot as plt
import time

# Timing Variables
laser_pretrig = 3              # Pretrigger time in seconds
camera_pretrig = 2             # Pretrigger time in seconds
delay = 10                     # Delay time in seconds before collection
measure_duration = 1         # Pressure measurement duration in seconds; was 2
sample_rate = int(1e3)         # Sampling rate for omega sensor in hz

# File Export Path
folderPath = os.path.dirname(__file__)
chamberPath = os.path.dirname(folderPath)
savepath = os.path.join(chamberPath, 'LabTesting')

print(figlet.figlet_format("MoBVaC"))                                          # ASCII print out of the chamber name
print(50*"=")
print(figlet.figlet_format("PSP Auto"))     


# # Pressure in kpa
# while True:
#     try:
#         init_press_choice = input("How would you like your pressure profile to be generated? Linspace or Manual: \n")
#         match init_press_choice:
#             case "Linspace":
#                 low_press = int(input("Input the lowest pressure in kPa: \n" )) #These must be int for the linspace command
#                 high_press = int(input("Input the highest pressure in kPa: \n"))
#                 num_points = int(input("Input the number of points inbetween: \n"))
                
                
#                 press_set_pts = np.linspace(low_press, high_press, num=num_points) # this is the vector of the pressure set points of the regulator
#                 print(f"The pressure range to be used is {press_set_pts} \n")
#             case "Manual":
#                 low_press = int(input("Input the lowest pressure in kPa: \n"))
#                 press_set_pts = [low_press]
#                 while True:
#                     try:
#                         additional_pt = float(input("Input additional points or hit enter to end: \n"))
#                         press_set_pts.append(additional_pt)
#                     except ValueError:
#                         print(f"The pressure range to be used is {press_set_pts} \n")
#                         break
                                 
#             case _:
#                 print("You have imput an invalid profile.")
#         break
#     except ValueError:
#         print("Nothing entered. Exiting Script \n")
        
# # Initializes the directory for saving the data
# if not os.path.exists(savepath):
#     os.makedirs(savepath)                                                      # Recursively make all directories
#     print(f"Directory: '{savepath}' created.")
#     print("=" * 50)
#     print("\n")
# else:
#     print(f"Directory: '{savepath}' already exists.")
#     print("=" * 50)
#     print("\n")
        
# ==============================================================================  
    
# General setup
# DAQ setup
trigger_channel = "port1/line0"
omega_channel = "ai0"
device_name = ni.local_sys()
# ==============================================================================
# plc variables (Fill these with the correct registries, i.e. 0 = 400000, 1 = 400001, etc.)
laser = 2           #Modbus register on the plc for the laser
camera = 1          #Modbus register on the plc for the camera

# ==============================================================================

# =====================================================
# Initializing the save variables
all_times_omega = []
all_pressure_omega = []
all_pressure_mean_omega = []
all_voltage_omega = []
# =====================================================

delay = 10                                                                      # Delay time in seconds
pause = np.linspace(1,delay,delay)                                              # Initializing the array to be printed out during the delay print out

# calibration operation
press_set_pts = [45] #kpa

for p in press_set_pts:
    start_time = time.time()
    exit_loop = False
    ix = 0
    count = 0
    voltage_percent = plc.get_set_voltage(p, ix)
    plc.set_pressure(voltage_percent)
    time.sleep(15) # 15
    past_pressures = np.array([])
    while not exit_loop:
        time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage = ni.omega_read(device_name, omega_channel, trigger_channel, sample_rate, measure_duration)
        print('last reading: ', str(pressure_kpa_mean))
        if round(pressure_kpa_mean) == p:
            exit_loop = True
            print('pressure successfully set: ', str(pressure_kpa_mean))
            end_time = time.time()
            elapsed_time = end_time - start_time
            mins, secs = divmod(elapsed_time, 60)
            print('time: ', str(mins), ' mins; ', str(int(secs)), ' seconds')
        else:
            Pcrit = 140
            count = count + 1
            
            past_pressures = np.append(past_pressures, pressure_kpa_mean)
            if count > 1:
                if int(past_pressures[-2] == int(pressure_kpa_mean)):
                    count = 1
                    Pcrit = Pcrit*2
                last2Pressures = np.array([past_pressures[-2], past_pressures[-1]])
                t = [1,2]
                temp_vars = last2Pressures - p
                slope, _ = np.polyfit(t, temp_vars, 1)
                ix = ix + int(Pcrit*(p - pressure_kpa_mean))
            else:
                ix = int(Pcrit*(p - pressure_kpa_mean))
            voltage_percent = plc.get_set_voltage(p, ix)
            print('hold on, reseting pressure to be closer to desired pressure')
            plc.set_pressure(voltage_percent)
            time.sleep(15)
        
    all_times_omega.append(time_vector)
    all_pressure_omega.append(pressure_kpa)
    all_pressure_mean_omega.append(pressure_kpa_mean)
    all_voltage_omega.append(raw_voltage)
    
    all_times_omega_array = np.array(all_times_omega)
    all_pressure_omega_array = np.array(all_pressure_omega)
    all_pressure_mean_omega_array = np.array(all_pressure_mean_omega)
    all_voltage_omega_array = np.array(all_voltage_omega)
    
    f = plt.figure(1)
    f.clear()
    plt.plot(time_vector, pressure_kpa)
    plt.xlabel('time')
    plt.ylabel('pressure')
    plt.title('time vs voltage')
    
    # =====================================================
    # Bulk Operation
    # for p in press_set_pts:
    #     plc.set_pressure(p)   # P                                              # This is the function that calls the plc to change the pressure from (0-1 Bar)
    #     current_setpoint = plc.view_set_pressure()                             # Read the set pressure from the plc 
    #     print(f"The pressure has been set to {current_setpoint} kPa.")
    #     print("="*50)
    #     print("\n")     
    #     time.sleep(15)
        
    #     # ========================================================
    #     # Used for testing the DAQ and omega sensor 
    
    #     time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage = ni.omega_read(device_name, omega_channel, trigger_channel, sample_rate, measure_duration)
    #     print("="*50)
    #     print(pressure_kpa_mean)
    #     print("="*50)
    #     print("\n")
    
        # =====================================================

    # all_times_omega.append(time_vector)
    # all_pressure_omega.append(pressure_kpa)
    # all_pressure_mean_omega.append(pressure_kpa_mean)
    # all_voltage_omega.append(raw_voltage)
      
    
    # all_times_omega_array = np.array(all_times_omega)
    # all_pressure_omega_array = np.array(all_pressure_omega)
    # all_pressure_mean_omega_array = np.array(all_pressure_mean_omega)
    # all_voltage_omega_array = np.array(all_voltage_omega)
    
    # f = plt.figure(1)
    # plt.plot(time_vector, pressure_kpa)
    # plt.xlabel('time')
    # plt.ylabel('pressure')
    # plt.title('time vs voltage')

# g = plt.figure(2)
# plt.plot(raw_voltage, pressure_kpa)
# plt.xlabel('voltage')
# plt.ylabel('pressure')
# plt.title('pressure vs voltage')
# g.show()

'''
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
            # plc.ttl_pulse_on(laser,status = "on")
            print("Laser triggered. \n")
        elif delay - time_elapse == camera_pretrig:
                # plc.ttl_pulse(camera, status = "on")
                print("Camera triggered. \n")
    
        # Turning off the camera and the laser
        # plc.ttl_pulse(laser, status = "off")
        # plc.ttl_pulse(camera, status = "off")
        #==============================================================================
        
    # Saving the various arrays from the data collection as .mat files
    savemat(os.path.join(savepath, "omega.mat"), {"pressure_kpa": all_pressure_omega_array,"pressure_kpa_mean":all_pressure_mean_omega_array,"time": all_times_omega_array,"voltage_raw":all_voltage_omega_array,"p_setpoints": press_set_pts})
    print("="*50)
    print(f"Data has been saved to this directory: {savepath}")
    print("="*50)
    print("\n")
    
    # main()
'''