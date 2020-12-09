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

    SQL = "INSERT INTO booking_result (booking_id, carrier_booking_number,confirm_datetime, " \
          "voyage_name, voyage_no, " \
          "receipt_country, receipt_port, start_date, " \
          "delivery_country, delivery_port, delivery_date, " \
          "exchange_ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

    cursor = db_connect.cursor()
    try:
        cursor.fast_executemany = True
        date_string = '2020/12/07 01:00:39'
        a_date = datetime.datetime.strptime(date_string, '%Y/%m/%d %H:%M:%S')
        data = [['dcgtestbooking005', '14200010519', datetime.datetime(2020, 11, 30, 11, 34),
                 '9832729:::EVER GREE', '1118-006W',
                 'TW', 'KHH', datetime.datetime(2020, 12, 18, 0, 0),
                 'GB', 'FXT', datetime.datetime(2021, 1, 16, 0, 0),
                 '2020113000059'], ]
        # cursor.executemany(SQL, data)
        abc = "DELETE FROM booking_result WHERE  booking_id= ? "
        dd = ["dcgtestbooking005", ]
        cursor.execut(abc, dd)
        db_connect.commit()
    except:
        db_connect.rollback()
    cursor.close()

    db_connect.close()
