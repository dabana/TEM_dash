# This class is meant to serve the results of the TEM simulation

import numpy as np
import pandas as pd

class Model(object):

    def __init__(self):
        self._soundings = pd.DataFrame()
        self._rx_positions = []

    def parseModel(self, h1, rho1, rho2, isV):
    # Method to parse a particular observation files (.obs)
        path = "./MdlemAll/"
        if isV:
            filename = "MdlA_" + str(h1) + "_" + str(rho1) + "_" + str(rho2) + "_V"
        else:
            filename = "MdlA_" + str(h1) + "_" + str(rho1) + "_" + str(rho2) + "_B"        
        filename = path + filename + ".obs"

        with open(filename) as file:
            line_index = 0
            skiped_lines = 5
            sounding = []
            timegates = []
            timeGatesRecovered = False
            for line in file:
                # Skip some lines
                if line_index >= skiped_lines:
                    # When a sounding heaer is encountered ...
                    if (line_index - skiped_lines) % 91 == 0:
                        # save the previously read sounding to the soundings dataframe
                        if len(sounding) > 0:
                            self._soundings[label] = pd.Series(sounding)
                            sounding = []
                            timeGatesRecovered = True 
                        # parse the header the sounding
                        sounding_header = line.split()
                        rx_pos = sounding_header[1]
                        rx_dir = sounding_header[4]
                        self._rx_positions.append(float(rx_pos))
                        label = rx_pos + "_" + rx_dir
                    # For any other line ...
                    else:
                        # Recover times gates (done once)
                        if timeGatesRecovered == False:
                            timegates.append(float(line.split()[0]) * 1e6)
                        # Append the data to the sounding
                        sounding.append(float(line.split()[2]))
                line_index += 1
            #Save the last sounding to the soundings dataframe
            if len(sounding) > 0:
                self._soundings[label] = pd.Series(sounding)
            self._soundings['time_us'] = timegates

    def get_X_soundings(self):
    # Method to get the x-component of the offset soundings
        df = self._soundings
        return df[df.columns[2:-1:2]]

    def get_Z_soundings(self):
    # Method to get the z-component of the offset soundings
        df = self._soundings
        return df[df.columns[1:-1:2]]

    def get_inloop_sounding(self):
    # Method to get the z-component of the in-loop sounding
        df = self._soundings
        return df[df.columns[0]]

    def get_timegates(self):
    # Method to get the time vector
        df = self._soundings
        return df[df.columns[-1]].to_frame()
    
    def get_rx_positions(self):
    # Method to get receiver positions (offsets) 
        rx_positions = [str(pos) for pos in self._rx_positions[1::2]]
        return rx_positions

        

