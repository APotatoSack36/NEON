import numpy
import os
import sys
from datetime import date

class OceanData:
    def __init__(self, blank_array = (0,0,0,0,0)):
        self.data_file_name = "ocean_data\\biweek_{} {}.dat"
        self.blank_array = blank_array
        self.fnum = 0
        self.line_index = 0
        self.checkDupes()
        self.file = numpy.savetxt(self.data_file_name.format(date.today(), self.fnum), blank_array, fmt='%s')

    def dump_odinfo(self, json, img_index):
        od = numpy.loadtxt(self.data_file_name.format(date.today(), self.fnum))
        od = numpy.vstack([od, self.blank_array])
        od[self.line_index][0] = json["temperature"]
        od[self.line_index][1] = json["ph"]
        od[self.line_index][3] = json["light"]
        od[self.line_index][2] = json["salinity"]
        od[self.line_index][4] = img_index
        numpy.savetxt(self.data_file_name.format(date.today(), self.fnum), od, fmt='%s')
        self.line_index += 1

    def checkDupes(self):
        if os.path.isfile(self.data_file_name.format(date.today(), self.fnum)):
            for i in range(10):
                if not os.path.isfile(self.data_file_name.format(date.today(), i)):
                    self.fnum = i
                    return i
            else:
                print("Program has too many duplicate files, ")
                sys.exit()
