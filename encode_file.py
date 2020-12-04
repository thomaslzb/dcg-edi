#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
解码文件
@File    :   encode_file.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
04/12/2020 13:19   lzb       1.0         None
"""
import os


def is_valid_file(file, file_type):
    """
    判断文件是否是合法的文件
    :param file:
    :param file_type:
    :return:
    """
    with open(file, 'r') as file:
        data = file.readlines()
    content = data[0]
    if content.find(file_type) == -1:
        return False
    return True


def get_one_line(content, start_string, end_string):
    return content[0:content[content.find(start_string):].find(end_string)]


def encode_file(db_connect, file):
    """
    解码文件到一个list中
    :param db_connect:
    :param file:
    :return:
    """ 
    data_list = []
    with open(file, 'r') as file:
        data = file.readlines()
    content = data[0]
    function_code = "UNB"
    line_string = get_one_line(content, function_code, "'")
    function_code = "UNH"
    line_string = get_one_line(content, function_code, "'")
    return data_list
