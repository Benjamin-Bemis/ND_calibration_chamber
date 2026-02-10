# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 10:57:59 2023

@author: Benjamin Bemis Ph.D Student
Advisor: Thomas Juliano 

This function list defines functions for use with the NIDAQ
"""
import nidaqmx as nidaq
import time
import numpy as np
from scipy.interpolate import interp1d
from scipy.interpolate import CubicSpline # Currently not used

""" 
Notes:

Omega wiring: Black and White wires into AI0

MKS wiring: Brown and Green wires into AI3

"""
class ni_vars:
    """
    This class contains all the pressure data records to be written to file after the chamber has finsihed operation.
    
    Author: Luke Denn 
    Editor: Benjamin Bemis
    Updated: 2/5/2026 
    """
    def __init__(self):
        self.time_vector = None
        self.mks_time_vector = None

        self.pressure_kpa = None
        self.mks_pressure_kpa = None
        self.pressure_kpa_mean = None
        self.mks_pressure_kpa_mean = None
        self.raw_voltage = None
        self.mks_raw_voltage = None

        self.all_times_omega = None
        self.all_times_mks = None
        self.all_pressure_omega = None
        self.all_pressure_mks = None
        self.all_pressure_mean_omega = None
        self.all_pressure_mean_mks = None
        self.all_voltage_omega = [None]
        self.all_voltage_mks = [None]
        self.all_voltage_omega_mean = None
        self.all_voltage_mks_mean = None
        
        self.pressure_combined_kpa = None
        self.pressure_combined_sigma_kpa = None
        self.all_pressure_combined_kpa = None
        self.all_pressure_combined_sigma_kpa = None
        
        self.device_name = local_sys()
        
def initialize():
    """
    This function is used to initilize the class variables for data storage. 
    It can also be used to clear existing data stored in the defined variables.
    
    Author: Luke Denn 
    Editor: Benjamin Bemis
    Updated: 2/4/2026

    Returns
    -------
    None.

    """    

    ni_vars.all_times_omega = np.array([])
    ni_vars.all_pressure_omega = np.array([])
    ni_vars.all_pressure_mean_omega = np.array([])
    ni_vars.all_voltage_omega = np.array([])
    ni_vars.all_voltage_omega_mean = np.array([])
    
    ni_vars.all_times_mks = np.array([])
    ni_vars.all_pressure_mks = np.array([])
    ni_vars.all_pressure_mean_mks = np.array([])
    ni_vars.all_voltage_mks = np.array([])
    ni_vars.all_voltage_mks_mean = np.array([])
    
    ni_vars.all_pressure_combined_kpa = np.array([])
    ni_vars.all_pressure_combined_sigma_kpa = np.array([])
    
def update():
    ni_vars.all_times_omega = np.concatenate([ni_vars.all_times_omega, ni_vars.time_vector], axis=0)
    ni_vars.all_pressure_omega = np.concatenate([ni_vars.all_pressure_omega, ni_vars.pressure_kpa], axis=0)
    ni_vars.all_pressure_mean_omega = np.concatenate([ni_vars.all_pressure_mean_omega, np.array([ni_vars.pressure_kpa_mean])], axis=0)
    ni_vars.all_voltage_omega = np.concatenate([ni_vars.all_voltage_omega, ni_vars.raw_voltage], axis=0)
    
    ni_vars.all_times_mks = np.concatenate([ni_vars.all_times_mks, ni_vars.mks_time_vector], axis=0)
    ni_vars.all_pressure_mks = np.concatenate([ni_vars.all_pressure_mks, ni_vars.mks_pressure_kpa], axis=0)
    ni_vars.all_pressure_mean_mks = np.concatenate([ni_vars.all_pressure_mean_mks, np.array([ni_vars.mks_pressure_kpa_mean])], axis=0)
    ni_vars.all_voltage_mks = np.concatenate([ni_vars.all_voltage_mks, ni_vars.mks_raw_voltage], axis=0)
    
    ni_vars.all_voltage_omega_mean = np.concatenate([ni_vars.all_voltage_omega_mean, np.array([np.mean(ni_vars.raw_voltage)])], axis=0)
    ni_vars.all_voltage_mks_mean = np.concatenate([ni_vars.all_voltage_mks_mean, np.array([np.mean(ni_vars.mks_raw_voltage)])], axis=0)
    
    ni_vars.all_pressure_weightedAvg_kpa = np.concatenate([ni_vars.all_pressure_combined_kpa, np.array([ni_vars.pressure_combined_kpa])], axis=0)
    ni_vars.all_pressure_weighted_uncert_kpa = np.concatenate([ni_vars.all_pressure_combined_sigma_kpa, np.array([ni_vars.pressure_combined_sigma_kpa])], axis=0)

        
# DAQ Functions 
def local_sys():
    """
    NIDAQ function for use with the USB DAQs
    purpose: accurate caputure of device information
    inputs: device 
    outputs: device_name

    """
    system = nidaq.system.System.local()

    for device in system.devices:
        device_name = device.name
    
    return(device_name)



def record(device_name, channel,trigger_channel, sample_rate, duration):
    """
    NIDAQ function for use with the USB DAQs
    purpose: opens channels on DAQ for recording in the continous mode. Records data for the specified duration at the specified sample rate. 
    inputs: device 
    outputs: device_name

    """
    with nidaq.Task() as task:
        if type(channel)==dict: # example -> channels = {"ai0" : "omega_channel" ,  "ai3" : "mks_channel" }
            for key in channel.keys():
                task.ai_channels.add_ai_voltage_chan(f"{device_name}/{channel[key]}",max_val=10.0,min_val=0.0)
                task.timing.cfg_samp_clk_timing(sample_rate,sample_mode=nidaq.constants.AcquisitionType.CONTINUOUS)
                # task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source=f"{device_name}/{trigger_channel}",trigger_edge=nidaq.constants.Edge.RISING)
            index = int(duration * sample_rate)
            time_vector = np.arange(0, duration, 1/sample_rate)
            data = task.read(number_of_samples_per_channel=index)
        else:
            
            task.ai_channels.add_ai_voltage_chan(f"{device_name}/{channel}",max_val=10.0,min_val=0.0)
            task.timing.cfg_samp_clk_timing(sample_rate,sample_mode=nidaq.constants.AcquisitionType.CONTINUOUS)
            # task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source=f"{device_name}/{trigger_channel}",trigger_edge=nidaq.constants.Edge.RISING)
            index = int(duration * sample_rate)
            time_vector = np.arange(0, duration, 1/sample_rate)
            data = task.read(number_of_samples_per_channel=index)
            
        task.stop()
        # task.clear()
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
    balance = 0.061                 #balenced at 0 bar
    sensitive = 1/10.095              #V/bar
    sens_uncert = 0.0008*101325            # From data sheet the accuracy of the sensor is +-0.08% of FS (Full Scale is 101325)

    # test = [np.abs(x)*10 for x in test]
    pressure_bar = [(sensitive*x + balance) for x in test]
    pressure_kpa = [x*1e2 -4.9 for x in pressure_bar]
    # pressure_bar_mean = np.mean(pressure_bar)
    pressure_kpa_mean = np.mean(pressure_kpa)
    raw_voltage = test
    
    ni_vars.time_vector = time_vector
    ni_vars.pressure_kpa = pressure_kpa
    ni_vars.pressure_kpa_mean = pressure_kpa_mean
    ni_vars.raw_voltage = raw_voltage
    ni_vars.uncertainty_omega_pa = sens_uncert 
    
    
    return [time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage]

  

def mks_read(device_name, channel, trigger_channel, sample_rate, measure_duration):
    test, time_vector = record(device_name, channel, trigger_channel, sample_rate,measure_duration)

    pressure_kpa = []
    # Data from MKS MicroPirani 925 datasheet Analog output calibration Equation 13. : [Pressure (Pa), Voltage (V)]
    # Chosen for its sensitivity from its range from 1 to 100 Torr, outside this range the sensor is not accurate
    data_mks = np.array([
        [1.333E2, 0.1], [6.66E2, 0.5], [1.333E3, 1.0], [6.66E3, 5.0], [1.333E4, 10]
        ])

    cal_p_mks = data_mks[:, 0]
    cal_v_mks = data_mks[:, 1]

    # Calibration interpolation function: Voltage -> Log10(Pressure)
    interp_func = interp1d(cal_v_mks, cal_p_mks, kind='linear', fill_value="extrapolate")

    def get_pressure_mks(v_input):
        pressure = interp_func(v_input)
        return pressure
    
    
    pressure_kpa = [get_pressure_mks(x)*1e-3 for x in test]
    pressure_kpa_mean = np.mean(pressure_kpa) # pressure_kpa
    raw_voltage = test
    
    ni_vars.mks_time_vector = time_vector
    ni_vars.mks_pressure_kpa = pressure_kpa
    ni_vars.mks_pressure_kpa_mean = pressure_kpa_mean
    ni_vars.mks_raw_voltage = raw_voltage
    
    
    
    return [time_vector, pressure_kpa, pressure_kpa_mean, raw_voltage]


def get_weighted_avg_pressure(mks_pressure_pa,omega_pressure_pa):
    
    """
    Combines the two pressure readings based on their uncertainties. 
    Inputs should be in Pascals.
    
    Author: Benjamin Bemis
    Updated: 2/4/2026b
    """
    Torr_to_Pa = 133.322
    FS = 101325 # Full scale range in Pa
    
    # Uncertainties
    sigma_omega = 0.008*FS
    
    p_torr = mks_pressure_pa/Torr_to_Pa
    
    if 5e-4 <= p_torr < 1e-3:
        sigma_mks = 0.1*mks_pressure_pa # 10% of measurement
    elif 1e-3 <= p_torr < 100:
        sigma_mks = 0.05*mks_pressure_pa # 5% of the measurement
    elif p_torr >= 100:
        sigma_mks = 0.25*mks_pressure_pa # 25% of the measurement
    else: 
        sigma_mks = 0.1*mks_pressure_pa # using nearest error for pressures extreme pressures (Not likely to be used)
        
    weight_omega = 1/(sigma_omega**2)
    weight_mks = 1/(sigma_mks**2)
    
    
    if omega_pressure_pa > 10e3: # uses the omega over 10kPa
        p_combined = omega_pressure_pa
        sigma = np.sqrt(1/(weight_omega))
        
    elif omega_pressure_pa < 3e3: # uses the mks under 3kPa
        p_combined = mks_pressure_pa
        sigma = np.sqrt(1/(weight_mks))
        
    else:     # uses a weighted combination in between 3 and 10 kPa
        p_combined = (weight_omega *omega_pressure_pa + weight_mks*mks_pressure_pa) / (weight_mks+weight_omega)
        sigma = np.sqrt(1/(weight_omega+weight_mks))
        
    
    return p_combined, sigma



def pressure_read(device_name, channels, trigger_channel, sample_rate, measure_duration):
    """
    Record voltages on the NI DAQ on both the omega pressure transducer and the MKS vacuum gauge. 
    This function should replace read_omega and read_mks as it should record them in parallel.
    Written by Ben Bemis 1/21/2026
    """
    test, time_vector = record(device_name, channels, trigger_channel, sample_rate,measure_duration)

    #Omega Pressure setup
    balance = 0.061                 #balenced at 0 bar
    sensitive = 1/10.095            #V/bar
    
    # Data from MKS MicroPirani 925 datasheet Analog output calibration Equation 13. : [Pressure (Pa), Voltage (V)]
    # Chosen for its sensitivity from its range from 1 to 100 Torr, outside this range the sensor is not accurate
    data_mks = np.array([
        [1.333E2, 0.1], [6.66E2, 0.5], [1.333E3, 1.0], [6.66E3, 5.0], [1.333E4, 10]
        ])

    cal_p_mks = data_mks[:, 0]
    cal_v_mks = data_mks[:, 1]

    # Calibration interpolation function: Voltage -> Pressure
    spline = CubicSpline(cal_v_mks, cal_p_mks)

    def get_pressure_mks(v_input):
        spline_pressure = spline(v_input)
        return spline_pressure
    
    
    
    # Conversion from voltage to pressure using the factory calibration for the Omega sensor
    omega_pressure_bar = [(sensitive*x + balance) for x in test[0]]
    omega_pressure_kpa = [x*1e2 -4.9 for x in omega_pressure_bar]
    # pressure_bar_mean = np.mean(pressure_bar)
    omega_pressure_kpa_mean = np.mean(omega_pressure_kpa)
    omega_raw_voltage = test[0]
    
    
    # Conversion from voltage to presssure for the MKS
    mks_pressure_kpa = [get_pressure_mks(x)*1e-3 for x in test[1]]
    mks_pressure_kpa_mean = np.mean(mks_pressure_kpa) # pressure_kpa
    mks_raw_voltage = test[1]
    
    
    # Combination of the two pressure transducers
    combined_pressure = []
    sigma = []
    for pt in range(len(test[0])):
        combined_pressure_new, sigma_new = get_weighted_avg_pressure(mks_pressure_kpa[pt]*1e3, omega_pressure_kpa[pt]*1e3)
        combined_pressure = np.append(combined_pressure, combined_pressure_new)
        sigma = np.append(sigma, sigma_new)

        
    
    
    
    # Writing Omega sensor to class
    ni_vars.time_vector = time_vector
    ni_vars.pressure_kpa = omega_pressure_kpa
    ni_vars.pressure_kpa_mean = omega_pressure_kpa_mean
    ni_vars.raw_voltage = omega_raw_voltage

    # Writing MKS to class
    ni_vars.mks_time_vector = time_vector
    ni_vars.mks_pressure_kpa = mks_pressure_kpa
    ni_vars.mks_pressure_kpa_mean = mks_pressure_kpa_mean
    ni_vars.mks_raw_voltage = mks_raw_voltage
    
    # Writing Combined weighted average to class
    ni_vars.pressure_combined_kpa = float(np.mean(combined_pressure*1e-3))
    ni_vars.pressure_combined_sigma_kpa = float(np.mean(sigma*1e-3))
    
