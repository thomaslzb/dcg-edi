#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   file_uploading.py
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
import os
import socket
import time
import shutil

from const import *
from concurrent.futures import ThreadPoolExecutor


def ftpconnect(host, port, username, password):
    ftp = ftplib.FTP()
    # ftp.set_debuglevel(2)         #打开调试级别2，显示详细信息
    ftp.encoding = 'utf-8'  # 解决中文编码问题，默认是latin-1
    try:
        ftp.connect(host, port)  # 连接
        ftp.login(username, password)  # 登录，如果匿名登录则用空串代替即可
        ftp.af = socket.AF_INET6  # IMPORTMENT: force ftplib to use EPSV by setting
        print(ftp.getwelcome())  # 打印欢迎信息
    except(socket.error, socket.gaierror):  # ftp 连接错误
        print("ERROR: cannot connect [{}:{}]".format(host, port))
        return None
    except ftplib.error_perm:  # 用户登录认证错误
        print("ERROR: user Authentication failed ")
        return None
    return ftp


def is_ftp_file(ftp_conn, ftp_path):
    try:
        if ftp_path in ftp_conn.nlst(os.path.dirname(ftp_path)):
            return True
        else:
            return False
    except ftplib.error_perm:
        return False


def downloadfile(ftp, remotepath, localpath):
    """
     下载文件
    :param ftp:
    :param remotepath:
    :param localpath:
    :return:
    """
    bufsize = 1024  # 设置缓冲块大小
    fp = open(localpath, 'wb')  # 以写模式在本地打开文件

    res = ftp.retrbinary(
        'RETR ' + remotepath,
        fp.write,
        bufsize)  # 接收服务器上文件并写入本地文件
    if res.find('226') != -1:
        print('download file complete', localpath)
    ftp.set_debuglevel(0)  # 关闭调试
    fp.close()  # 关闭文件


def uploadfile(ftp, remotepath, upload_file):
    """
    上传文件
    :param ftp:
    :param remotepath:
    :param upload_file:
    :return: True
    """
    is_send = False
    try:
        with open(upload_file, 'rb') as fp:
            res = ftp.storlines("STOR " + remotepath, fp)
            if res.startswith('226 Transfer complete'):
                print(upload_file+'.... Upload success.')
                is_send = True
            else:
                print('Upload failed')
    except ftplib.all_errors as e:
        print('FTP error:', e)

    return is_send


def ftp_theadpool(func, ftp, file_list):
    """
    通过线程池调用上传文件列表
    :param func:
    :param file_list:
    :return:
    """
    pool = ThreadPoolExecutor(6)
    for remotepath, localpath in file_list:
        pool.submit(func, ftp, remotepath, localpath)
    pool.shutdown()


def get_file_list(directory, files_list):
    """
    扫描文件夹directory中所有文件，返回文件的相对路径列表
    :param directory:
    :param files_list:
    :return:
    """
    newDir = directory
    if os.path.isfile(directory):         # 如果是文件则添加进 fileList
        files_list.append(directory)
    elif os.path.isdir(directory):
        for s in os.listdir(directory):   # 如果是文件夹
            newDir = os.path.join(directory, s)
            get_file_list(newDir, files_list)
    return files_list


if __name__ == "__main__":
    while True:
        files_list = []
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_UPLOAD_DIR)
        bak_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_UPLOAD_BACKUP_DIR)
        files_list = get_file_list(local_path, [])
        if files_list:
            ftp = ftpconnect(HOST, PORT, USERNAME, PASSWORD)
            ftp.cwd(REMOTE_DIRECTORY)
            for file in files_list:
                (path, filename) = os.path.split(file)
                remote_file = filename
                # 上传文件
                if uploadfile(ftp, remote_file, file):
                    # remove to bak
                    try:
                        shutil.move(file, bak_path)
                        print(file+"..... Move file success....")
                    except:
                        print("Move file failure....")
                    pass
            ftp.close()
        else:
            time.sleep(UPLOADING_SLEEP_TIME)
            print("FTP Servicing is sleeping ...")

