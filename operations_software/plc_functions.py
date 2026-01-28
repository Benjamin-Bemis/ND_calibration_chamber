# -*- coding: utf-8 -*-
"""
Created on 11/3/2023

Author: Benjamin Bemis Ph.D Student

"""
from pyModbusTCP.client import ModbusClient
import numpy as np
import time
import threading
import logging # Allows console logging for debugging

def Psi2kPa(Psi):
    '''
    pressure conversion, Psi to kPa
    
    Proportion air tuned so 1.4100141001410016 V is 50kPa
    Psi2kPa(upper_range + atmospherePressure)
    '''
    kPa = Psi*6.894757
    return kPa

atm = 100 # Psi
upper_range = 500 #psig referenced from the data sheet

#Regulator pressure range in kPa. Note: this is absolute pressure
p_range = np.linspace(-1*Psi2kPa(upper_range)/20, 5.15*Psi2kPa(upper_range)/40, num = 100000)

#voltage_pt_range = np.linspace(0, 10, num = 100000)
voltage_pt_range = np.interp(p_range, (p_range.min(), p_range.max()), (0, 100)) 

def find_closest_value_index(value, array):
    array = np.asarray(array)
    index = np.abs(array - value).argmin()
    return index

def get_set_voltage(pressure, ix):
    index = find_closest_value_index(pressure, p_range)
    return voltage_pt_range[index+ix]


def set_pressure(voltage_percent):
    c = ModbusClient(host="169.254.23.198", port=502, unit_id=1, auto_open=True)
    # Open the Modbus connection
    if c.open():
        # Define the Modbus address to write to (400001)
        modbus_address = 0  # Note that Modbus addresses are 0-based, so 400001 becomes 1
    
        # Define the data to write (for example, a single integer value)
        
        data_to_write = int(100*voltage_percent)
        # Write the data to the specified Modbus address
        is_success = c.write_single_register(modbus_address, data_to_write)
    
        if is_success:
            print(f"Successfully wrote {voltage_percent} to the PLC: Modbus address {modbus_address}")
            print("="*50)
            print("\n")
        else:
            print(f"Failed to write to Modbus address {modbus_address}")
            print("="*50)
            print("\n")
    
        # Close the Modbus connection
        c.close()
    else:
        print("Unable to open Modbus connection")
        print("="*50)
        print("\n")


def view_set_pressure():
    """
    This function queries the PLC for the current set pressure of the regulator.

    Returns
    -------
    Current pressure as a float.
    """
    c = ModbusClient(host="169.254.23.198", port=502, unit_id=1, auto_open=True)
    set_point = c.read_holding_registers(0)
    set_point = int(set_point[0])/100
    print('set_point: ', set_point)
    set_pressure_index = find_closest_value_index(set_point, voltage_pt_range)
    print('set_pressure_index: ',str(set_pressure_index))
    c.close()
    return (p_range[set_pressure_index])

def ttl_pulse(register,status):   
    
    """
    This function turns on and off a 5V signal. This can be used to make a square wave for triggering external devices.
    
    Author: Benjamin Bemis 
    Updated: 1/28/2026
    
    Parameters
    ----------
    register : This is the PLC register number minus 1. Note that Modbus addresses are 0-based, so 400002 becomes 1 (Expected values should be 1 or 2).
    status : 'on' or 'off'. This give either a 0V or 5V.

    Returns
    -------
    No returns. However, there are updates written to the console.


    """
    # Setup of the debugger logging
    # logging.basicConfig()
    # logging.getLogger('pyModbusTCP.client').setLevel(logging.DEBUG)
    
    
    # Base function:    
    c = ModbusClient(host="169.254.23.198", port=502, unit_id=1, auto_open=True)
    
    if c.open(): # this function needs to use the open() command not is_open. They return conflicting booleen logic
        # Define the Modbus address to write to (400001)
        modbus_address = register  # Note that Modbus addresses are 0-based, so 400002 becomes 1
        match status:
            case 'on':
                # Define the data to write (for example, a single integer value)
                data_to_write = 100; # This should write 5V
            
                # Write the data to the specified Modbus address
                is_success = c.write_single_register(modbus_address, data_to_write)
            case 'off':
                # Define the data to write (for example, a single integer value)
                data_to_write = 0; # This should write 0V
            
                # Write the data to the specified Modbus address
                is_success = c.write_single_register(modbus_address, data_to_write)
            case _:
                return "You have asked the plc to do something other than on or off."
        
    
        if is_success:
            print(f"Successfully wrote to the PLC: Modbus address {modbus_address}")
            print("="*50)
            print("\n")
            
        else:
            print(f"Failed to write TTL Pulse to Modbus address {modbus_address}")
            print("="*50)
            print("\n")
    
        # Close the Modbus connection
        c.close()
    else:
        print("Unable to open Modbus connection")
        print("="*50)
        print("\n")
        
def runOsciloscope(measure_duration, register):
    ttl_pulse(register, status = "on")
    time.sleep(measure_duration)
    ttl_pulse(register, status = "off")
        
def run_PLC_Controller(ni, p, channels, trigger_channel, sample_rate, measure_duration, register):
    
    """
        Solution to controlling the pressure with a uncalibrateable pressure regulator.
        Uses proportional control plus extra logic to set pressure in a timely fashion.
        
        Author: Luke Denn
        Updated: 1/20/2026
        
        Arguments:
            ni - this is the class of functions and stored variables belonging to the ni class package created in ni_functions.py
            p - this is a list of the desired set pressures
            channels - this is a dictionary of the channels being used in the 6009 DAQ
            sample_rate - desired sample rate
            measure_duration - this is number of desired points/sample rate
            register - ends up being the modbus address for the oscilloscope
            
        Outputs:
            there are no outputs, because all of the data is populated into the ni class. each row of the data matrix is a set pressure.
            some rows will have 1 column and some will have enough columns per the data points in the measure duration
    """
    device_name = ni.local_sys()

    # Thread Code
    # ==============================================================================
    thread1 = threading.Thread(target = ni.pressure_read, args = (device_name, channels, trigger_channel, sample_rate, measure_duration))
    # thread2 = threading.Thread(target = runOsciloscope, args = (measure_duration, register))
    
    # =====================================================
    start_time = time.time()
    exit_loop = False
    ix = 0
    count = 0
    voltage_percent = get_set_voltage(p, ix)
    set_pressure(voltage_percent)
    time.sleep(15) # 15
    past_pressures = np.array([])
    
    while not exit_loop:
        ni.pressure_read(device_name, channels, trigger_channel, sample_rate, measure_duration) # class system doesn't have arguments returned
        
        print('last reading, omega: ', str(ni.pressure_kpa_mean))
        print('last reading, mks: ', str(ni.mks_pressure_kpa_mean))
        print('weighted pressure reading: ', str(ni.pressure_weightedAvg_kpa))
        
        if round(ni.pressure_weightedAvg_kpa) == round(p):
            exit_loop = True
            print('pressure successfully set: ', str(ni.pressure_weightedAvg_kpa))
            
            # time for the controller to work
            end_time = time.time()
            elapsed_time = end_time - start_time
            mins, secs = divmod(elapsed_time, 60)
            print('time: ', str(mins), ' mins; ', str(int(secs)), ' seconds')
            
            # recollect data, pressure set! this is for use with oscilloscope and other instruments
            thread1.start()
            # thread2.start()
            
            thread1.join()
            # thread2.join()

            
        else:
            Pcrit = 140
            count = count + 1
            
            past_pressures = np.append(past_pressures, ni.pressure_weightedAvg_kpa)
            if count > 1:
                if round(past_pressures[-2], 1) == round(ni.pressure_weightedAvg_kpa, 1):
                    count = 1
                    Pcrit = Pcrit*2
                last2Pressures = np.array([past_pressures[-2], past_pressures[-1]])
                t = [1,2]
                temp_vars = last2Pressures - p
                slope, _ = np.polyfit(t, temp_vars, 1)
                ix = ix + int(Pcrit*(p - ni.pressure_weightedAvg_kpa))
            else:
                ix = int(Pcrit*(p - ni.pressure_weightedAvg_kpa))
            voltage_percent = get_set_voltage(p, ix)
            print('hold on, reseting pressure to be closer to desired pressure of ', str(p), ' kPa')
            set_pressure(voltage_percent)
            time.sleep(15)
    
    # only the controller updates the lists from all the set values
    ni.all_times_omega = np.concatenate([ni.all_times_omega, ni.time_vector], axis=0)
    ni.all_pressure_omega = np.concatenate([ni.all_pressure_omega, ni.pressure_kpa], axis=0)
    ni.all_pressure_mean_omega = np.concatenate([ni.all_pressure_mean_omega, np.array([ni.pressure_kpa_mean])], axis=0)
    ni.all_voltage_omega = np.concatenate([ni.all_voltage_omega, ni.raw_voltage], axis=0)
    
    ni.all_times_mks = np.concatenate([ni.all_times_mks, ni.mks_time_vector], axis=0)
    ni.all_pressure_mks = np.concatenate([ni.all_pressure_mks, ni.mks_pressure_kpa], axis=0)
    ni.all_pressure_mean_mks = np.concatenate([ni.all_pressure_mean_mks, np.array([ni.mks_pressure_kpa_mean])], axis=0)
    ni.all_voltage_mks = np.concatenate([ni.all_voltage_mks, ni.mks_raw_voltage], axis=0)
    
    ni.all_voltage_omega_mean = np.concatenate([ni.all_voltage_omega_mean, np.array([np.mean(ni.raw_voltage)])], axis=0)
    ni.all_voltage_mks_mean = np.concatenate([ni.all_voltage_mks_mean, np.array([np.mean(ni.mks_raw_voltage)])], axis=0)
    
    ni.all_pressure_weightedAvg_kpa = np.concatenate([ni.all_pressure_weightedAvg_kpa, np.array([ni.pressure_weightedAvg_kpa])], axis=0)
    ni.all_pressure_weighted_uncert_kpa = np.concatenate([ni.all_pressure_weighted_uncert_kpa, np.array([ni.pressure_weighted_uncert_kpa])], axis=0)
     
    return elapsed_time

def closed_contact(status):
    '''
    Similar to ttl_pulse, This function is to make a closed contact for triggering external devices.
    
    Author: Benjamin Bemis
    Updated: 1/28/2026
        
    Parameters: 
        status - 'on' or 'off'. 'on' will close the normally open contact. 'off' will reopen it.
        
    Return: 
        Print outs to console, the status of the command sent to the PLC.
    '''
    c = ModbusClient(host="169.254.23.198", port=502, unit_id=1, auto_open=True)
    
    # For the CLICK PLC model: C0-12DRE-D
    modbus_address = 16384  # Note that Modbus addresses are 0-based, so 16384 becomes 16385 or channel y1 
    match status:
        case 'on':
            # Define the data to write (0 or 1)
            data_to_write = 1; # This is writing a 1 bit (1 is a closed true contact)
        
            # Write the data to the specified Modbus address
            is_success = c.write_single_coil(modbus_address, data_to_write)
            print(f"Contact is closed: {modbus_address}")
            print("\n")
        case 'off':
            # Define the data to write (0 or 1)
            data_to_write = 0; # This is writing a 0 bit
        
            # Write the data to the specified Modbus address
            is_success = c.write_single_coil(modbus_address, data_to_write)
            print(f"Contact is open: {modbus_address}")
            print("\n")
        case _:
            return "You have asked the plc to do something other than on or off."
    c.close() # Close the communication port
    
    if is_success:
        print("="*50)
        print(f"Successfully wrote: {data_to_write} to PLC
        print("="*50)
        print("\n")
        
    
    else:
        print("Unable to open Modbus connection")
        print("="*50)
        print("\n")
        
