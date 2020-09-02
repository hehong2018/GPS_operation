#!/usr/bin/env python
# encoding: utf-8
'''
Define some common function
  
Create on 2019-04-24
@author: Hong He
@Change time: 
'''
from __future__ import division
import numpy
import linecache
import os
import decimal
from math import *

decimal.getcontext().prec=16
class GaussianNoiseGPS():

    def __init__(self, file_path, param="Lon&Lat", longitude_accuracy=0.000001, latitude_accuracy=0.000001,
                 altitude_accuracy=1):
        '''
        Initialize object
        :param file_path:Truth gps path
        :param param: gaussian noise parameters "Lon":add noise to longitude,"lat":add noise to latitude,
        "all":add noise to longitude,latitude,and altitude
        :param longitude_accuracy:The variance of gaussian Noise for longitude
        :param latitude_accuracy:The variance of gaussian Noise for latitude
        :param altitude_accuracy:The variance of gaussian Noise for altitude
        '''
        self.path = file_path
        self.param = param
        self.longitude_accuracy = longitude_accuracy
        self.latitude_accuracy = latitude_accuracy
        self.altitude_accuracy = altitude_accuracy


    def __gaussian_noise__(self, truth_value, accuracy=0.000001):
        '''
        Add Gaussian noise to truth value
        :param longtitude_value: Truth value
        :return: Gaussian noise value
        '''
        return str(int(self.wgs2nds(self.__guss_numpy__(self.nds2wgs(int(truth_value)), accuracy))))

    def __gaussian_noise_altitude(self, truth_value, accuracy=1):
        '''
        Add gaussian_noise to altitude
        :param truth_value: Truth value
        :param accuracy: default 1
        :return: int altitude
        '''
        return str(int(self.__guss_numpy__(int(truth_value), accuracy)))

    def __guss_numpy__(self, truth_value, accuracy):
        '''
        Old value add gaussian noise
        :param value:Input value
        :return:Gaussian noise result
        '''
        # scale=0.00001 longitude accuracy 1 meter,latitude accuracy 1.1 meter
        # scale=0.0001 longitude accuracy 10 meter,latitude accuracy 11 meter
        # scale=0.001 longitude accuracy 100 meter,latitude accuracy 111 meter
        # scale=0.01 longitude accuracy 1000 meter,latitude accuracy 1111 meter
        # VTD scale=0.000001
        return truth_value + numpy.random.normal(loc=0.0, scale=accuracy)

    @staticmethod
    def nds2wgs( transfer_data):
        '''
        nds value to wgs (longitude or latitude)
        :param transfer_data: nds value
        :return: wgs value
        '''
        # print transfer_data
        # print decimal.Decimal((float(transfer_data) * 90)/ (1024 * 1024 * 1024))
        # return round((int(transfer_data) * 90)/ (1024 * 1024 * 1024),15)
        return (decimal.Decimal(transfer_data)*decimal.Decimal('90')/(decimal.Decimal('1024')*decimal.Decimal('1024')*decimal.Decimal('1024')))

    @staticmethod
    def wgs2nds(transfer_data):
        '''
        wgs value to nds value (longitude or latitude)
        :param transfer_data:
        :return:
        '''
        # return round((int(transfer_data) * (1024 * 1024 * 1024)/(90)), 15)
        return (decimal.Decimal(transfer_data) * decimal.Decimal('1024.0')*decimal.Decimal('1024.0')*decimal.Decimal('1024.0')/decimal.Decimal('90.0'))

    def generate_file(self, file_name, start, step, end):
        '''
        Generate Gaussian noise new gps file that endswith ".gps.gps"
        According to "start" and "end" pose ,add "step" every time.
        If "start<=0" or "start > end" ,start is 0 .
        :param file_name: Truth gps file(full path)
        :param param:Transfer longitude , latitude or all
        :return: none
        '''
        lines = linecache.getlines(file_name)

        new_lines = list()

        if start >= len(lines) or start < 0:
            current_pose = 0
        else:
            current_pose = start

        if 0 >= end or start >= end:
            end = len(lines) - 1

        if not type(step)==int or step >= 0:
            step = 1

        while current_pose <= end and current_pose <= len(lines) - 1:

            pos_item = lines[current_pose].split(",")

            if current_pose >= start:
                # print current_pose
                if "Lon" in self.param:
                    pos_item[1] = self.__gaussian_noise__(pos_item[1], self.longitude_accuracy)

                if "Lat" in self.param:
                    pos_item[2] = self.__gaussian_noise__(pos_item[2], self.latitude_accuracy)

                if "all" in self.param:
                    pos_item[1] = self.__gaussian_noise__(pos_item[1], self.longitude_accuracy)
                    pos_item[2] = self.__gaussian_noise__(pos_item[2], self.latitude_accuracy)
                    pos_item[3] = self.__gaussian_noise_altitude(pos_item[3], self.altitude_accuracy)

            pos_item[-1] = pos_item[-1].replace("\n", "")
            new_lines.append(','.join(pos_item))

            current_pose += step

        # print new_lines
        with open(file_name + ".gps", "w") as new:
            for line in new_lines:
                new.write(line + "\n")

    def generate_all_file(self, start, step, end):
        '''
        Add Gaussian noise to all gps.
        :return: none
        '''
        all_files = list()
        for root, dirs, files in os.walk(self.path):
            for file in files:
                if file.endswith(".gps"):
                    self.generate_file(os.path.join(root, file), start, step, end)



if __name__ == "__main__":
    add_gaussianNoise = GaussianNoiseGPS("/home/user/test_code/vtd_data/", "all")
    # add_gaussianNoise.generate_all_file(5000, 1, 0)
    add_gaussianNoise.generate_file("/home/user/test_code/vtd_data/PEQI_2721_Different_"
                                    "Speed_With_The_Same_Radius_R2_10km_h_path0001.gps", 5000, 1, 0)
