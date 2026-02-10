# -*- coding: utf-8 -*-
"""
Created on 11/3/2023

Author: Benjamin Bemis Ph.D Student

"""
from pyModbusTCP.client import ModbusClient
import numpy as np
import time
import threading
# import logging # Allows console logging for debugging
import scipy

def Psi2kPa(Psi):
    '''
    Pressure conversion, Psi to kPa
    
    Input: Pressure in Psi
    Return: Pressure in kPa
    '''
    kPa = Psi*6.894757
    return kPa

def find_closest_value_index(value, array):
    array = np.asarray(array)
    index = np.abs(array - value).argmin()
    return index

def get_set_voltage(p):  
    """
    Function uses the regulator calibration curve to find the voltage percent to write to the PLC to control the pressure regulator.
    the filepath to the regulator calibration is hard-coded.
    
    inputs: desired pressure
    outputs: pressure, as a percent
    
    """
    
    # specific to regulator, from calibration
    # =========================================================================
    calibration = 'C:/Users/Calibration Chamber/Documents/GitHub/ND_calibration_chamber/operations_software/regulator_calibration/cal_2_5_26.mat'
    data = scipy.io.loadmat(calibration)
    pressure_cal = data.get('mean_combined_kpa')
    voltage_vec = data.get('set_voltage')
    
    pressure_cal = pressure_cal.tolist()
    voltage_vec = voltage_vec.tolist()
    voltages = []
    
    # if np array was 2D, might have to take out the second dimension
    if isinstance(pressure_cal[0],list):
        pressure_cal = pressure_cal[0]
        voltage_vec = voltage_vec[0]
    
    # remove duplicates, always takes first of duplicates
    for idx, value in enumerate(voltage_vec):
        if value not in voltages:
            voltages.append(value)
        else:
            pressure_cal.pop(idx) 
            voltage_vec.pop(idx)
            
    # relationship is linear, inc v -> incr p. interp function requires an increasing function in x
    pressure_cal.sort(reverse = False) # var.sort(reverse = False) Sorts a list to be in accending order
    voltage_vec.sort(reverse = False)
    # =========================================================================
    
    voltage2set = np.interp(p, pressure_cal, voltage_vec)

    return voltage2set


def set_pressure(pressure):
    
    voltage = get_set_voltage(pressure)
    c = ModbusClient(host="169.254.23.198", port=502, unit_id=1, auto_open=True)
    # Open the Modbus connection
    if c.open():
        # Define the Modbus address to write to (400001)
        modbus_address = 0  # Note that Modbus addresses are 0-based, so 400001 becomes 1
    
        # Define the data to write (for example, a single integer value)
        
        data_to_write = int(1000*voltage) # This multiplication is to get three points of percision. 
        # Write the data to the specified Modbus address
        is_success = c.write_single_register(modbus_address, data_to_write)
    
        if is_success:
            # print(f"Successfully wrote {voltage*1e-3} Volts to the PLC. The pressure was set to {place_holder_for_set_pressure}")
            view_set_pressure()
            print("="*50)
            print("\n")
        else:
            print(f"Failed to write to the PLC at: {modbus_address}")
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
    set_point = int(set_point[0])/1000
    print(f"Current Voltage: {set_point/10} V")
    
    # specific to regulator, from calibration
    # =========================================================================
    calibration = 'C:/Users/Calibration Chamber/Documents/GitHub/ND_calibration_chamber/operations_software/regulator_calibration/cal_2_5_26.mat'
    data = scipy.io.loadmat(calibration)
    pressure_cal = data.get('mean_combined_kpa')
    voltage_vec = data.get('set_voltage')
    
    pressure_cal = pressure_cal.tolist()
    voltage_vec = voltage_vec.tolist()
    voltages = []
    
    # if np array was 2D, might have to take out the second dimension
    if isinstance(pressure_cal[0],list):
        pressure_cal = pressure_cal[0]
        voltage_vec = voltage_vec[0]
    
    # remove duplicates, always takes first of duplicates
    for idx, value in enumerate(voltage_vec):
        if value not in voltages:
            voltages.append(value)
        else:
            pressure_cal.pop(idx) 
            voltage_vec.pop(idx)
            
    # relationship is linear, inc v -> incr p. interp function requires an increasing function in x
    pressure_cal.sort(reverse = False) # var.sort(reverse = False) Sorts a list to be in accending order
    voltage_vec.sort(reverse = False)
    # =========================================================================
    p = np.interp(set_point, voltage_vec, pressure_cal)
    c.close()
    
    print(f"Set Pressure: {p} kPa")
    return 

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
        print(f"Successfully wrote: {data_to_write} to PLC")
        print("="*50)
        print("\n")
        
    
    else:
        print("Unable to open Modbus connection")
        print("="*50)
        print("\n")
        
        
        
def runOsciloscope(measure_duration, register):
    ttl_pulse(register, status = "on")
    time.sleep(measure_duration)
    ttl_pulse(register, status = "off")
        
def calibration_chamber_pressure(ni, p, channels, trigger_channel, sample_rate, measure_duration, register):
    """
        Setting pressure from a pressure calibration vector to our pressure regulator
        
        Author: Luke Denn
        Updated: 2/05/2026
        
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
    start_time = time.time()
    device_name = ni.local_sys()
    
    voltage = get_set_voltage(p)
    set_pressure(voltage)
    time.sleep(30) # give the regulator time to act

    # collect data and update data storage
    ni.pressure_read(device_name, channels, trigger_channel, sample_rate, measure_duration)
    ni.update()
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    mins, secs = divmod(elapsed_time, 60)
    print('time: ', str(mins), ' mins; ', str(int(secs)), ' seconds')
    
    return elapsed_time
    
    
def run_PLC_Controller(ni, p, channels, trigger_channel, sample_rate, measure_duration, register):
    
    """
        Solution to controlling the pressure with a uncalibrateable pressure regulator.
        Uses proportional control plus extra logic to set pressure in a timely fashion.
        
        Author: Luke Denn
        Updated: 1/20/2026
        
        OBSOLETE: 2/3/2026 BENJAMIN BEMIS
        
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
    voltage = get_set_voltage(p, ix)
    set_pressure(voltage)
    time.sleep(30) # Time to wait until vacuum settles
    past_pressures = np.array([])
    
    while not exit_loop:
        ni.pressure_read(device_name, channels, trigger_channel, sample_rate, measure_duration) # class system doesn't have arguments returned
        past_pressures = np.append(past_pressures, ni.pressure_weightedAvg_kpa)
        count = count + 1

        print('last reading, omega: ', str(ni.pressure_kpa_mean))
        print('last reading, mks: ', str(ni.mks_pressure_kpa_mean))
        print('weighted pressure reading: ', str(ni.pressure_weightedAvg_kpa))
        
        if np.abs(ni.pressure_weightedAvg_kpa - p) == 0.05:
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
            Pgain = 200
            Dgain = Pgain/3
            Igain = Pgain/8
            
            if count < 1:
                ix = ix + int(Pgain*(p - ni.pressure_weightedAvg_kpa))
            elif count > 1:
                # previous error - 2x prev error = (p - past(-1)) - (p - past(-2) = past(-2) - past(-1)
                slope = past_pressures[-2] - past_pressures[-1] # difference in pressures over iteration, denominator is 1
                ix = Pgain*(p - ni.pressure_weightedAvg_kpa) + slope*Dgain + Igain*np.sum(p-past_pressures)
                print(ix)
                
            voltage = get_set_voltage(p, ix)
            print('hold on, reseting pressure to be closer to desired pressure of ', str(p), ' kPa')
            set_pressure(voltage)
            time.sleep(15)
    
    # only the controller updates the lists from all the set values
    ni.update()
     
    return elapsed_time
