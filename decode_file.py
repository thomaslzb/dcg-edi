#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
解码文件
@File    :   decode_file.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
04/12/2020 13:19   lzb       1.0         None
"""
import datetime
from const import FILTER_LOADING_PORT, FILTER_DELIVERY_PORT, FILTER_LOADING_COUNTRY
import re


def is_valid_file(file, file_type):
    """
    判断文件是否是合法的文件
    :param file:
    :param file_type:
    :return:
    """
    with open(file, 'r') as file:
        data = file.readlines()
    for line_data in data:
        if line_data.find(file_type) != -1:
            return True
    return False


def string_to_date(date_str):
    try:
        date_str = date_str[date_str.find(":") + 1:][0:date_str[date_str.find(":") + 1:].find(":")]
        if len(date_str) == 14:
            date_str = datetime.datetime.strptime(date_str, "%Y%m%d%H%M%S")
        elif len(date_str) == 12:
            date_str = datetime.datetime.strptime(date_str, "%Y%m%d%H%M")
        elif len(date_str) == 8:
            date_str = datetime.datetime.strptime(date_str, "%Y%m%d")
    except:
        date_str = ""
    return date_str


def get_one_line(content, start_string):
    end_string = "'"
    index = content.find(start_string)
    substring = content[index:]
    string = substring[0:substring.find(end_string)]
    return string


def get_element(line_content, position, sign):
    """
    从某行中取到特定的值
    :param line_content: 整行的内容
    :param position: 需要取值的位置
    :return: 获取的值
    """
    line = line_content
    i = 0
    while sign in line:
        index = line.find(sign) + 1
        line = line[index:]
        i = i + 1
        if i == position:
            break
    if line.find(sign) < 0:
        element = line
    else:
        element = line[0:line.find(sign)]
    return element


def encode_IFTMBC_file(file):
    """
    解码文件到一个list中
    :param file:
    :return:data_list
    """
    with open(file, 'r') as file:
        data = file.readlines()
    content = data[0]
    message_code = get_element(get_one_line(content, "UNB"), 5, "+")

    carrier_booking_number = get_element(get_one_line(content, "RFF+BN:"), 1, "+")
    carrier_booking_number = carrier_booking_number[carrier_booking_number.find(":") + 1:]

    booking_id = get_element(get_one_line(content, "BGM+770"), 2, "+")

    confirm_datetime = get_element(get_one_line(content, "DTM+134:"), 1, "+")
    confirm_datetime = string_to_date(confirm_datetime)

    voyage_no = get_element(get_one_line(content, "TDT+20"), 2, "+")

    voyage_name = get_element(get_one_line(content, "TDT+20"), 8, "+")

    receipt_country = get_element(get_one_line(content, "LOC+9"), 2, "+")
    receipt_country = receipt_country[0:2]

    receipt_port = get_element(get_one_line(content, "LOC+9"), 2, "+")
    receipt_port = receipt_port[2:5]

    start_date = get_element(get_one_line(content, "DTM+133:"), 1, "+")
    start_date = string_to_date(start_date)

    delivery_country = get_element(get_one_line(content, "LOC+11"), 2, "+")
    delivery_country = delivery_country[0:2]

    delivery_port = get_element(get_one_line(content, "LOC+11"), 2, "+")
    delivery_port = delivery_port[2:5]

    delivery_date = get_element(get_one_line(content, "DTM+132:"), 1, "+")
    delivery_date = string_to_date(delivery_date)

    data_list = (booking_id, carrier_booking_number, confirm_datetime,
                 voyage_name, voyage_no,
                 receipt_country, receipt_port, start_date,
                 delivery_country, delivery_port, delivery_date,
                 message_code)
    data_list = (data_list, )
    return data_list


def encode_IFTSAI_file(file):
    """
    解析 IFTSAI 文件 到一个 tuple 中
    :param file:
    :return:
    """
    # 取到文件的所有字符串
    with open(file, 'r') as file:
        all_data_list = file.readlines()

    carrier_company = get_element(get_one_line(all_data_list[0], "UNOA:1"), 1, "+")

    all_data_list = all_data_list[0].split("'", -1)
    # 将数据分组
    group = []
    each_record = []
    begin_go = False
    new_group = False
    for line_data in all_data_list:
        if line_data.find("UNH") != -1:  # 查询到，就开始计数
            each_record = []
            new_group = True
            begin_go = True

        if line_data.find("UNT") != -1:  # 查询到，就开始计数
            new_group = False

        if new_group and begin_go:
            each_record.append(line_data)
        else:
            if begin_go:
                group.append(each_record)

    # 将提取数据存入list中
    data_record = []
    for each_record in group:
        code = " ".join(each_record)

        message_code = get_element(get_one_line(code, "UNH"), 1, "+")
        message_date = get_element(get_one_line(code, "DTM+137"), 1, "+")
        message_date = string_to_date(message_date)

        voyage_name = get_element(get_one_line(code, "TDT"), 8, "+")
        voyage_name = get_element(voyage_name, 3, ":")

        route_name = get_element(get_one_line(code, "FTX"), 4, "+")

        voyage_no = get_element(get_one_line(code, "TDT"), 2, "+")

        place_of_receipt = get_element(get_one_line(code, "LOC+88"), 2, "+")[0:5]
        place_of_receipt_date = get_element(get_one_line(code, "DTM+180"), 1, "+")
        place_of_receipt_date = string_to_date(place_of_receipt_date)

        place_of_loading = get_element(get_one_line(code, "LOC+9"), 2, "+")[0:5]
        place_of_loading_date = get_element(get_one_line(code, "DTM+133"), 1, "+")
        place_of_loading_date = string_to_date(place_of_loading_date)

        place_of_discharge = get_element(get_one_line(code, "LOC+11"), 2, "+")[0:5]
        place_of_discharge_date = get_element(get_one_line(code, "DTM+132"), 1, "+")
        place_of_discharge_date = string_to_date(place_of_discharge_date)

        place_of_delivery = get_element(get_one_line(code, "LOC+7"), 2, "+")[0:5]
        place_of_delivery_date = get_element(get_one_line(code, "DTM+17"), 1, "+")
        place_of_delivery_date = string_to_date(place_of_delivery_date)

        if (place_of_loading in FILTER_LOADING_PORT or place_of_loading[:2] in FILTER_LOADING_COUNTRY) \
                and place_of_delivery in FILTER_DELIVERY_PORT:
            data_record.append((message_code, message_date, route_name,
                                voyage_name, voyage_no,
                                place_of_delivery, place_of_delivery_date,
                                place_of_receipt, place_of_receipt_date,
                                place_of_loading, place_of_loading_date,
                                place_of_discharge, place_of_discharge_date,
                                carrier_company,
                                ))
    return data_record
