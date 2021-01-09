#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   ftp_demo.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
05/01/2021 17:13   lzb       1.0         ftp client

https://www.thinbug.com/q/19245769
https://github.com/keepitsimple/pyFTPclient
"""
import os

from const import *
import threading
import logging
import ftplib
import socket
import time


def setInterval(interval, times=-1):
    # This will be the actual decorator,
    # with fixed interval and times parameter
    def outer_wrap(function):
        # This will be the function to be
        # called
        def wrap(*args, **kwargs):
            stop = threading.Event()

            # This is another function to be executed
            # in a different thread to simulate setInterval
            def inner_wrap():
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


class PyFTPclient:
    def __init__(self, host, port=21, login='anonymous', passwd='anonymous', monitor_interval=30):
        self.host = host
        self.port = port
        self.login = login
        self.passwd = passwd
        self.monitor_interval = monitor_interval
        self.ptr = None
        self.max_attempts = 15
        self.waiting = True

    def connect(self, ftp, dst_path=None):
        if dst_path is None:
            dst_path = ""

        ftp.connect(self.host, self.port)
        ftp.login(self.login, self.passwd)
        #  ======================== VERY IMPORTANT ===========================
        ftp.af = socket.AF_INET6  # 这个设置非常重要: force ftplib to use EPSV by setting
        #  ======================== VERY IMPORTANT ===========================
        # optimize socket params for download task
        ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
        ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
        ftp.cwd(dst_path)  # 转换至需要的FTP目标目录

    def isHaveFtpPath(self, ftp, dst_ftp_path=None):
        if dst_ftp_path is None:
            dst_ftp_path = ""
        try:
            if dst_ftp_path in ftp.nlst(os.path.dirname(dst_ftp_path)):
                return True
            else:
                return False
        except ftplib.error_perm:
            return False

    def DownloadFile(self, dst_filename, local_filename=None, dst_path=None):
        """
        下载文件函数
        :param dst_filename: 目标文件名
        :param local_filename: 本地文件名
        :param dst_path: 目标目录
        :return: 1 = Success None = Failure
        """
        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_DOWNLOAD_PATH)
        if local_filename is None:
            local_filename = dst_filename

        local_filename = os.path.join(local_path, local_filename)

        if dst_path is None:
            dst_path = ""

        with open(local_filename, 'wb') as f:
            self.ptr = f.tell()

            @setInterval(self.monitor_interval)
            def monitor():
                if not self.waiting:
                    i = f.tell()
                    if self.ptr < i:
                        logging.info("File size is %d  - speed is %0.1f Kb/s" % (i, (i-self.ptr)/(1024*self.monitor_interval)))
                        self.ptr = i
                    else:
                        ftp.close()

            ftp = ftplib.FTP()
            ftp.set_debuglevel(2)
            ftp.set_pasv(True)

            self.connect(ftp, dst_path)
            ftp.voidcmd('TYPE I')
            dst_file_size = ftp.size(dst_filename)

            mon = monitor()   # begin monitor
            while dst_file_size > f.tell():
                try:
                    self.connect(ftp, dst_path)
                    self.waiting = False
                    # retrieve file from position where we were disconnected
                    res = ftp.retrbinary('RETR %s' % dst_filename, f.write) if f.tell() == 0 else \
                        ftp.retrbinary('RETR %s' % dst_filename, f.write, rest=f.tell())

                except:
                    self.max_attempts -= 1
                    if self.max_attempts == 0:
                        mon.set()
                        logging.exception('')
                        # raise
                        logging.debug("max attempts 30 times.")
                    self.waiting = True
                    logging.info('waiting 30 sec...')
                    time.sleep(30)
                    logging.info('reconnect')

            mon.set()  # stop monitor
            ftp.close()

            try:
                if not res.startswith('226 Transfer complete'):
                    logging.error('Downloaded file {0} is not full.'.format(dst_filename))
                    # os.remove(local_filename)
                    return None
            except:
                logging.debug("Res Error")
                return None
            return 1


if __name__ == "__main__":
    logging.basicConfig(filename=FTP_LOG_FILENAME, format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    obj = PyFTPclient(FTP_HOST, port=FTP_PORT, login=FTP_USERNAME, passwd=FTP_PASSWORD)
    while True:
        ftp_connect = ftplib.FTP()
        ftp_connect.set_debuglevel(2)
        ftp_connect.set_pasv(True)

        obj.connect(ftp_connect, REMOTE_FPT_PATH)

        all_files_name = ftp_connect.nlst()  # 获取远程FTP的所有文件名

        for file_name in all_files_name:
            start_time = time.time()
            logging.info("Downloading file:" + file_name)
            if obj.DownloadFile(file_name, None, REMOTE_FPT_PATH):
                info_status = "Success"
                # 下载成功后，删除远程的文件
                # ftp_connect.delete(file_name)  # 删除远程FTP文件
            else:
                info_status = "Failure"

            spend_time = time.time() - start_time
            logging.info(info_status + " download file: " + file_name + "... {:3.6f}".format(spend_time) + "s. ")

        ftp_connect.close()
        time.sleep(FTP_SLEEP_TIME)
