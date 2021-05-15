#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   upload_file_temp.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
17/04/2021 10:25   lzb       1.0         None
"""
import datetime

import pandas as pd
import numpy as np
import pymysql

INSERT_SQL = "INSERT INTO uk_postcode " \
                 "(postcode, county, district, " \
                 "country, postcode_area, " \
                 "postcode_district, latitude, " \
                 "longitude, easting, " \
                 "north, op_datetime, " \
                 "op_user_id) " \
                 "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"


# 连接的 MYSQL 数据库
def connect_remote_db():
    # 远程数据库的配置
    IP_ADDRESS = '127.0.0.1'
    DATABASE_NAME = "ukdcg"
    DATABASE_USERNAME = "ukdcg"
    DATABASE_PWD = "ukthomas"
    connect = pymysql.connect(IP_ADDRESS, DATABASE_USERNAME, DATABASE_PWD, DATABASE_NAME)

    return connect


def insert_sql_many(db_connects, sql, data):
    """
    :param db_connects: database
    :param data: value
    :param sql: update sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    try:
        cursor.fast_executemany = True
        cursor.executemany(sql, data)
        db_connects.commit()
        print('Save DB Successfully......')
    except:
        db_connects.rollback()
        print('Save DB Error......')
    cursor.close()


def upload_csv_file(input_file_name):
    print('read file....')
    data = pd.read_csv(input_file_name, dtype=str, header=1)
    print('get data....')
    data = data.replace(np.nan, '', regex=True)
    data_index = data.index
    print('get data index....'+str(data_index))
    get_data_list = []
    for i in data_index:
        rowValues = data.values[i]
        if rowValues[1] != 'No':
            postcode = rowValues[0].strip().upper()
            county = rowValues[7].strip().upper()
            district = rowValues[8].strip().upper()
            country = rowValues[12].strip().upper()
            postcode_area = rowValues[41].strip().upper()
            postcode_district = rowValues[42].strip().upper()
            latitude = rowValues[2]
            longitude = rowValues[3]
            easting = rowValues[4]
            if easting == '':
                easting = 0
            else:
                easting = int(easting)
            north = rowValues[5]
            if north == '':
                north = 0
            else:
                north = int(north)
            get_data_list.append((postcode, county, district, country, postcode_area, postcode_district,
                                  latitude, longitude, easting, north, datetime.datetime.now(), 1))
    return get_data_list


if __name__ == "__main__":
    print('begin loading file.....')
    file_name = 'C:\DCG\EXCEL Develop\postcodes.csv'
    data_list = upload_csv_file(file_name)
    if data_list:
        connect_db = connect_remote_db()
        print('begin insert DB......')
        insert_sql_many(connect_db, INSERT_SQL, data_list)
    print('finished.....')
