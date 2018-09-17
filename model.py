# This class contains:
# 1) The resistivity model
# 2) The results of the foward modeling with em1dtmfwd.exe (obs files for V and B)
# 3) A method to load a specific model from the MdlemAll folder.
# 4) 

import numpy as np
import pandas as pd

class Model(object):

    def __init__(self):
        self.df = pd.DataFrame()

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
            position_index = 0
            skiped_lines = 5
            measlist = []
            for line in file:
                #print(line)
                if line_index >= skiped_lines:
                    #Get the position
                    if (line_index - skiped_lines) % 91 == 0:
                        if len(measlist) > 0:
                            self.df[label] = pd.Series(measlist)
                        measlist = []
                        sounding_header = line.split()
                        rx_pos = sounding_header[1]
                        rx_dir = sounding_header[4]
                        label = rx_pos + "_" + rx_dir
                        #print(label)
                        position_index += 1
                    else:
                        measurement = float(line.split()[2])
                        #print(measurement)
                        measlist.append(measurement)
                #print(len(measlist))
                line_index += 1

model = Model()
model.parseModel(10, 100, 100, True)
print(model.df.head(n=5))

        

