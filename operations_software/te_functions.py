# -*- coding: utf-8 -*-
"""
Created on Tue Aug 29 16:23:35 2023


@author: Benjamin Bemis, Ph.D Student
@editer: Luke Denn, AE undergrad in spring of 2026

This script defines communication with the TE Technologies TC-720
https://tetech.com/product/tc-720/

This will house all the TE_control_functions. 

"""

import serial 
from serial.tools.list_ports import comports
import time
import numpy as np

class te_vars:
    def __init__(self):
        self.temp = None
        self.temps = None
        self.times = None
        
        self.all_times_te = None
        self.all_temps_te = None
        self.all_avg_temp = None
        self.comport = None
        
        
def initialize():
    te_vars.all_times_te = np.array([])
    te_vars.all_temps_te = np.array([])
    te_vars.all_avg_temp = np.array([])
    te_vars.comport = get_device()
    
def update(avg_temp_col):
    te_vars.all_avg_temp  = np.concatenate([te_vars.all_avg_temp, np.array([avg_temp_col])], axis=0)
        
    te_vars.all_times_te = np.concatenate([te_vars.all_times_te, np.array([te_vars.times])], axis=0)
    te_vars.all_temps_te = np.concatenate([te_vars.all_temps_te, np.array([te_vars.temps])], axis=0)
        
def get_device(): 
    """
    Author: Benjamin Bemis 
    Updated: 1/30/2026
    
    This function queries the OS serial communication ports to find the TE controller.

    Returns: 
        Hardware communication port as string. 

    """
    target_id = "AQ01WHIEA"
    for port in comports():
        if target_id == port.serial_number:
            # print("Found device located at " f"{port.device}")
            te_vars.comport = port.name
            return port.name
        
    else:
        print("Hardware not found")
        
        
        
def decthex(decimal_number):
   
    hexadecimal_representation = hex(decimal_number*100)[2:]
    hexadecimal_representation = hexadecimal_representation.rjust(4, '0')  # Add leading zeros
    char_list = []
    
    char_list.extend(hexadecimal_representation)
    # char_list.extend(hex_rep)


    return char_list


def TE_command(user_command):
    """

    Parameters
    ----------
    user_command : This is the type of command the user wants to pass to the TE Controller.

    Returns
    -------
    hex_write_command : hexadecimal write command.
    hex_read_command : hexadecimal read command.

    """
    match user_command:
        case "st":          #TE set points 
            hex_write_command = ['1','c']
            hex_read_command = ['5','0']
            
        case "pb":          #Perportional Bandwith
            hex_write_command = ['1','d']
            hex_read_command = ['5','1']
            
        case "ig":          #Integral Gain
            hex_write_command = ['1','e']
            hex_read_command = ['5','2']
            
        case "dg":          #Derivative Gain
            hex_write_command = ['1','f']
            hex_read_command = ['5','3']
            
        case "oe":          # Output Enabled
            hex_write_command = ['3','0']
            hex_read_command = ['6','4']
    
    return hex_write_command, hex_read_command



def TE_checksum(command,setpoint):

    ascii_list = []
    ascii_list.extend(command)
    ascii_list.extend(setpoint)
    
    sum_list = []
    for char in ascii_list:
        # print(char)
        sum_list.append(hex(ord(char))[2:])
    
    checksum = sum(int(char,16) for char in sum_list)
    checksum = hex(checksum)[-2:]
    return checksum

    
def hexc2dec(bufp):
        newval=0
        divvy=4096
        for pn in range (1,5):
                vally=ord(bufp[pn])
                if(vally < 97):
                        subby=48
                else:
                        subby=87
                newval+=((ord(bufp[pn])-subby)*divvy)
                divvy/=16
                if(newval > 32767):
                        newval=newval-65536
        return newval



def therm_read():
    buf=[0,0,0,0,0,0,0,0,0,0,0,0,0] # initializes the read value to be filled by the controller 
    bst=['*','0','1','0','0','0','0','2','1','\r']
    port = get_device()
    # change to the port that is connected to the TC-720 Temperature Controller
    # this is a sample application used to demonstrate the TC-720 serial protocol
    ser=serial.Serial(port, 230400, timeout=1)
    for pn in range(0,10):
            ser.write((bst[pn].encode('utf-8')))
    for pn in range(0,8):
            buf[pn]=ser.read(1)
            # print(buf[pn])
    ser.close()
    te_vars.temp = hexc2dec(buf)/100.0
    
    return te_vars.temp


def set_temp(temp_set_point):
    # temp_set_point must be in C
    setpoint = decthex(temp_set_point)
    command,_ = TE_command("st")
    checksum = TE_checksum(command,setpoint)
    
    bstc=['*']
    bstc.extend(command)
    bstc.extend(setpoint)
    bstc.extend(checksum)
    bstc.extend(['\r']) #write control
    
    port = get_device()
    ser=serial.Serial(port, 230400, timeout=1)
    for pn in range(0,10):
            ser.write((bstc[pn].encode('utf-8')))
            time.sleep(0.004)
    ser.close()
    print(f"Temperature Setpoint: {temp_set_point}")
    print("="*50)
    print("\n")
            
def output_enable(setting):
    match setting:
        case "on":
            setpoint = ['0','0','0','1']
        case "off":
            setpoint = ['0','0','0','0']
        case _:
            setpoint = ['0','0','0','0']
            return "Error: Incorrect command given. TE output set to off for safety."
        
        
    command,_ = TE_command("oe")
    checksum = TE_checksum(command,setpoint)
    
    bstc=['*']
    bstc.extend(command)
    bstc.extend(setpoint)
    bstc.extend(checksum)
    bstc.extend(['\r']) #write control
    buf=[0,0,0,0,0,0,0,0,0,0,0,0,0] # initializes the read value to be filled by the controller 

    port = get_device()
    ser=serial.Serial(port, 230400, timeout=1)
    for pn in range(0,10):
            ser.write((bstc[pn].encode('utf-8')))
            time.sleep(0.004)
    for pn in range(0,8):
            buf[pn]=ser.read(1)
    ser.close()
    

def set_output_ss_monitor(setpoint,interval,ss_length):
    # pid_selector(int(setpoint))
    set_temp(setpoint)
    current_temp = therm_read()
    diff = np.abs(setpoint - current_temp)
    # diff = 1
    output_enable("on")
    print("TE is on")
    print("="*50)
    print("\n")
    counter = 0
    te_vars.temps = []
    length = int((ss_length*60)/interval)
    init = np.linspace(0,length,num=length)
    print(f"Set Point: {setpoint}")
    print("="*50)
    print("\n")
    for x in init:
        # print(counter)
        current_temp = therm_read()
        print(f"\rTemp: {current_temp}",end="",flush=True)
        te_vars.temps.append(current_temp)
        time.sleep(interval)
        counter += 1
        
    data = te_vars.temps[counter - length:counter]       
    sum_data = sum(data)
    avg  = sum_data / length
    # print(f"Moving Average Temperature: {avg}")
    # print("="*50)
    # print("\n")
    diff = np.abs(setpoint - avg) 
    while diff > 0.5:
             # print(counter)
        data = te_vars.temps[counter - length:counter]       
        sum_data = sum(data)
        avg  = sum_data / length
        print(f"\rMoving Average Temperature: {avg}", f" Current Temp: {current_temp}",end="",flush=True)
        # print("="*50)
        # print("\n")
        diff = np.abs(setpoint - avg) 
        
        counter += 1
        current_temp = therm_read()
        # print(current_temp)
        # print("="*50)
        # print("\n")
        te_vars.temps.append(current_temp)

        time.sleep(interval)  
    
    print("\n")
    print(f'Temperature difference: {diff}')
    print("\n")
    print("="*50)
    print("\n")
    print(f"Steady State has been reached: [avg]")    
    print("="*50)
    print("\n")
    te_vars.times = np.linspace(counter - length,counter,num=length)       

        
'''
    original pid code, unused 2/10/2026

    def set_pid_gain(gain):
        #Expects a List of 3 values: [p,i,d]
        gain = [100*x for x in gain]                 #add 2 digits of percision
        commands = ['pb','ig','dg']
        i = 0
        for com in commands:
            setpoint = decthex(int(gain[i]))
            command,_ = TE_command(com)
            checksum = TE_checksum(command,setpoint)
            
            bstc=['*']
            bstc.extend(command)
            bstc.extend(setpoint)
            bstc.extend(checksum)
            bstc.extend(['\r']) #write control
            
            
            ser=serial.Serial('com4', 230400, timeout=1)
            for pn in range(0,10):
                    ser.write((bstc[pn].encode('utf-8')))
                    time.sleep(0.004)
            ser.close()
            # print(bstc) #This line can be used to troublshoot
            bstc = []       #Clear the code that was written to the serial port
            i = i+1
    
    
    def pid_selector(set_point):                                                   # This is a function that sets the proper pid control for the desired setpoint
        approx_set = 5*round(set_point/5)       #Return the nearest case (round to nearest 5)
        match approx_set:
            gain = [20.91,0.8,0.11]             # Designated by Luke
            case 20:
                
                
                gain = [0,0,0]                        # Experimentally chosen [p,i,d] gain
                set_pid_gain(gain)
                return "Using the PID gain for 20 C.\n"
            
            
            # case 25:
                
            #     gain = [0,0,0]                        # Experimentally chosen [p,i,d] gain
            #     set_pid_gain(gain)
            #     return "Using the PID gain for 25 C."
            
            # case 30:
                
            #     gain = [0,0,0]                        # Experimentally chosen [p,i,d] gain
            #     set_pid_gain(gain)
            #     return "Using the PID gain for 30 C."
            
            
            # case 35:
                
                
            #     gain = [0,0,0]                        # Experimentally chosen [p,i,d] gain
            #     set_pid_gain(gain)
            #     return "Using the PID gain for 35 C."
            
            
            # case 40:
                
                
            #     gain = [0,0,0]                        # Experimentally chosen [p,i,d] gain
            #     set_pid_gain(gain)
            #     return "Using the PID gain for 40 C."
            
            
            # case 45:
                
                
            #     gain = [0,0,0]                        # Experimentally chosen [p,i,d] gain
            #     set_pid_gain(gain)
            #     return "Using the PID for 45 C."
            
            
            
            # case 50:
                
                
            #     gain = [0,0,0]                        # Experimentally chosen [p,i,d] gain
            #     set_pid_gain(gain)
            #     return "Using the PID for 50 C."
            
            
            case _:
                return "There is not a set PID for the desired setpoint: {approx_set}"
'''
    
    
    
    
''' Original Code sample from Tetech
# bstc.encode('utf-8')


# read control sensor temp1
bst=['*','0','1','0','0','0','0','2','1','\r'] # characters in this line must be in lowercase
# stx relates to '*'
# the command code is '0','1'
# data being transmitted is '0','0','0','0'
# checksum is '2','1'
# return is '\r'


buf=[0,0,0,0,0,0,0,0,0,0,0,0,0] # initializes the read value to be filled by the controller 


# change to the port that is connected to the TC-720 Temperature Controller
# this is a sample application used to demonstrate the TC-720 serial protocol
ser=serial.Serial('com4', 230400, timeout=1)
for pn in range(0,10):
        ser.write((bstc[pn].encode('utf-8')))
        # customer's have noticed an improved communication from the controller with a 4 millisecond delay
        # this delay is optional, however feel free to attempt it in case of any communication problems
for pn in range(0,8):
        buf[pn]=ser.read(1)
        print(buf[pn])
for pn in range(0,10):
        ser.write((bst[pn].encode('utf-8')))
for pn in range(0,8):
        buf[pn]=ser.read(1)
        print(buf[pn])
ser.close()
temp1=hexc2dec(buf)
print(temp1/100.0) #this prints the current read temperature
wait=input("PORT CLOSED")

'''
        