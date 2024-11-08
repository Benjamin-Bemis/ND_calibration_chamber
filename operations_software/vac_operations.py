#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: Benjamin Bemis Ph.D Student, 

This script initializes and operates the Notre Dame Pressure and Temperature Controlled Calibration Chamber

Version: 1.0
Updated: 1/15/2024

"""

import subprocess
import os
import pyfiglet as figlet
import time






#==============================================================================    
# User defined values: These will be implimented into the GUI eventually


# File Export Path
test_series = "PSP_characterization_4_2024/"                               # Make sure to update this line with the name of the tests. Ex. "11_17_23_intensity_tests"
data_folder = "Matlab_exports/"                                                # This is the folder generated to house all the export folders
base_folder = "C:/Users/17409/OneDrive/Documents/Calibration Chamber Data/"
savepath = os.path.join(base_folder, (data_folder + test_series))


# Timing Variables
laser_pretrig = 3              # Pretrigger time in seconds
camera_pretrig = 2             # Pretrigger time in seconds
delay = 10                     # Delay time in seconds before collection
measure_duration = 2           # Pressure measurement duration in seconds
sample_rate = int(1e3)         # Sampling rate for omega sensor in hz

#============================================================================== 




"""
To-do list 


-add package install miniscript just below the import block so that the correct packages can be installed

-figure out pressure regulator scaling

-Allow non integer temp set points (will need to be a float to in tranistion) [te_functions_setoutput_ss_moniter]
    -elongate the settling time 

- Manual Mode within psp_auto: Need to be able to set non integers in the first interation of pressure (This is at the beginning of the code when prompting the user) 

-impliment camera control(Add to PLC program)

-impliment laser control(Add to PLC program)

-impliment active heatsink to get to ~15C (Should be controlled through the TC720)
"""




#==============================================================================
print(figlet.figlet_format("Menu"))                                          # ASCII print out of the chamber name
print("="*50)
#==============================================================================


while True:
    try:
        operation = input("What operation mode would you like to run? PSP/TSP Auto, PSP/TSP Int, MANUAL, pressure_variation: \n")
        break
    except ValueError:
        print("Invalid operation.\n")   

start = time.time()
match operation:
    case "PSP/TSP Auto":
        subprocess.run(["python","psp_calibration_controls.py",savepath,str(laser_pretrig),str(camera_pretrig),str(delay),str(measure_duration),str(sample_rate)])
    case "PSP/TSP Int":
        subprocess.run(["python","psp_int.py",savepath,str(laser_pretrig),str(camera_pretrig),str(delay),str(measure_duration),str(sample_rate)])
    case "MANUAL":
        subprocess.run(["python","manual.py",savepath,str(laser_pretrig),str(camera_pretrig),str(delay),str(measure_duration),str(sample_rate)])
    case "pressure_variation":
        subprocess.run(["python","pressure_variation.py",savepath,str(laser_pretrig),str(camera_pretrig),str(delay),str(measure_duration),str(sample_rate)])
    case _:
        print("Invalid operation. \n")
end = time.time()


print(f"{operation} has finished and took {end-start} seconds to complete. \n")