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
from encode_file import encode_file, is_valid_file
from ftp_tools import create_ftp_connect, is_ftp_file, download_file
from sql_const import SELECT_BOOKING_SQL, INSERT_BOOKING_RESULT


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
                # 查询是否所有文件中，是否有已经处理完成的的文件，有的话，删除远程的文件
                files = checked_file(connect_db, all_files)
                delete_files = files[0]
                for file in delete_files:
                    ftp.delete(file)  # 删除远程FTP文件

                download_files = files[1]
                if download_files:
                    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_DIR)
                    bak_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_BACKUP_DIR)
                    # 下载需要的文件，下载成功后，删除文件
                    success_download_files = download_file_to_local(ftp, download_files, local_path)
                    for file in success_download_files:

                        # 处理已经下载的文件，更新到数据库中
                        file_type = "IFTMBC"
                        local_file = os.path.join(local_path, file)

                        if is_valid_file(local_file, file_type):
                            data_list = encode_file(connect_db, local_file)
                            # 更新数据
                            # insert_sql(connect_db, INSERT_BOOKING_RESULT, data_list)

                            # ftp.delete(file)  # 删除远程FTP文件

                            try:
                                # 将处理完成后的文件，移除到备份目录中
                                start_time = time.time()
                                shutil.copy(file, bak_path)
                                os.remove(file)
                                if PROGRAM_DEBUG:
                                    spend_time = time.time() - start_time
                                    print(" ** Step7: 将文件 " + file + "移至到备份目录中...." + "{:3.6f}".format(spend_time) + "s. ")
                            except:
                                if PROGRAM_DEBUG:
                                    spend_time = time.time() - start_time
                                    print(file + " ** Step7: 将文件移至到备份目录失败...." + "{:3.6f}".format(spend_time) + "s. ")

        else:
            if PROGRAM_DEBUG:
                spend_time = time.time() - start_time
                print(" ** Step2: 连接远程的FTP服务器目录不正确..." + "{:3.6f}".format(spend_time) + "s. ")

        # 关闭FTP连接
        ftp.close()
    else:
        if PROGRAM_DEBUG:
            spend_time = time.time() - start_time
            print(" ** Step5: 连接远程的FTP服务器...失败 " + "{:3.6f}".format(spend_time) + "s. ")


# main progress
if __name__ == "__main__":
    is_connect_db = True
    if REMOTE_DATABASE:  # 连接远程数据库
        db_connect = connect_remote_db()
        print("Connect REMOTE database success!")

        while is_connect_db:
            print("Begin Searching files...")
            main_progress(db_connect)
            print("EDI GET File System Sleeping ...\n")
            time.sleep(EDI_GET_SLEEP_TIME)
        db_connect.close()
    else:
        print("Connect REMOTE database Failure!")
