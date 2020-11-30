#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   ftp_file.py    
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
from distutils import file_util
import ftplib
import os
import time
import socket
from concurrent.futures import ThreadPoolExecutor

FTP_SERVICE = {
    'HOST': '47.115.73.25',
    'USERNAME': "ftpdcg",
    'PASSWORD': "dcg123.",
}

host = '47.115.73.25'
username = 'ftpdcg'
password = 'dcg123.'
file = 'readme.txt'
port = 21


def ftpconnect(host, port, username, password):
    ftp = ftplib.FTP()
    # ftp.set_debuglevel(2)         #打开调试级别2，显示详细信息
    ftp.encoding = 'utf-8'  # 解决中文编码问题，默认是latin-1
    try:
        ftp.connect(host, port)  # 连接
        ftp.login(username, password)  # 登录，如果匿名登录则用空串代替即可
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


def uploadfile(ftp, remotepath, localpath):
    """
    上传文件
    :param ftp:
    :param remotepath:
    :param localpath:
    :return:
    """
    bufsize = 1024
    fp = open(localpath, 'rb')
    res = ftp.storbinary('STOR ' + remotepath, fp, bufsize)  # 上传文件
    if res.find('226') != -1:
        print('upload file complete', remotepath)
    ftp.set_debuglevel(0)
    fp.close()


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


if __name__ == "__main__":

    import ftplib

    ftp = ftplib.FTP()
    ftp.set_debuglevel(2)
    ftp.encoding = 'utf-8'
    try:
        ftp.connect(host, port)
        ftp.login(username, password)
        ftp.af = socket.AF_INET6  # IMPORTMENT: force ftplib to use EPSV by setting
        print(ftp.getwelcome())
    except(socket.error, socket.gaierror):  # ftp error
        print("ERROR: cannot connect [{}:{}]".format(host, port))
    except ftplib.error_perm:  # user Authentication failed
        print("ERROR: user Authentication failed ")

    filename = 'readme.txt'

    files = []
    ftp.dir()
    print(files)
    file_list = ftp.nlst()  # 获取目录下的文件
    print(file_list)

    # Method 1
    try:
        with open("readme.txt", 'rb') as fp:
            res = ftp.storlines("STOR " + filename, fp)
            if not res.startswith('226 Transfer complete'):
                print('Upload failed')

    except ftplib.all_errors as e:
        print('FTP error:', e)

    # Method 2
    try:
        bufsize = 1024
        fp = open("readme.txt", 'rb')
        res = ftp.storbinary('STOR ' + "readme", fp, bufsize)  # 上传文件
        if res.find('226') != -1:
            print('upload file complete', "readme")
    except ftplib.all_errors as e:
        print('FTP error:', e)

    # ftp.close()

    # ftp_msg = ftp.pwd()
    # print(ftp_msg)
    #
    # ftp.cwd('dcg')
    # ftp_msg = ftp.pwd()
    # print(ftp_msg)
    # files = []


    start = time.time()


    # uploadfile(ftp, ftp_msg, "readme.txt",)  # 上传文件
    # ftp.delete("api-error.log")  # testing ok
    ftp.quit()

#
# def up_to_ftp(edi_file):
#     file_path = Path(edi_file)
#
#     with FTP(FTP_SERVICE['HOST'], FTP_SERVICE['USERNAME'], FTP_SERVICE['PASSWORD']) as ftp, open(file_path, 'rb') as file:
#         ftp.storbinary(f'STOR {file_path.name}', file)
#
#
# ftp = FTP()
# host = "47.115.73.25"
# port = 21
# ftp.connect(host, port)
# print(ftp.getwelcome())
# try:
#     print("Logging in...")
#     myFTP = FTP(host, "ftpdcg", "dcg123.")
#     ftp.set_debuglevel(2)
#     with myFTP, open('C://DCG//GitHub//dcg-edi//sendfile-upftp', 'rb') as file:
#         ftp.storbinary(f'STOR {"C://DCG//GitHub//dcg-edi//sendfile-upftp//abc.txt"}', file)
#
# except:
#     "failed to login"
#
# # filename = "FTP-abc.txt"
# # ftp = FTP('47.115.73.25')
# # ftp.login('ftpdcg', 'dcg123.')
# # # ftp.cwd('Articles')
# # uploadfile = open('C://DCG//GitHub//dcg-edi//sendfile-upftp//abc.txt', 'rb')
# #
# # ftp.storlines('STOR ' + filename, uploadfile)
# #
