#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
长荣EDI报文，从数据库中读入数据，制作报文，并上传到FTP服务器
@File    :   edi_send.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
25/11/2020 12:37   lzb       1.0         None
"""
import shutil
from datetime import datetime
import time
from db_utils import *
from sql_const import BOOKING_SQL
from const import *
from ftp_tools import create_ftp_connect, uploading_file, get_file_list
from evengreen_files import *


def get_booking_data(current_row):
    booking_data = {
        'booking_id': current_row[0].strip(),
        'receipt_country': current_row[1].strip(),
        'receipt_port': current_row[2].strip(),
        'delivery_country': current_row[3].strip(),
        'delivery_country_name': current_row[4].strip(),
        'delivery_port': current_row[5].strip(),
        'delivery_port_name': current_row[6].strip(),
        'transport_service_type': str(current_row[7]).strip(),
        'transport_service_mode': str(current_row[8]).strip(),
        'scheduled_date': current_row[9].strftime('%Y%m%d'),
        'voyage_name': current_row[10].strip(),
        'voyage_no': current_row[11].strip(),
        'email': current_row[12].strip(),
        'contact': current_row[13].strip(),
        'telephone': current_row[14].strip(),
        'fax': current_row[15].strip(),
        'booking_date': current_row[16],
        'contract_no': current_row[17].strip(),
        'business_name': current_row[18].strip(),
        'address1': current_row[19].strip(),
        'address2': current_row[20].strip(),
        'town': current_row[21].strip(),
        'country': current_row[22],
        'postcode': current_row[23].strip(),
    }
    return booking_data


def get_booking_detail_data(current_row):
    booking_detail_data = {
        'product_description': current_row[0].strip(),
        'container_code': current_row[1].strip(),
        'container_qty': current_row[2],
        'weight': current_row[3],
        'weight_disc': current_row[4],
        'weight_unit': current_row[5].strip(),
        'quantity': current_row[6],
        'volume': current_row[7],
        'volume_unit': current_row[8].strip(),
        'remark': current_row[9].strip(),
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

    return error_msg


def ftp_file(ftp_files_list):
    start_time = time.time()
    ftp = create_ftp_connect(FTP_HOST, FTP_PORT, FTP_USERNAME, FTP_PASSWORD)
    if ftp:
        ftp.cwd(REMOTE_DIRECTORY)  # 转换至需要上传的目录
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step5: 连接远程的FTP服务器 " + "{:3.6f}".format(spend_time) + "s. ")

        # 上传文件(上传整个目录的文件)
        start_time = time.time()
        for file in ftp_files_list:
            (path, filename) = os.path.split(file)
            remote_file = filename
            if uploading_file(ftp, remote_file, file):
                if PROGRAM_DEBUG:
                    spend_time = time.time() - start_time
                    print(" ** Step6: 成功上传文件 " + filename + "...." + "{:3.6f}".format(spend_time) + "s. ")
                # remove to bak
                try:
                    # 上传成功后，将本地文件到备份目录中
                    start_time = time.time()
                    bak_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_UPLOAD_BACKUP_DIR)
                    shutil.copy(file, bak_path)
                    os.remove(file)
                    if PROGRAM_DEBUG:
                        spend_time = time.time() - start_time
                        print(" ** Step7: 将文件 " + filename + "移至到备份目录中...." + "{:3.6f}".format(spend_time) + "s. ")
                except:
                    if PROGRAM_DEBUG:
                        spend_time = time.time() - start_time
                        print(filename + " ** Step7: 将文件移至到备份目录失败...." + "{:3.6f}".format(spend_time) + "s. ")
        # 关闭FTP连接
        ftp.close()
    else:
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step5: 连接远程的FTP服务器...失败 " + "{:3.6f}".format(spend_time) + "s. ")


def make_edi_file(connect_db, booking_data, all_booking_detail_row):
    """
    制作EDI报文，并且更新数据库
    :param connect_db: 数据库连接
    :param booking_data: booking的数据
    :param all_booking_detail_row: booking_detail 的数据
    :return:
    """
    check_result = check_data(booking_data, all_booking_detail_row)
    if len(check_result) <= 0:
        start_time = time.time()
        # 收集所有数据
        booking_data = get_eid_data(booking_data, all_booking_detail_row)
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step1: 收集所有数据 " + "{:3.3f}".format(spend_time) + "s. ")

        # 编写报文的内容
        start_time = time.time()
        content_list = encoding_edi_file(booking_data, connect_db)
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step2: 编写报文的内容 " + "{:3.6f}".format(spend_time) + "s. ")

        # 保存文件
        start_time = time.time()
        filename = booking_data["booking_id"] + ".txt"
        save_to_file(filename, content_list)
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step3: 生成新的报文文件 " + "{:3.6f}".format(spend_time) + "s. ")

        # 更新数据库
        status = 1
    else:
        # 更新数据库
        status = 2
    str_error = check_result

    start_time = time.time()
    data = [status, str_error, booking_data["booking_id"]]
    update_sql(connect_db, UPDATE_BOOKING_STATUS_SQL, data)
    if PROGRAM_DEBUG:
        spend_time = time.time() - start_time
        print(" ** Step4: 更新数据 " + "{:3.6f}".format(spend_time) + "s. ")

    return


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
    status = [0, ]
    booking_cursor = select_sql_data(connect_db, BOOKING_SQL, status)  # 取到所有未处理的数据
    get_row = booking_cursor.fetchone()
    if get_row:
        # 取到所有未处理的订舱主数据
        booking_data = get_booking_data(get_row)

        # 取到所有未处理的订舱明细数据
        booking_detail_cursor = select_sql_data(connect_db, BOOKING_DETAIL_SQL, [booking_data['booking_id'], ])

        all_booking_detail_row = booking_detail_cursor.fetchall()
        if all_booking_detail_row:    # 如何没有订单明细，则不做任何处理
            make_edi_file(connect_db, booking_data, all_booking_detail_row)

        booking_detail_cursor.close()

    booking_cursor.close()

    return


# main progress
if __name__ == "__main__":
    while True:
        try:
            db_connect = connect_remote_db()
            print("Connect REMOTE database success!")
            main_progress(db_connect)
            db_connect.close()

            # 查询是否有需要上传的文件，如何有，就上传
            files_list = []
            local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_UPLOAD_DIR)
            files_list = get_file_list(local_path, files_list)
            if files_list:
                # 上传到FTP服务器
                ftp_file(files_list)

            print("EDI SEND System Sleeping ...\n")
            time.sleep(EDI_SEND_SLEEP_TIME)
        except:
            time.sleep(60)

