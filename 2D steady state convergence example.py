import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

## assume b = a/2

## let's calculate temperature at halfway point: x = a/2

## pick a point (x,y) = (a/5,2a)
def temp(n):
    summation = ((1-((-1)**n))/n) * (np.sin(n*np.pi/10)*np.sinh(n*np.pi*0.48)) / (np.sinh(n*np.pi/2))
    return summation

n = np.linspace(1, 10, 10)

T0 = 100 

all_temps = []

for nn in n: 
    T = 2*T0/np.pi * temp(nn)
    all_temps.append(T)
    print(T)

print(sum(all_temps))