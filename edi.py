#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   edi.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
25/11/2020 12:37   lzb       1.0         None
"""
from datetime import datetime

from const import *
from db_utils import *
from sql_const import *


def get_booking_data(current_row):
    booking_data = {
        'booking_id': current_row[0],
        'receipt_country': current_row[1],
        'receipt_port': current_row[2],
        'delivery_country': current_row[3],
        'delivery_port': current_row[4],
        'transport_service_type': current_row[5],
        'transport_service_mode': current_row[6],
        'scheduled_date': current_row[7].strftime('%Y-%m-%d'),
        'voyage_name': current_row[8],
        'voyage_no': current_row[9],
        'confirm_email': current_row[10],
        'booking_contact': current_row[11],
        'contract_no': current_row[12],
    }
    return booking_data


def get_booking_detail_data(current_row):
    booking_detail_data = {
        'container_code': current_row[0],
        'container_qty': current_row[1],
        'weight': current_row[2],
        'weight_disc': current_row[3],
        'weight_unit': current_row[4],
        'quantity': current_row[5],
        'volume': current_row[6],
        'volume_unit': current_row[7],
        'remark': current_row[8],
    }
    return booking_detail_data


def check_data(booking_data, all_detail_row):
    today = datetime.today().strftime('%Y-%m-%d')
    if booking_data['scheduled_date'] <= today:
        return False
    for detail_row in all_detail_row:
        detail_data = get_booking_detail_data(detail_row)
        if detail_data['weight'] <= 0:
            return False

        if detail_data['weight'] <= 0:
            return False
    return True


def main_progress(connect_db):
    """
    EDI main progress
    :param connect_db: 数据库
    :return:none
    """
    """
    查数据库，有数据'
    检查数据是否合法，如果合法， 则全部放入对应的列表中
    开始编写报文
    保存报文
    上传报文
    """
    booking_cursor = select_sql(connect_db, BOOKING_SQL)  # 取到所有未处理的数据
    get_row = booking_cursor.fetchone()
    if get_row:
        booking_data = get_booking_data(get_row)
        booking_detail_cursor = select_sql_data(connect_db, BOOKING_DETAIL_SQL, booking_data['booking_id'])  # 取到所有未处理的订舱明细数据
        all_booking_detail_row = booking_detail_cursor.fetchall()
        if all_booking_detail_row:
            check_result = check_data(booking_data, all_booking_detail_row)
            if check_result:
                # 正式开始写报文
                pass
        booking_detail_cursor.close()
    booking_cursor.close()
    return


if __name__ == "__main__":
    is_connect_db = True
    if REMOTE_DATABASE:  # 连接远程数据库
        db_connect = connect_remote_db()
        print("Connect REMOTE database success!")
    else:
        db_connect = connect_local_db()
        print("Connect LOCAL database success!")
    # end if

    while is_connect_db:
        main_progress(db_connect)

    db_connect.close()
