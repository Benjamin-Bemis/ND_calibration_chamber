# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 16:21:22 2023

@author: Benjamin Bemis Ph.D Student
99.87250764300121
(p_range.min(), p_range.max())
"""
from pyModbusTCP.client import ModbusClient
import numpy as np

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
        

     