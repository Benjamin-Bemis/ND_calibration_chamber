# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 10:57:59 2023

@author: Benjamin Bemis Ph.D Student
Advisor: Thomas Juliano 

This function list defines functions for use with the NIDAQ
"""
import nidaqmx as ni
import time
import numpy as np

""" 
Notes:

Omega wiring: Black and White wires into AI0


"""

# DAQ Functions 
def local_sys():
    # Defines the Daq system and assigns the proper device name
    system = ni.system.System.local()

    for device in system.devices:
        device_name = get_device_info(device)
    return(device_name)



def get_device_info(device):
    """
    NIDAQ function for use with the USB DAQs
    purpose: accurate caputure of device information
    inputs: device 
    outputs: device_name

    """
    
    
    print("=" * 50)
    print(f"Device Name: {device.name}")
    device_name = device.name
    print(f"Product Type: {device.product_type}")
#    print(f"Serial Number: {device.serial_number}")
    print(f"Bus Type: {device.bus_type}")
#    print(f"Device Number: {device.device_number}")
    print(f"Number of AI Channels: {device.ai_physical_chans}")
    print(f"Number of AO Channels: {device.ao_physical_chans}")
    print(f"Number of DI Channels: {device.di_ports}")
    print(f"Number of DO Channels: {device.do_ports}")
    return device_name



def record(device_name, channel,trigger_channel, sample_rate, duration):
    """
    NIDAQ function for use with the USB DAQs
    purpose: opens channel on DAQ for recording in the continous mode. Records data for the specified duration at the specified sample rate. 
    inputs: device 
    outputs: device_name

    """
    with ni.Task() as task:
        task.ai_channels.add_ai_voltage_chan(f"{device_name}/{channel}",max_val=10.0,min_val=-10.0)
        task.timing.cfg_samp_clk_timing(sample_rate,sample_mode=ni.constants.AcquisitionType.CONTINUOUS)
        # task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source=f"{device_name}/{trigger_channel}",trigger_edge=ni.constants.Edge.RISING)
        index = int(duration * sample_rate)
        time_vector = np.arange(0, duration, 1/sample_rate)
        data = task.read(number_of_samples_per_channel=index)
        return data, time_vector


def triggertest (length):
    length = 10
    x = np.linspace(1, length,num=length)
    counter = 1
    for i in x < length:
        print("Loop location:")
        print(counter)
        print("=" * 50)
        
        if counter > 5:
            time.sleep(0.25)
        
        
        
        counter = counter + 1
    # time.sleep(length)
    
# =====================================================
# Functional code for reading Omega Sensor

def omega_read (device_name,omega_channel,trigger_channel,sample_rate,measure_duration):
    test, time_vector = record(device_name, omega_channel, trigger_channel, sample_rate,measure_duration)
    
    #Omega Pressure setup
    balence = 0.061                 #balenced at 0 bar
    sensitive = 1/10.095              #V/bar

    # test = [np.abs(x)*10 for x in test]
    pressure_bar = [(sensitive*x + balence) for x in test]
    pressure_kpa = [x*1e2 -4.9 for x in pressure_bar]
    # pressure_bar_mean = np.mean(pressure_bar)
    pressure_kpa_mean = np.mean(pressure_kpa)
    raw_voltage = test

    # ploting the results
    # plt.plot(time_vector,test)
    # plt.xlabel('Time (s)')
    # plt.ylabel('Voltage (V)')
    # plt.show()
    
    # plt.plot(time_vector,pressure_kpa)
    # plt.xlabel('Time (s)')
    # plt.ylabel('Pressure (kPa)')
    # plt.show()
    
    
    # plt.plot(time_vector,pressure_kpa)
    # plt.xlabel('Time (s)')
    # plt.ylabel('Pressure (kPa)')
    # plt.show()

    return time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage
# =====================================================