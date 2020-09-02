#!/usr/bin/env python
# encoding: utf-8
'''
Define some common function
  
Create on 2019-04-29
@author: Hong He
@Change time: 
'''

from __future__ import division
from math import *
from decimal import *
import math
import numpy as np
import os
import linecache
import decimal

# try:
#     import geopy
#     import geopy.distance
# except:
#     os.system("sudo pip install geopy")

getcontext().prec = 16


class CommonMethod():
    # semi-major axis of earth
    A = 6378137.0

    # flattening of earth, 1 / 298.257
    FLAT = 0.0033528131778969

    # first eccentricity ratio
    ESQUARE = FLAT * (2 - FLAT)

    # PI
    PI = 3.141592653589793

    # PI/180
    DEGTORAG = 0.0174532925199433

    # 1/Ang_Hud
    radToDeg = 57.29577951308233

    @classmethod
    def abs2rel(cls, two_dimensional_array, reference):
        '''
        @summary: Converting absolute coordinates into relative coordinates in rectangular coordinates
        @param two_dimensional_array: A two-dimensional array of longitude and latitude. Note that longitude is first and latitude is second.
        @param reference: Convert to the reference point needed for rectangular coordinates. Note that the first point of input is selected here.
        @return : Points in Cartesian Coordinates
        '''

        # Initialize the list of longitude and latitude points in rectangular coordinates
        rel_data = []

        # Formula calculation of absolute coordinate to relative coordinate
        sinphi = math.sin(reference[1] * (cls.DEGTORAG))
        cosphi = math.cos(reference[1] * (cls.DEGTORAG))
        meridianRadius_ = ((cls.A * (1 - cls.ESQUARE)) / (pow(1 - cls.ESQUARE * sinphi * sinphi, 1.5)))
        parallelRadius_ = (cls.A * cosphi / math.sqrt(1 - cls.ESQUARE * sinphi * sinphi))
        for item in two_dimensional_array:
            dlon = (item[0] - reference[0]) * (cls.DEGTORAG)
            if dlon > cls.PI:
                dlon = dlon - 2 * cls.PI
            elif dlon < - cls.PI:
                dlon = 2 * cls.PI + dlon
            rel_lon = dlon * (parallelRadius_)
            rel_lat = (item[1] - reference[1]) * ((cls.DEGTORAG) * meridianRadius_)
            rel_data.append([rel_lon, rel_lat])
        return rel_data

    @classmethod
    def rel2abs(cls, reference, two_dimensional_array):
        '''
        reference:relpoint
        two_dimensional_array:abspoint
        '''
        abs_data = []

        sinphi = math.sin(reference[1] * cls.DEGTORAG)
        cosphi = math.cos(reference[1] * cls.DEGTORAG)
        meridianRadius_ = (cls.A * (1 - cls.ESQUARE)) / (pow(1 - cls.ESQUARE * sinphi * sinphi, 1.5))
        parallelRadius_ = cls.A * cosphi / math.sqrt(1 - cls.ESQUARE * sinphi * sinphi)

        for item in two_dimensional_array:
            abs_lon = reference[0] + item[0] / parallelRadius_ * cls.radToDeg
            abs_lat = reference[1] + item[1] / meridianRadius_ * cls.radToDeg

            if abs_lon >= 180.0:
                abs_lon -= 360.0
            elif abs_lon <= -180.0:
                abs_lon += 360.0

            abs_lon = float(CommonMethod.wgs2nds(str(abs_lon)))
            abs_lat = float(CommonMethod.wgs2nds(str(abs_lat)))

            abs_data.append([abs_lon, abs_lat])
        return abs_data

    @classmethod
    def p2p_ditance(cls, lon1, lat1, lon2, lat2):
        '''
        Get point A to point B distance
        :param lon1: Longitude of point A
        :param lat1: Latitude of point A
        :param lon2: Longitude of point B
        :param lat2: Latitude of point B
        :return: distance
        '''
        return sqrt((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2)

    @classmethod
    def nds2wgs(cls, transfer_data):
        '''
        nds value to wgs (longitude or latitude)
        :param transfer_data: nds value
        :return: wgs value
        '''
        # print transfer_data
        # print decimal.Decimal((float(transfer_data) * 90)/ (1024 * 1024 * 1024))
        # return round((int(transfer_data) * 90)/ (1024 * 1024 * 1024),15)
        return (decimal.Decimal(transfer_data) * decimal.Decimal('90') / (
                decimal.Decimal('1024') * decimal.Decimal('1024') * decimal.Decimal('1024')))

    @classmethod
    def wgs2nds(cls, transfer_data):
        '''
        wgs value to nds value (longitude or latitude)
        :param transfer_data:
        :return:
        '''
        # return round((int(transfer_data) * (1024 * 1024 * 1024)/(90)), 15)
        return (decimal.Decimal(transfer_data) * decimal.Decimal('1024.0') * decimal.Decimal(
            '1024.0') * decimal.Decimal('1024.0') / decimal.Decimal('90.0'))

    @classmethod
    def get_gps_data(cls, gps_dir):
        '''
        Get gps list from gps file
        :param gps_dir: GPS full name path ,file name
        :return: GPS list
        '''
        lst_gps = []

        with open(gps_dir, 'r') as f:
            for line in f:
                pose_data = line.split(',')
                lon = CommonMethod.nds2wgs(str(pose_data[1]))
                lat = CommonMethod.nds2wgs(str(pose_data[2]))
                lst_gps.append([float(lon), float(lat)])
        return lst_gps

    @classmethod
    def write_file(cls, file_name, tag_name, new_lines):
        '''
        Write data to new file
        :param file_name: Input full name of file
        :param new_lines: Data to save
        :return: None
        '''
        with open(file_name.replace(".gps", "_") + tag_name + ".gps", "w") as new:
            for line in new_lines:
                new.write(line + "\n")


class GPSPartOperations():

    def __init__(self):
        pass

    @classmethod
    def move_by_lon_lat(cls, lon1, lat1, lon2, lat2, distance, dirction):
        '''
        Move by longitude
        :param value:longitude or latitude value
        :param distance:length by meter
        :return: new longitude
        '''
        new_lon = lon2
        new_lat = lat2
        current_distance = sqrt((lon2 - lon1) ** 2 + (lat2 - lat1) ** 2)

        angle_old = 0
        if (lat2 - lat1) != 0 and (lon2 - lon1) != 0:
            angle_old = abs(np.arctan((lat2 - lat1) / (lon2 - lon1)))

        if distance != 0:
            if "lon" in dirction:
                new_lon = lon2 + distance
            elif "lat" in dirction:
                new_lat = lat2 + distance
            else:
                new_lon = (distance + current_distance) * sin(angle_old)
                new_lat = (distance + current_distance) * cos(angle_old)

        return new_lon, new_lat

    @classmethod
    def turn_angle(cls, lon1, lat1, lon2, lat2, angle):
        '''
        Point A and B turn round B' by angle
        :param angle:Turn round angle
        :param lon1:Point A' longitude
        :param lat1:Point A' latitude
        :param lon2:Point B' longitude
        :param lat2:Point B' latitude
        :return: new lon2,lat2
        '''

        distance = CommonMethod.p2p_ditance(lon1, lat1, lon2, lat2)
        angle_old = 0

        if (lat2 - lat1) != 0 and (lon2 - lon1) != 0:
            angle_old = (np.arctan((lon2 - lon1) / (lat2 - lat1)))
        if (lat2 - lat1) < 0:

            lat2_new = -distance * cos(angle_old + angle * CommonMethod.DEGTORAG)
        else:
            lat2_new = distance * cos(angle_old + angle * CommonMethod.DEGTORAG)

        if (lon2 - lon1) < 0:
            lon2_new = -distance * sin(angle_old + angle * CommonMethod.DEGTORAG)
        else:
            lon2_new = distance * sin(angle_old + angle * CommonMethod.DEGTORAG)

        return lon2_new, lat2_new

    @classmethod
    def reflection_to_lon_lat(cls, lon1, lat1, lon2, lat2, param):
        distance = CommonMethod.p2p_ditance(lon1, lat1, lon2, lat2)
        lon2_new = None
        lat2_new = None

        if "lat" in param:
            if (lat2 - lat1) < 0:
                lat2_new = distance
            else:
                lat2_new = -distance
            lon2_new = lon1

        elif "lon" in param:
            if (lon2 - lon1) < 0:
                lon2_new = distance
            else:
                lon2_new = -distance
            lat2_new = lat1
        else:
            print (''' 
                    Please input "lon" or "lat" parameter
                  ''')
            exit(-1)
        return lon2_new, lat2_new

    @classmethod
    def amplification(cls, lon1, lat1, lon2, lat2, multiple):
        '''
        amplification GPS
        :param multiple:amplification multiple ,default 1
        :param lon1:Point A' longitude
        :param lat1:Point A' latitude
        :param lon2:Point B' longitude
        :param lat2:Point B' latitude
        :return:Zoom value point
        '''

        distance = CommonMethod.p2p_ditance(lon1, lat1, lon2, lat2)
        new_lon = lon2
        new_lat = lat2
        if distance > 0:
            if lon2 < 0:
                new_lon = lon2 - abs(lon2 - lon1) * multiple
            else:
                new_lon = lon2 - abs(lon2 - lon1) * multiple

            if lat2 < 0:
                new_lat = lat2 - abs(lat2 - lat1) * multiple
            else:
                new_lat = lat2 + abs(lat2 - lat1) * multiple
        return new_lon, new_lat

    @classmethod
    def get_mv_rel(cls, point_lon, point_lat, move_data):
        '''
        Move all gps point
        :param point_lon: New longitude of first point
        :param point_lat: New latitude of first point
        :param move_data: Input gps list
        :return: new gps list
        '''
        if move_data:
            new_data = list()
            all_rel_gps = CommonMethod.abs2rel(move_data, move_data[0])
            transfer_data = CommonMethod.rel2abs([point_lon, point_lat], all_rel_gps)

            for data_ in transfer_data:
                new_lon = float(CommonMethod.nds2wgs(data_[0]))
                new_lat = float(CommonMethod.nds2wgs(data_[1]))
                new_data.append([new_lon, new_lat])
            return new_data
        else:
            print ("Input gps list is empty!")
            exit(-1)

    # @classmethod
    # def narrow(cls, lon1, lat1, lon2, lat2, multiple=1):
    #     '''
    #     Narrow GPS
    #     :param lon1:Point A' longitude
    #     :param lat1:Point A' latitude
    #     :param lon2:Point B' longitude
    #     :param lat2:Point B' latitude
    #     :param multiple: Narrow multiple
    #     :return:current point new longitude and latitude
    #     '''
    #     distance = CommonMethod.haversine(lon1, lat1, lon2, lat2)
    #
    #     multi = 1 / 2 ** multiple
    #
    #     if distance > 0:
    #         return (lon1 + lon2) * multi, (lat1 + lat2) * multi
    #     else:
    #         return lon2, lat2


class GPSFileOperations():
    current_pose = 0

    def __init__(self, file_path):
        self.file_path = file_path

    def __file_lines_(self, file_name):
        '''
        Get file lines
        :param file_name: Full name of file
        :return: line list
        '''
        return linecache.getlines(file_name)

    def __callback__(self, even_method, file_name, start, *arg, **kwargs):
        '''
        Callback method
        :param even_method: Function name
        :param file_name: Full name of file
        :param start: start operation pose
        :param arg: arg list
        :param kwargs: parameter dictionary
        :return: new gps list
        '''
        current_pose = 0
        gps_all = CommonMethod.get_gps_data(file_name)

        if kwargs["lon"] and kwargs["lat"]:
            gps_all = GPSPartOperations.get_mv_rel(kwargs["lon"], kwargs["lat"], gps_all)

        all_rel_gps = CommonMethod.abs2rel(gps_all, gps_all[start])
        new_rel_gps = list()
        while current_pose <= len(all_rel_gps) - 1:
            value = all_rel_gps[current_pose]
            if current_pose >= start:
                value = even_method(all_rel_gps[start][0],
                                    all_rel_gps[start][1],
                                    all_rel_gps[current_pose][0],
                                    all_rel_gps[current_pose][1],
                                    *arg
                                    )
            new_rel_gps.append(value)
            current_pose += 1

        return CommonMethod.rel2abs(gps_all[start], new_rel_gps)

    def __transfer__(self, current_pose, lines, new_data):
        '''
        Insert new data to lines
        :param current_pose: default 0
        :param lines: File lines of before operation
        :param new_data: Gps list
        :return: New line list
        '''
        new_lines = list()
        while current_pose < len(lines) - 1:
            line_info = lines[current_pose].replace("\n", "").split(",")

            line_info[1] = str(new_data[current_pose][0])
            line_info[2] = str(new_data[current_pose][1])

            new_lines.append(",".join(line_info))
            current_pose += 1
        return new_lines

    def gps_operations(self, file_name, mode, start, *args, **kwargs):
        '''
        Gps operations
        :param file_name: Full name of file
        :param mode: Operation mode
        :param start: Start change pose
        :param args: args list
        :param kwargs: parameter dictionary
        :return: None
        '''
        run_type = None
        tag_name = None

        if "amp" in mode:
            run_type = GPSPartOperations.amplification
            tag_name = "amp"
        elif "turn" in mode:
            run_type = GPSPartOperations.turn_angle
            tag_name = "turn"
        elif "cut" in mode:
            run_type = GPSPartOperations.move_by_lon_lat
            tag_name = "cut"
        elif "ref" in mode:
            run_type = GPSPartOperations.reflection_to_lon_lat
            tag_name = "reflection"
        else:
            print ('''Please input run mode:
                      amp : amplification mode
                      turn : turn by angle
                      cut : cut and move by latitude or longitude
                      ref: reflection to latitude or longitude 
                    ''')
            exit(-1)

        new_data = self.__callback__(run_type, file_name, start, *args, **kwargs)

        CommonMethod.write_file(file_name,
                                tag_name + "_" + str(kwargs["name"]),
                                self.__transfer__(
                                    self.current_pose,
                                    self.__file_lines_(file_name),
                                    new_data
                                )
                                )

    def move_position(self, file_name, tag_name, point_lon, point_lat):

        new_data = list()
        gps_all = GPSPartOperations.get_mv_rel(point_lon, point_lat, CommonMethod.get_gps_data(file_name))
        for gps_ in gps_all:
            new_lon = float(CommonMethod.wgs2nds(gps_[0]))
            new_lat = float(CommonMethod.wgs2nds(gps_[1]))
            new_data.append([new_lon, new_lat])
        CommonMethod.write_file(file_name,
                                tag_name,
                                self.__transfer__(
                                    self.current_pose,
                                    self.__file_lines_(file_name),
                                    new_data
                                )
                                )

    def generate_all_file(self, method, *arg):
        '''
        Add Gaussian noise to all gps.
        :return: none
        '''
        all_files = list()
        for root, dirs, files in os.walk(self.file_path):
            for file in files:
                if file.endswith(".gps"):
                    method(os.path.join(root, file), arg)


class GPSTimeStampOperation():

    def __init__(self, file_):
        '''
        Initial object by file
        :param file_: Input full name of file
        '''
        self.file_name = file_

    def __read_gps__(self):
        '''
        Return file lines list
        :return:
        '''
        return linecache.getlines(self.file_name)

    def time_delay_ms(self, start, delay_value):
        '''
        Set delay time of millisecond and generate new file
        :param start:Start delay pose
        :param delay_value:Delay time value
        :return:None
        '''
        gps_lines = self.__read_gps__()
        new_lines = list()
        current_pose = 0

        for line_ in gps_lines:
            line_tmp = line_.rstrip("\n").split(",")
            if current_pose >= start:
                line_tmp[-1] = str(eval(line_tmp[-1]) + delay_value)
            new_lines.append(",".join(line_tmp))

        CommonMethod.write_file(self.file_name, "delay_" + str(delay_value), new_lines)

    def generate_tunnel_gps(self, start, end):
        gps_lines = self.__read_gps__()
        new_lines = list()
        cp_line = gps_lines[start].rstrip("\n").split(",")
        current_pose = 0

        for line_ in gps_lines:
            line_tmp = line_.rstrip("\n").split(",")
            if current_pose >= start and current_pose < end:
                line_tmp[1] = cp_line[1]
                line_tmp[2] = cp_line[2]
                line_tmp[4] = "0"
            new_lines.append(",".join(line_tmp))
            current_pose += 1

        CommonMethod.write_file(self.file_name, "tunnel_" + str(start) + "_" + str(end), new_lines)


if __name__ == "__main__":
    gps_obj = GPSFileOperations("/home/user/test_code/vtd_data/test_data/result/gps/0515/delay")
    gps_time_obj = GPSTimeStampOperation("/home/user/complex_3/SE-PJ_PEQI-2894_ComplexScene3-P28_path0004_test.gps")
    # step =1
    # gps_obj.move_by_lon_lat(
    #     "/home/user/test_code/vtd_data/LightCase6-10_L_path0001.gps", 500, 10,
    #     "lon")
    # gps_obj.amplification_gps(
    #     "/home/user/test_code/vtd_data/LightCase6-10_L_path0001.gps", 500, 0.5)
    # gps_obj.gps_operations(
    #     "/home/user/test_code/vtd_data/LightCase6-10_L_path0001.gps",
    #     "move",
    #     720,
    #     10,
    #     "lon",
    #     lon=10.13938064686954,
    #     lat=47.99168958328664)

    # for i in range(10):
    #     value=i*0.02+0.02
    #
    # gps_obj.gps_operations(
    #     "/home/user/test_code/vtd_data/LightCase6-10_L_path0001.gps",
    #     "amp",
    #     0,
    #     0.01,
    #     lon=10.13938064686954,
    #     lat=47.99168958328664, name=0.01)
    #
    # for root, dir, files in os.walk("/home/user/test_code/vtd_data/cases/"):
    #     for file_ in files:
    #         if file_.endswith(".gps") and "delay" in file_:
    #             gps_obj.move_position(os.path.join(root, file_), "test", 10.13938064686954, 47.99168958328664)

    # gps_obj.move_position("/home/user/complex_3/SE-PJ_PEQI-2894_ComplexScene3-P28_path0004.gps", "test", 10.13938064686954, 47.99168958328664)
    # for i in range(5):
    #     value = i * 20 +20
    #     gps_time_obj.time_delay_ms(0, value)
    # gps_obj.gps_operations("/home/user/test_code/vtd_data/LightCase6-10_L_path0001.gps",
    #                        "ref",
    #                        0,
    #                        "lat",
    #                        lon=10.13938064686954,
    #                        lat=47.99168958328664,
    #                        name="lat")
    gps_time_obj.generate_tunnel_gps(4750, 8399)
