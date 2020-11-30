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
import time
from db_utils import *
from sql_const import *
from const import *
from files import *


def get_booking_data(current_row):
    booking_data = {
        'booking_id': current_row[0].strip(),
        'receipt_country': current_row[1].strip(),
        'receipt_port': current_row[2].strip(),
        'delivery_country': current_row[3].strip(),
        'delivery_port': current_row[4].strip(),
        'transport_service_type': str(current_row[5]).strip(),
        'transport_service_mode': str(current_row[6]).strip(),
        'scheduled_date': current_row[7].strftime('%Y%m%d'),
        'voyage_name': current_row[8].strip(),
        'voyage_no': current_row[9].strip(),
        'email': current_row[10].strip(),
        'contact': current_row[11].strip(),
        'telephone': current_row[12].strip(),
        'fax': current_row[13].strip(),
        'booking_date': current_row[14],
        'contract_no': current_row[15].strip(),
    }
    return booking_data


def get_booking_detail_data(current_row):
    booking_detail_data = {
        'product_description': current_row[0],
        'container_code': current_row[1],
        'container_qty': current_row[2],
        'weight': current_row[3],
        'weight_disc': current_row[4],
        'weight_unit': current_row[5],
        'quantity': current_row[6],
        'volume': current_row[7],
        'volume_unit': current_row[8],
        'remark': current_row[9],
    }
    return booking_detail_data


def check_data(booking_data, all_detail_row):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    error_msg = ""
    if booking_data['scheduled_date'] <= today:  # 日期不能小于今日
        error_msg = "scheduled_date error"
        return error_msg

    if len(booking_data['fax'].strip()) == 0:  # 传真不能为空
        error_msg = "Fax can‘t be empty."
        return error_msg

    if len(booking_data['telephone'].strip()) == 0:  # 电话不能为空
        error_msg = "Telephone can‘t be empty."
        return error_msg

    if len(booking_data['email'].strip()) == 0:  # 电邮不能为空
        error_msg = "Email can‘t be empty."
        return error_msg

    if len(booking_data['booking_id'].strip()) == 0:  # 订单号不能为空
        error_msg = "booking_id can‘t be empty."
        return error_msg

    for detail_row in all_detail_row:
        detail_data = get_booking_detail_data(detail_row)
        if detail_data['weight'] <= 0:  # 重量必须大于零
            error_msg = "weight can't not less than zero"
            return error_msg

        if detail_data['volume'] <= 0:  # 体积必须大于零
            error_msg = "volume can't not less than zero"
            return error_msg

        if detail_data['quantity'] <= 0:  # 数量必须大于零
            error_msg = "quantity can't not less than zero"
            return error_msg

        # 如果是每件货品的重量，这个数量必须大于零， 最后是传入重重量
        if detail_data['weight_disc'] == 0 and detail_data['quantity'] <= 0:
            error_msg = "weight_disc and quantity error"
            return error_msg

    return error_msg


def get_eid_data(booking_data, all_booking_detail_row):
    """
    传入订舱的主表数据， 并且组装好详细表的数据
    :param booking_data:
    :param all_booking_detail_row:
    :return: edi 所有需要的数据
    """
    edi_data = []
    for detail_row in all_booking_detail_row:
        detail_data = get_booking_detail_data(detail_row)
        edi_data.append(detail_data)

    booking_data["GID"] = edi_data

    return booking_data


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
        # 取到所有未处理的订舱主数据
        booking_data = get_booking_data(get_row)

        # 取到所有未处理的订舱明细数据
        booking_detail_cursor = select_sql_data(connect_db, BOOKING_DETAIL_SQL, booking_data['booking_id'])

        all_booking_detail_row = booking_detail_cursor.fetchall()
        if all_booking_detail_row:
            check_result = check_data(booking_data, all_booking_detail_row)
            if len(check_result) <= 0:
                # 收集所有数据
                booking_data = get_eid_data(booking_data, all_booking_detail_row)

                # 正式开始写报文
                handle_edi_file(booking_data)

                # 更新数据库
                status = 1
            else:
                # 更新数据库
                status = 2
            str_error = check_result
        else:
            status = 2
            str_error = 'Booking detail can not not be empty.'

        data = (status, str_error, booking_data["booking_id"])
        update_sql(connect_db, UPDATE_BOOKING_STATUS_SQL, data)

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
        print("Begin Searching database...")
        main_progress(db_connect)
        print("Sleeping 60s......\n")
        time.sleep(10)
    db_connect.close()
