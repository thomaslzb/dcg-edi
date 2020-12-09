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
import datetime


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


def string_to_date(date_str):
    date_str = date_str[date_str.find(":") + 1:][0:date_str[date_str.find(":") + 1:].find(":")]
    date_str = datetime.datetime.strptime(date_str, "%Y%m%d%H%M")
    return date_str


def get_one_line(content, start_string):
    end_string = "'"
    index = content.find(start_string)
    substring = content[index:]
    string = substring[0:substring.find(end_string)]
    return string


def get_element(line_content, position):
    """
    从某行中取到特定的值
    :param line_content: 整行的内容
    :param position: 需要取值的位置
    :return: 获取的值
    """
    line = line_content
    sign = "+"
    i = 0
    while sign in line:
        index = line.find(sign) + 1
        line = line[index:]
        i = i + 1
        if i == position:
            break
    element = line[0:line.find(sign)]
    return element


def encode_IFTMBC_file(file):
    """
    解码文件到一个list中
    :param db_connect:
    :param file:
    :return:data_list
    """
    data_list = []
    with open(file, 'r') as file:
        data = file.readlines()
    content = data[0]
    exchange_ref = get_element(get_one_line(content, "UNB"), 5)

    carrier_booking_number = get_element(get_one_line(content, "RFF+BN:"), 1)
    carrier_booking_number = carrier_booking_number[carrier_booking_number.find(":") + 1:]

    booking_id = get_element(get_one_line(content, "BGM+770"), 2)

    confirm_datetime = get_element(get_one_line(content, "DTM+134:"), 1)
    confirm_datetime = string_to_date(confirm_datetime)

    voyage_no = get_element(get_one_line(content, "TDT+20"), 2)

    voyage_name = get_element(get_one_line(content, "TDT+20"), 8)

    receipt_country = get_element(get_one_line(content, "LOC+9"), 2)
    receipt_country = receipt_country[0:2]

    receipt_port = get_element(get_one_line(content, "LOC+9"), 2)
    receipt_port = receipt_port[2:5]

    start_date = get_element(get_one_line(content, "DTM+133"), 2)
    start_date = string_to_date(start_date)

    delivery_country = get_element(get_one_line(content, "LOC+11"), 2)
    delivery_country = delivery_country[0:2]

    delivery_port = get_element(get_one_line(content, "LOC+11"), 2)
    delivery_port = delivery_port[2:5]

    delivery_date = get_element(get_one_line(content, "DTM+132"), 2)
    delivery_date = string_to_date(delivery_date)

    data_list = [booking_id, carrier_booking_number, confirm_datetime,
                 voyage_name, voyage_no,
                 receipt_country, receipt_port, start_date,
                 delivery_country, delivery_port, delivery_date,
                 exchange_ref, ]

    return data_list
