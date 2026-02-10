# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 15:21:34 2024

@author: Calibration Chamber
"""

# import os
# import sys

# path = os.path.dirname(__file__)
# path = os.path.dirname(path)
# path = os.path.join(path, 'LabTesting')

#     if set_point is None:
#         set_point = int(set_point)/100
#     else:
        
from argparse import ArgumentParser

parser = ArgumentParser(description='description')

parser.add_argument("-x", "--Value", required = True, help = "first value")
parser = vars(parser.parse_args)



'''
    from ni_functions:
        
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
    '''
    
    # from pressure_variation.py: 
    #==============================================================================    
    # User defined values: Parsed from the main script


    # File Export Path
    # from argparse import ArgumentParser

    # parser = ArgumentParser()
    # print(parser)
    # parser.add_argument("savepath",type=str)
    # parser.add_argument("laser_pretrig", type=str)
    # parser.add_argument("camera_pretrig", type=str)
    # parser.add_argument("delay", type=str)
    # parser.add_argument("measure_duration", type=str)
    # parser.add_argument("sample_rate", type=str)
    # args = parser.parse_args()
    # savepath = args.savepath
    # laser_pretrig = int(args.laser_pretrig)
    # camera_pretrig = int(args.camera_pretrig)
    # delay = int(args.delay)
    # measure_duration = int(args.measure_duration)
    # sample_rate = int(args.sample_rate)

    #============================================================================== 
    
    def Psi2kPa(Psi):
        '''
        pressure conversion, Psi to kPa
        '''
        kPa = Psi*6.894757
        return kPa
