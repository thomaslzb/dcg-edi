#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   testing_server.py.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
26/11/2020 11:25   lzb       1.0         None
"""
import datetime
from db_utils import *

if __name__ == "__main__":
    is_connect_db = True
    db_connect = connect_remote_db()
    print("Connect REMOTE database success!")

    begin_time = datetime.datetime.now()

    SQL = "INSERT INTO route_timetable (message_code, message_date, route_name, " \
          "voyage_name, voyage_no, place_of_delivery, " \
          "place_of_delivery_date, place_of_receipt, place_of_receipt_date, " \
          "place_of_loading, place_of_loading_date,place_of_discharge, " \
          "place_of_discharge_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor = db_connect.cursor()
    try:
        cursor.fast_executemany = True
        date_string = '2020/12/07 01:00:39'
        a_date = datetime.datetime.strptime(date_string, '%Y/%m/%d %H:%M:%S')
        data = [['14550', datetime.datetime(2020, 10, 19, 6, 8), 'China-Australia-Taiwan Service', 'ITAL LAGUNA', '096N', 'CNXMN', datetime.datetime(2020, 11, 6, 0, 0), 'AUSYD', datetime.datetime(2020, 10, 20, 0, 0), 'AUSYD', datetime.datetime(2020, 10, 20, 0, 0), 'CNXMN', datetime.datetime(2020, 11, 6, 0, 0)],
                ['14551', datetime.datetime(2020, 10, 19, 6, 8), 'China-Australia-Taiwan Service', 'IRENES WAVE', '2047N', 'CNXMN', datetime.datetime(2021, 1, 1, 0, 0), 'AUSYD', datetime.datetime(2020, 12, 16, 0, 0), 'AUSYD', datetime.datetime(2020, 12, 16, 0, 0), 'CNXMN', datetime.datetime(2021, 1, 1, 0, 0)],
                ]
        # cursor.executemany(SQL, data)
        abc = "DELETE FROM booking_result WHERE  booking_id= ? "
        dd = ["dcgtestbooking005", ]
        cursor.execut(abc, dd)
        db_connect.commit()
    except:
        db_connect.rollback()
    cursor.close()

    db_connect.close()
