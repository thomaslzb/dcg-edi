#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   ftp_tools.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

ftp登陆连接
from ftplib import FTP            #加载ftp模块
ftp=FTP()                         #设置变量
ftp.set_debuglevel(2)             #打开调试级别2，显示详细信息
ftp.connect("IP","port")          #连接的ftp sever和端口
ftp.login("user","password")      #连接的用户名，密码
print ftp.getwelcome()            #打印出欢迎信息
ftp.cmd("xxx/xxx")                #进入远程目录
bufsize=1024                      #设置的缓冲区大小
filename="filename.txt"           #需要下载的文件
file_handle=open(filename,"wb").write #以写模式在本地打开文件
ftp.retrbinaly("RETR filename.txt",file_handle,bufsize) #接收服务器上文件并写入本地文件
ftp.set_debuglevel(0)             #关闭调试模式
ftp.quit()                        #退出ftp

ftp相关命令操作
ftp.cwd(pathname)                 #设置FTP当前操作的路径
ftp.dir()                         #显示目录下所有目录信息
ftp.nlst()                        #获取目录下的文件
ftp.mkd(pathname)                 #新建远程目录
ftp.pwd()                         #返回当前所在位置
ftp.rmd(dirname)                  #删除远程目录
ftp.delete(filename)              #删除远程文件
ftp.rename(fromname, toname)#将fromname修改名称为toname。
ftp.storbinaly("STOR filename.txt",file_handel,bufsize)  #上传目标文件
ftp.retrbinary("RETR filename.txt",file_handel,bufsize)  #下载FTP文件

https://www.cnblogs.com/xiao-apple36/p/9675185.html

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
27/11/2020 12:17   lzb       1.0         None
"""

# FTP操作
import ftplib
import logging
import os
import socket
import time
import shutil

from const import *


def create_ftp_connect(host, port, username, password, is_EPSV=True):
    """
    建立FTP连接
    :param is_EPSV: 判断是否转成 EPSV 模式， MSK 公司的不需要转换成该模式
    :param host:
    :param port:
    :param username:
    :param password:
    :return: FTP 连接

    """
    ftp_connect = ftplib.FTP()
    # ftp.set_debuglevel(2)         #打开调试级别2，显示详细信息
    ftp_connect.encoding = 'utf-8'  # 解决中文编码问题，默认是latin-1
    try:
        ftp_connect.connect(host, port)  # 连接
        ftp_connect.login(username, password)  # 登录，如果匿名登录则用空串代替即可
        if is_EPSV:
            ftp_connect.af = socket.AF_INET6  # IMPORTANT: force ftplib to use EPSV by setting
        print(ftp_connect.getwelcome())  # 打印欢迎信息
    except(socket.error, socket.gaierror):  # ftp 连接错误
        logging.exception("ERROR!")
        print("ERROR: cannot connect [{}:{}]".format(host, port))
        return None
    except ftplib.error_perm:  # 用户登录认证错误
        logging.info("ERROR: user Authentication failed ")
        print("ERROR: user Authentication failed ")
        return None
    return ftp_connect


def is_ftp_file(ftp_conn, ftp_path):
    try:
        if ftp_path in ftp_conn.nlst(os.path.dirname(ftp_path)):
            return True
        else:
            return False
    except ftplib.error_perm:
        return False


def uploading_file(ftp_connect, remote_name, upload_file):
    """
    上传文件
    :param ftp_connect: FTP connect name
    :param remote_name: remote file name
    :param upload_file: the file you need to upload
    :return: True
    """
    is_send = False
    try:
        with open(upload_file, 'rb') as fp:
            res = ftp_connect.storlines("STOR " + remote_name, fp)
            if res.startswith('226 Transfer complete'):
                logging.info("Upload File success....."+upload_file)
                print(upload_file+'.... Upload success.')
                is_send = True
            else:
                logging.info("Upload File failure....." + res)
                print('Upload failed')
    except ftplib.all_errors as e:
        logging.exception("FTP Error!" + e)
        print('FTP error:', e)

    return is_send


def get_file_list(directory, file_list):
    """
    使用递归算法，扫描文件夹directory中所有文件，返回文件的相对路径列表
    :param directory:
    :param file_list:
    :return:
    """
    newDir = directory
    if os.path.isfile(directory):         # 如果是文件则添加进 fileList
        file_list.append(directory)
    elif os.path.isdir(directory):
        for s in os.listdir(directory):   # 如果是文件夹
            newDir = os.path.join(directory, s)
            get_file_list(newDir, file_list)
    return file_list


