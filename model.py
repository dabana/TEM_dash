# This class contains:
# 1) The resistivity model
# 2) The results of the foward modeling with em1dtmfwd.exe (obs files for V and B)
# 3) A method to load a specific model from the MdlemAll folder.
# 4) 

import numpy as np
import pandas as pd

class Model(object):

    def __init__(self):
        self._soundings = pd.DataFrame()
        self._rx_positions = []

    def parseModel(self, h1, rho1, rho2, isV = True):
        path = "./MdlemAll/"
        if isV:
            filename = "MdlA_" + str(h1) + "_" + str(rho1) + "_" + str(rho2) + "_V"
        else:
            filename = "MdlA_" + str(h1) + "_" + str(rho1) + "_" + str(rho2) + "_B"
        
        #load conductivity model
        filename = path + filename + ".obs"
        with open(filename) as file:
            line_index = 0
            skiped_lines = 5
            sounding = []
            timegates = []
            timeGatesRecovered = False
            for line in file:
                #Skip the first skiped_lines
                if line_index >= skiped_lines:
                    #At the header of each sounding
                    if (line_index - skiped_lines) % 91 == 0:
                        #Save the sounding to the soundings dataframe
                        if len(sounding) > 0:
                            self._soundings[label] = pd.Series(sounding)
                            sounding = []
                            timeGatesRecovered = True 
                        #Recover receiver position and direction
                        sounding_header = line.split()
                        rx_pos = sounding_header[1]
                        rx_dir = sounding_header[4]
                        self._rx_positions.append(float(rx_pos))
                        label = rx_pos + "_" + rx_dir
                    #Save readings to the sounding
                    else:
                        #Recover times gates once
                        if timeGatesRecovered == False:
                            timegates.append(float(line.split()[0]) * 1e6)
                        sounding.append(float(line.split()[2]))
                line_index += 1
            #Save the last sounding to the soundings dataframe
            if len(sounding) > 0:
                self._soundings[label] = pd.Series(sounding)
            self._soundings['time_us'] = timegates
            #self._rx_positions = pd.DataFrame({'rx_pos': self._rx_positions})

    def get_X_soundings(self):
        df = self._soundings
        return df[df.columns[2:-1:2]]

    def get_Z_soundings(self):
        df = self._soundings
        return df[df.columns[1:-1:2]]

    def get_inloop_sounding(self):
        df = self._soundings
        return df[df.columns[0]]

    def get_timegates(self):
        df = self._soundings
        return df[df.columns[-1]]
    
    def get_rx_positions(self):
        rx_positions = [str(pos) for pos in self._rx_positions[1::2]]
        return rx_positions

model = Model()
model.parseModel(10, 100, 100, isV=True)
print(model._soundings.head(n=5))
alist = model.get_rx_positions()
print(alist)
#print(model._soundings.columns)
#print(model.rx_positions)

        

