#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   const.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
25/11/2020 12:33   lzb       1.0         None
"""

REMOTE_DATABASE = False  # 是否连接远程数据库
IS_UNIX_OS = False  # 是否是服务器

PROGRAM_DEBUG = False  # 是否DEBUG
RECORD_LOGGING = False  # 是否记录logging

IP_DB_LOCAL = '127.0.0.1'
LOCAL_DATABASE_USERNAME = "ukdcg"
LOCAL_DATABASE_PWD = "ukthomas"
LOCAL_DATABASE_NAME = "edi"

IP_DATABASE = '47.115.73.25'
REMOTE_DATABASE_USERNAME = "dcguk"
REMOTE_DATABASE_PWD = "a1d2m3."
REMOTE_DATABASE_NAME = "edi"

EDI_SLEEP_TIME = 60

LOCAL_UPLOAD_DIR = "sendfile-ftp"
LOCAL_UPLOAD_BACKUP_DIR = "sendfile-bak"

LOCAL_DOWNLOAD_DIR = "getfile-ftp"
LOCAL_DOWNLOAD_BACKUP_DIR = "getfile-bak"


REMOTE_DIRECTORY = "testing"

HOST = '47.115.73.25'
USERNAME = 'ftpdcg'
PASSWORD = 'dcg123.'
PORT = 21

UPLOADING_SLEEP_TIME = 60
