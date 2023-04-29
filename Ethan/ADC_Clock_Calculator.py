# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 18:51:43 2023

@author: Ethan
"""

sr = 100000
cycles = 12
st = [3, 15, 28, 56, 84, 112, 144, 480]

for time in st:
    ADC_CLK = sr*(time + cycles)
    
    print(ADC_CLK)

