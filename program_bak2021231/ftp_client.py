#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   ftp_demo.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
05/01/2021 17:13   lzb       1.0         None

https://www.thinbug.com/q/19245769
https://github.com/keepitsimple/pyFTPclient
"""

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

    def download_testing(self, dst_filename, local_filename=None):
        if local_filename is None:
            local_filename = dst_filename

        ftp = ftplib.FTP()
        ftp.set_debuglevel(2)
        ftp.set_pasv(True)

        ftp.connect(self.host, self.port)
        ftp.login(self.login, self.passwd)
        ftp.af = socket.AF_INET6  # IMPORTMENT: force ftplib to use EPSV by setting
        # ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        # ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
        # ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)

        # ftp.voidcmd('TYPE I')
        try:
            ftp.cwd(REMOTE_DIRECTORY)  # 转换至需要上传的目录

            bufsize = 1024  # 设置缓冲块大小
            fp = open(local_filename, 'wb')  # 以写模式在本地打开文件

            res = ftp.retrbinary('RETR ' + dst_filename, fp.write, bufsize)  # 接收服务器上文件并写入本地文件
        except:
            logging.info('waiting 30 sec...')

        if res.find('226') != -1:
            is_download = True
            # print('download file complete', local_name)
        ftp.set_debuglevel(0)  # 关闭调试

    def DownloadFile(self, dst_filename, local_filename=None):
        if local_filename is None:
            local_filename = dst_filename

        with open(local_filename, 'wb') as f:
            self.ptr = f.tell()

            @setInterval(self.monitor_interval)
            def monitor():
                if not self.waiting:
                    i = f.tell()
                    if self.ptr < i:
                        logging.debug("%d  -  %0.1f Kb/s" % (i, (i-self.ptr)/(1024*self.monitor_interval)))
                        self.ptr = i
                    else:
                        ftp.close()

            def connect():
                ftp.connect(self.host, self.port)
                ftp.login(self.login, self.passwd)
                #  ======================== VERY IMPORTANT ===========================
                ftp.af = socket.AF_INET6   # VERY IMPORTANT: force ftplib to use EPSV by setting
                #  ======================== VERY IMPORTANT ===========================
                # optimize socket params for download task
                ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
                ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)

            ftp = ftplib.FTP()
            ftp.set_debuglevel(2)
            ftp.set_pasv(True)

            connect()
            ftp.voidcmd('TYPE I')
            ftp.cwd(REMOTE_DIRECTORY)  # 转换至需要上传的目录
            dst_filesize = ftp.size(dst_filename)

            # mon = monitor()
            while dst_filesize > f.tell():
                try:
                    # connect()
                    self.waiting = False
                    # retrieve file from position where we were disconnected
                    res = ftp.retrbinary('RETR %s' % dst_filename, f.write) if f.tell() == 0 else \
                        ftp.retrbinary('RETR %s' % dst_filename, f.write, rest=f.tell())

                except:
                    self.max_attempts -= 1
                    if self.max_attempts == 0:
                        # mon.set()
                        logging.exception('')
                        raise
                    self.waiting = True
                    logging.info('waiting 30 sec...')
                    time.sleep(30)
                    logging.info('reconnect')

            # mon.set()  #stop monitor
            ftp.close()

            if not res.startswith('226 Transfer complete'):
                logging.error('Downloaded file {0} is not full.'.format(dst_filename))
                # os.remove(local_filename)
                return None

            return 1


if __name__ == "__main__":
    logging.basicConfig(filename=LOCAL_LOG_DIR, format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.DEBUG)
    # logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=cfg.logging.level)
    obj = PyFTPclient(FTP_HOST, port=FTP_PORT, login=FTP_USERNAME, passwd=FTP_PASSWORD)
    # obj.download_testing('demo.log')
    obj.DownloadFile('demo.log')
