# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:21:22 2023

@author: Benjamin Bemis Ph.D Student
99.87250764300121
(p_range.min(), p_range.max())
"""
from pyModbusTCP.client import ModbusClient
import numpy as np
import time
import threading

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
    c = ModbusClient(host="169.254.23.198", port=502, unit_id=1, auto_open=True)
    set_point = c.read_holding_registers(0)
    set_point = int(set_point[0])/100
    print('set_point: ', set_point)
    set_pressure_index = find_closest_value_index(set_point, voltage_pt_range)
    print('set_pressure_index: ',str(set_pressure_index))
    c.close()
    return (p_range[set_pressure_index])

def ttl_pulse(register,status):
    c = ModbusClient(host="169.254.23.198", port=502, unit_id=1, auto_open=True)
    
    if c.open():
        # Define the Modbus address to write to (400001)
        modbus_address = register  # Note that Modbus addresses are 0-based, so 400001 becomes 1
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
        
def run_PLC_Controller(ni, p, device_name, omega_channel, trigger_channel, sample_rate, measure_duration, register):
    ni.all_times_omega = []
    ni.all_pressure_omega = []
    ni.all_pressure_mean_omega = []
    ni.all_voltage_omega = []
    ni.all_voltage_omega_mean = []
    # Thread Code
    # ==============================================================================
    thread1 = threading.Thread(target = ni.omega_read, args = (device_name, omega_channel, trigger_channel, sample_rate, measure_duration))
    thread2 = threading.Thread(target = runOsciloscope, args = (measure_duration, register))
    
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
        [time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage] = ni.omega_read(device_name, omega_channel, trigger_channel, sample_rate, measure_duration)
        
        print('last reading: ', str(ni.pressure_kpa_mean))
        if round(ni.pressure_kpa_mean) == p:
            exit_loop = True
            print('pressure successfully set: ', str(ni.pressure_kpa_mean))
            end_time = time.time()
            elapsed_time = end_time - start_time
            mins, secs = divmod(elapsed_time, 60)
            print('time: ', str(mins), ' mins; ', str(int(secs)), ' seconds')
            
            thread1.start()
            thread2.start()
            
            thread1.join()
            thread2.join()

            thread1 = threading.Thread(target = ni.omega_read, args = (device_name, omega_channel, trigger_channel, sample_rate, measure_duration))
            thread2 = threading.Thread(target = runOsciloscope, args = (measure_duration, register))
            
        else:
            Pcrit = 140
            count = count + 1
            
            past_pressures = np.append(past_pressures, ni.pressure_kpa_mean)
            if count > 1:
                if round(past_pressures[-2], 1) == round(ni.pressure_kpa_mean, 1):
                    count = 1
                    Pcrit = Pcrit*2
                last2Pressures = np.array([past_pressures[-2], past_pressures[-1]])
                t = [1,2]
                temp_vars = last2Pressures - p
                slope, _ = np.polyfit(t, temp_vars, 1)
                ix = ix + int(Pcrit*(p - ni.pressure_kpa_mean))
            else:
                ix = int(Pcrit*(p - ni.pressure_kpa_mean))
            voltage_percent = get_set_voltage(p, ix)
            print('hold on, reseting pressure to be closer to desired pressure of ', str(p))
            set_pressure(voltage_percent)
            time.sleep(15)
        
    ni.all_times_omega.append(ni.time_vector)
    ni.all_pressure_omega.append(ni.pressure_kpa)
    ni.all_pressure_mean_omega.append(ni.pressure_kpa_mean)
    ni.all_voltage_omega.append(ni.raw_voltage)
    
    ni.all_voltage_omega_mean.append(np.mean(ni.raw_voltage))
    
    OmegaDic = {'all_times_omega_array' : np.array(ni.all_times_omega),
    'all_pressure_omega_array' : np.array(ni.all_pressure_omega),
    'all_pressure_mean_omega_array' : np.array(ni.all_pressure_mean_omega),
    'all_voltage_omega_array' : np.array(ni.all_voltage_omega),
    'all_voltage_omega_mean_array' : np.array(ni.all_voltage_omega_mean)}
     
    return OmegaDic, elapsed_time