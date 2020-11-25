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
import pymssql
import pymysql


# 连接数据库
def connect_local_db():
    connect = pymysql.Connect(
        host='127.0.0.11',
        port=3306,
        user='ukdcg',
        passwd='ukthomas',
        db='edi',
        charset='utf8'
    )
    return connect


# 连接数据库
def connect_remote_db():
    connect = pymssql.connect(
        host='47.115.73.25',
        port=1433,
        user='dcguk',
        password='a1d2m3.',
        database='edi',
        charset='utf8'
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
    :param db_connects: database
    :param sql:
    :return: cursor
    """
    cursor = db_connects.cursor()
    cursor.execute(sql % data)  # 取到所有未处理的数据， 一次最多处理60条
    return cursor


def update_sql(db_connects, sql, data):
    """
    :param db_connects: database
    :param data: value
    :param sql: update sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    cursor.execute(sql % data)
    db_connects.commit()
    cursor.close()


def insert_sql(db_connects, sql, data):
    """
    :param db_connects: database
    :param data: value
    :param sql: update sql
    :return: cursor
    """
    cursor = db_connects.cursor()
    cursor.execute(sql % data)
    db_connects.commit()
    cursor.close()
