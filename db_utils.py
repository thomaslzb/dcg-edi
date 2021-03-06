#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   db_utils.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
14/10/2020 12:56   lzb       1.0         None
"""
import logging
import pyodbc
from const import *


# 连接远程的 MS SQL SERVER 数据库
def connect_remote_db():
    connect = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + IP_DATABASE
                             + ';DATABASE=' + REMOTE_DATABASE_NAME
                             + ';UID=' + REMOTE_DATABASE_USERNAME
                             + ';PWD=' + REMOTE_DATABASE_PWD
                             + '; CHARSET=UTF8'
                             + ';sslca={BaltimoreCyberTrustRoot.crt.pem}; sslverify=0; Option=3;'
                             )
    return connect


def select_sql(db_connects, sql):
    """
    :param db_connects: database
    :param sql:
    :return: cursor
    """
    cursor = db_connects.cursor()
    cursor.execute(sql)  # 取到所有未处理的数据， 一次最多处理60条
    return cursor


def select_sql_data(db_connects, sql, data):
    """
    :param data: param
    :param db_connects: database
    :param sql: sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    cursor.execute(sql, data)  # 取到所有未处理的数据
    return cursor


def update_sql(db_connects, sql, data):
    """
    :param db_connects: database
    :param data: value
    :param sql: update sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    try:
        cursor.execute(sql, data)
        db_connects.commit()
    except:
        logging.exception("exception")
        db_connects.rollback()
    cursor.close()


def insert_sql(db_connects, sql, data):
    """
    :param db_connects: database
    :param data: value
    :param sql: update sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    try:
        cursor.execute(sql, data)
        db_connects.commit()
    except:
        logging.exception("exception")
        db_connects.rollback()
    cursor.close()


def insert_sql_many(db_connects, sql, data):
    """
    :param db_connects: database
    :param data: value
    :param sql: update sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    try:
        cursor.fast_executemany = True
        cursor.executemany(sql, data)
        db_connects.commit()
    except:
        logging.exception("exception")
        db_connects.rollback()
    cursor.close()

