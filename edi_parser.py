#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
用于解析长荣EDI报文，从本地目录中判断是否有需要解析的文件，回写到数据库中，并备份已经处理完毕的报文
@File    :   edi_download.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
04/12/2020 09:41   lzb       1.0         None
"""
import logging
import os
import shutil
import time

from const import *
from db_utils import *
from decode_file import is_valid_file, encode_IFTMBC_file, encode_IFTSAI_file
from sql_const import *


def IFTMBC_file(local_file, file):
    """
    处理IFTMBC 订舱确认报文, 并更新到数据库中
    :param local_file: 下载到本地目录的文件
    :param file: 具体的文件名称
    :return:
    """

    # 备份目录
    bak_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_BACKUP_PATH)

    # 解码文件，并将数据存入列表中
    data_list = encode_IFTMBC_file(local_file)

    if data_list:
        insert_data(INSERT_BOOKING_RESULT, data_list, local_file, bak_path)
    else:
        print(" ***** No data have been found.")
        logging.info(" ***** No data have been found.")


def IFTSAI_file(local_file, file):
    """
    处理IFTSAI 运输计划及实施信息报文
    :param local_file: 下载到本地目录的文件
    :param file: 具体的文件名称
    :return:
    """
    # 备份目录
    bak_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_BACKUP_PATH)

    start_time = time.time()

    # 解码文件，并将数据存入列表中
    data_list = encode_IFTSAI_file(local_file)
    spend_time = time.time() - start_time
    info = " ***** ENCODE IFTSAI - The total recodes number is "+str(len(data_list)) + \
           " and taken times {:3.6f}".format(spend_time) + "s. "
    logging.info(info)
    print(info)

    if data_list:
        insert_data(INSERT_ROUTE_TIMETABLE, data_list, local_file, bak_path)
    else:
        print(" ***** No data have been found.")
        logging.info(" ***** No data have been found.")


def insert_data(sql, data_list, local_file, bak_path):
    """
    将数据更新进数据库
    :param sql: 需要插入的sql语句
    :param data_list: 需要更新的数据
    :param local_file: 本地文件
    :param bak_path: 备份文件的目录
    :return:
    """
    try:
        start_time = time.time()
        connect_db = connect_remote_db()
        spend_time = time.time() - start_time
        logging.info(" ***** CONNECT DATABASE have taken " + "{:3.6f}".format(spend_time) + "s. ")
        print(" ***** connect database, taken time ..." + "{:3.6f}".format(spend_time) + "s. ")
        # 插入INSERT_ROUTE_TIMETABLE的数据
        start_time = time.time()
        insert_sql_many(connect_db, sql, data_list)
        connect_db.close()
        spend_time = time.time() - start_time
        logging.info(" ***** INSERT_ROUTE_TIMETABLE Data have taken " + "{:3.6f}".format(spend_time) + "s. ")
        print(" ***** 插入INSERT_ROUTE_TIMETABLE的数据..." + "{:3.6f}".format(spend_time) + "s. ")

        # 将处理完成后的文件，移除到备份目录中
        start_time = time.time()
        shutil.copy(local_file, bak_path)
        os.remove(local_file)
        spend_time = time.time() - start_time
        logging.info(" ***** BACKUP File ...{:3.6f}".format(spend_time) + "s. ")
        print(" ***** 将文件 " + local_file + "移至到备份目录中...." + "{:3.6f}".format(spend_time) + "s. ")
    except:
        logging.exception("Error!!!")
        print(" ***** Some Error have happened.")


def parser_file():
    """
    处理目录下的文件
    :return:
    """
    # 需要处理的文件

    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_PATH)

    local_files = os.listdir(local_path)
    for file in local_files:
        if file.startswith(FILE_HEADER):   # 只处理成功完成下载的文件
            logging.info("Begin parse the file " + file)
            print("Begin parse the file " + file)
            start_time = time.time()
            local_file = os.path.join(local_path, file)

            if is_valid_file(local_file, "IFTMBC"):
                # IFTMBC 订舱确认报文
                IFTMBC_file(local_file, file)

            if is_valid_file(local_file, "IFTSAI"):
                # IFTSAI 运输计划及实施信息报文
                IFTSAI_file(local_file, file)
            # end if
            spend_time = time.time() - start_time
            logging.info("Finished parse the file " + file + " Taken {:3.6f}".format(spend_time) + "s. \n")
            print("Finished parse the file " + file + " Taken {:3.6f}".format(spend_time) + "s. ")
    # end for


# main progress
if __name__ == "__main__":
    logging.basicConfig(filename=LOG_EDI_PARSER, format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    print("System restart ....")
    logging.info("============================ EDI Parser System restart ============================")
    while True:
        parser_file()
        time.sleep(EDI_PARSER_SLEEP_TIME)
        print("Sleeping....")
