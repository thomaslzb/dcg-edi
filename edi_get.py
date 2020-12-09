#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
长荣EDI报文，从FTP中取文件，回写到数据库中，并删除已经处理完毕的报文
@File    :   edi_download.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
04/12/2020 09:41   lzb       1.0         None
"""
import os
import shutil
import time

from const import *
from db_utils import *
from encode_file import is_valid_file, encode_IFTMBC_file
from ftp_tools import create_ftp_connect, is_ftp_file, download_file
from sql_const import SELECT_BOOKING_SQL, INSERT_BOOKING_RESULT, UPDATE_BOOKING_STATUS_SQL


def checked_file(connect_db, file_list):
    """
    删除已经完成报文的文件
    :param connect_db: 数据库连接
    :param file_list: 所有的文件list
    :return: delete_files 需要删除的文件  download_files 需要下载的文件列表
    """
    download_files = []
    delete_files = []
    for file in file_list:
        booking_id = [os.path.splitext(file)[0], ]
        booking_cursor = select_sql_data(connect_db, SELECT_BOOKING_SQL, booking_id)  # 取到数据
        get_row = booking_cursor.fetchone()
        if get_row:
            status = get_row[0]
            if status == 9:  # 文件已经处理
                delete_files.append(file)
        else:
            # 将文件加入需要下载的文件列表中
            download_files.append(file)

    return delete_files, download_files


def download_file_to_local(ftp_connect, files_list, local_path):
    """
    下载 列表中的文件到本地目录
    :param ftp_connect: FTP连接
    :param files_list: 需要下载的文件列表
    :param local_path: 本地文件目录
    :return:
    """
    download_files_success = []
    for file in files_list:
        local_name = os.path.join(local_path, file)
        if download_file(ftp_connect, file, local_name):
            download_files_success.append(file)

    return download_files_success


def IFTMBC_file(ftp, connect_db, local_file, file):
    """
    处理IFTMBC 订舱确认报文, 并更新到数据库中
    :param ftp: FTP 连接
    :param connect_db: 数据库连接
    :param local_file: 下载到本地目录的文件
    :param file: 具体的文件名称
    :return:
    """

    # 备份目录
    bak_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_BACKUP_DIR)

    start_time = time.time()

    # 解码文件，并将数据存入列表中
    data_list = [encode_IFTMBC_file(local_file), ]

    # 插入BOOKING CONFIRM的数据
    insert_sql_many(connect_db, INSERT_BOOKING_RESULT, data_list)
    if PROGRAM_DEBUG:
        spend_time = time.time() - start_time
        print(" ** Step4: 插入BOOKING CONFIRM的数据..." + "{:3.6f}".format(spend_time) + "s. ")

    # 更新BOOKING的状态
    start_time = time.time()
    data_list = [[9, '', data_list[0][0], ], ]
    insert_sql_many(connect_db, UPDATE_BOOKING_STATUS_SQL, data_list)
    if PROGRAM_DEBUG:
        spend_time = time.time() - start_time
        print(" ** Step5: 更新BOOKING的状态..." + "{:3.6f}".format(spend_time) + "s. ")

    ftp.delete(file)  # 删除远程FTP文件
    if PROGRAM_DEBUG:
        spend_time = time.time() - start_time
        print(" ** Step6: 删除远程FTP文件..." + "{:3.6f}".format(spend_time) + "s. ")

    try:
        # 将处理完成后的文件，移除到备份目录中
        start_time = time.time()
        shutil.copy(local_file, bak_path)
        os.remove(local_file)
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step7: 将文件 " + file + "移至到备份目录中...."
                  + "{:3.6f}".format(spend_time) + "s. ")
    except:
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(file + " ** Step6: 将文件移至到备份目录失败...."
                  + "{:3.6f}".format(spend_time) + "s. ")


def handle_file(ftp, connect_db, all_files):
    """
    处理所有FTP目录下的文件
    :param ftp: FTP连接
    :param connect_db: 数据库连接
    :param all_files: 所有FTP目录下的文件
    :return:
    """
    # 查询是否所有文件中，是否有已经处理完成的的文件，有的话，删除远程的文件
    start_time = time.time()

    # 区分需要处理的文件或需要删除的文件
    files = checked_file(connect_db, all_files)
    delete_files = files[0]
    download_files = files[1]

    for file in delete_files:
        ftp.delete(file)  # 删除远程FTP文件

    if PROGRAM_DEBUG:
        spend_time = time.time() - start_time
        print(" ** Step2: 删除已经处理完成的远程FTP文件" + "{:3.6f}".format(spend_time) + "s. ")

    if download_files:
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_DIR)
        start_time = time.time()
        # 下载需要的文件，下载成功后，删除文件
        success_download_files = download_file_to_local(ftp, download_files, local_path)
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step3: 下载需要处理的文件到本地" + "{:3.6f}".format(spend_time) + "s. ")

        for file in success_download_files:

            # 处理已经下载的文件，更新到数据库中
            local_file = os.path.join(local_path, file)

            if is_valid_file(local_file, "IFTMBC"):
                # IFTMBC 订舱确认报文
                IFTMBC_file(ftp, connect_db, local_file, file)

            # if is_valid_file(local_file, "IFTSAI"):
            # IFTSAI 运输计划及实施信息报文
                # IFTSAI_file(ftp, connect_db, local_file, file)
            # end if
        # end for
    # end if


def main_progress(connect_db):
    start_time = time.time()
    ftp = create_ftp_connect(FTP_HOST, FTP_PORT, FTP_USERNAME, FTP_PASSWORD)
    if ftp:
        ftp.cwd(REMOTE_DIRECTORY)  # 转换至需要下载文件的目录

        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step1: 连接远程的FTP服务器成功..." + "{:3.6f}".format(spend_time) + "s. ")
        # 查询是否有需要处理的文件
        ftp_path = ftp.pwd()
        if is_ftp_file(ftp, ftp_path):
            all_files = ftp.nlst()  # 获取远程FTP的所有文件名
            if all_files:
                handle_file(ftp, connect_db, all_files)
        else:
            if PROGRAM_DEBUG:
                spend_time = time.time() - start_time
                print(" ** Step2: 连接远程的FTP服务器目录不正确..." + "{:3.6f}".format(spend_time) + "s. ")

    else:
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step5: 连接远程的FTP服务器...失败 " + "{:3.6f}".format(spend_time) + "s. ")
    # 关闭FTP连接
    ftp.close()


# main progress
if __name__ == "__main__":
    while True:
        try:
            db_connect = connect_remote_db()
            print("Connect REMOTE database success!")
            main_progress(db_connect)
            print("EDI SEND System Sleeping ...\n")
            db_connect.close()
            time.sleep(EDI_GET_SLEEP_TIME)
        except:
            print("Connect REMOTE database Failure! Sleep 30s, Try again!")
            time.sleep(30)
