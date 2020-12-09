#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
台湾长荣EDI的报文编写
@File    :   evengreen_files.py
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li
写EDI的文件
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
27/11/2020 09:33   lzb       1.0         None
"""
import os
import datetime
from db_utils import *
from sql_const import *


def get_country_name(connect_db, country_code):
    """
    返回国家名称
    :param connect_db: 数据库连接
    :param country_code: 国家代码 2 位
    :return: name 国家名称
    """
    name = ""
    data = [country_code,]
    booking_cursor = select_sql_data(connect_db, SELECT_COUNTRY_SQL, data)  # 取到数据
    get_row = booking_cursor.fetchone()
    if get_row:
        name = get_row[0].strip()
    return name


def get_country_port_name(connect_db, country_code, port_code):
    """
    返回国家名称
    :param connect_db: 数据库连接
    :param country_code: 国家代码 2 位
    :param port_code: 港口代码 3 位
    :return: port_name
    """
    port_name = ""
    data = [country_code, port_code]
    booking_cursor = select_sql_data(connect_db, SELECT_COUNTRY_PORT_SQL, data)  # 取到数据
    get_row = booking_cursor.fetchone()
    if get_row:
        port_name = get_row[0].strip()
    return port_name


def encoding_edi_file(data, connect_db):
    """
    将数据，写入到EDI FILE 中
    :param data: EDI FILE 的数据
    :param connect_db: 数据库连接
    :return:
    """

    content_list = []
    # 文件头： 时间+预定单号
    # UNB+UNOA:3+DCG+EGLV:ZZZ+201123:1409+DCG2001'
    op_date = datetime.datetime.now().strftime("%y%m%d")
    op_time = datetime.datetime.now().strftime("%H%M")
    content_list.append("UNB+UNOA:3+DCG+EGLV:ZZZ+" + op_date + ":" + op_time + "+" + data["booking_id"])

    # UNH+DCG2001+IFTMBF:D:99B:UN:2.0'
    content_list.append("UNH+" + data["booking_id"] + "+IFTMBF:D:99B:UN:2.0")

    # BGM+335+dcgtestbooking001+9'
    content_list.append("BGM+335+" + data["booking_id"] + "+9")

    # CTA+IC+:MARK'
    content_list.append("CTA+IC+:" + data["contact"])

    # COM+?+00861581388333:TE'
    content_list.append("COM+?+" + data["telephone"] + ":TE")

    # COM+mark@dcglogistics.com:EM'
    content_list.append("COM+" + data["email"] + ":EM")

    # DTM+137:20201123:102'
    op_datetime = datetime.datetime.now().strftime("%Y%m%d")
    content_list.append("DTM+137:" + op_datetime + ":102")

    # TSR+30+2' ---- Transport Service Requirements
    content_list.append("TSR+" + data["transport_service_mode"] + "+2")

    # FTX+AAI+++TEST ONLY'

    # RFF+SI:DCG2020112301'
    content_list.append("RFF+SI:" + data["booking_id"])

    # RFF+CT:CND005244'
    content_list.append("RFF+CT:" + data["contract_no"])

    # LOC+88+TWKHH:181:6:Kaohsiung+TW:162:5:Taiwan'
    country_name = get_country_name(connect_db, data["receipt_country"])
    port_name = get_country_port_name(connect_db, data["receipt_country"], data["receipt_port"])
    content_list.append("LOC+88+" + data["receipt_country"] + data["receipt_port"] + ":181:6:"
                        + port_name + "+" + data["receipt_country"] + ":162:5:" + country_name)

    # DTM+196:20201210:102'
    content_list.append("DTM+196:" + data["scheduled_date"] + ":102")

    # LOC+7+GBFXT:181:6:Felixstowe'
    content_list.append("LOC+7+" + data["delivery_country"] + data["delivery_port"] + ":181:6:"
                        + data["delivery_port_name"])

    # LOC+9+TWKHH:139:6:Kaohsiung+TW:162:5:Taiwan'
    content_list.append("LOC+9+" + data["receipt_country"] + data["receipt_port"] + ":139:6:"
                        + port_name + "+" + data["receipt_country"] + ":162:5:" + country_name)

    # LOC+11+GBFXT:139:6:Felixstowe+GB:162:5:United Kingdom'
    content_list.append("LOC+11+" + data["delivery_country"] + data["delivery_port"] + ":139:6:"
                        + data["delivery_port_name"] + "+" + data["delivery_country"] + ":162:5:"
                        + data["delivery_country_name"])

    # NAD+ZZZ+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    content_list.append("NAD+ZZZ+++" + data["business_name"] + "+" + data["address1"] + "+ "
                        + data["address2"] + "+" + data["town"] + "+" + data["postcode"] + "+" + data["country"])

    # CTA+IC+:THOMAS LI'
    content_list.append("CTA+IC+:" + data["contact"])

    # NAD+CZ+++BOWER GREEN LIMITED '
    content_list.append("NAD+CZ+++BOWER GREEN LIMITED")

    # NAD+CN+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    content_list.append("NAD+CN+++" + data["business_name"] + "+" + data["address1"] + "+ "
                        + data["address2"] + "+" + data["town"] + "+" + data["postcode"] + "+" + data["country"])

    # NAD+NI+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    content_list.append("NAD+NI+++" + data["business_name"] + "+" + data["address1"] + "+ "
                        + data["address2"] + "+" + data["town"] + "+" + data["postcode"] + "+" + data["country"])

    # CTA+IC+:THOMAS'
    content_list.append("CTA+IC+:" + data["contact"])

    # COM+?+004407421900978:TE'
    content_list.append("COM+?+" + data["telephone"] + ":TE")

    # COM+mark@dcglogistics.com:EM'
    content_list.append("COM+" + data["email"] + ":EM")

    # NAD+CA+EGLV:160:86+EVERGREEN MARINE CORP (M) SDN BHD'
    content_list.append("NAD+CA+EGLV:160:86+EVERGREEN MARINE CORP (M) SDN BHD")

    # NAD+FW+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    content_list.append("NAD+FW+++" + data["business_name"] + "+" + data["address1"] + "+ "
                        + data["address2"] + "+" + data["town"] + "+" + data["postcode"] + "+" + data["country"])

    # CTA+IC+:THOMAS LI'
    content_list.append("CTA+IC+:" + data["contact"])

    # COM+?+00861581388333:TE'
    content_list.append("COM+?+" + data["telephone"] + ":TE")

    # COM+mark@dcglogistics.com:EM'
    content_list.append("COM+" + data["email"] + ":EM")
    i = 0
    for detail_data in data['GID']:
        i = i + 1
        # GID+1+916:5L:67:6:Textile Bags'
        content_list.append("GID+" + str(detail_data["quantity"]))

        # FTX+AAA+++LINEN FABRIC CHAIR'
        content_list.append("FTX+AAA+++" + detail_data["product_description"])

        # MEA+AAE+G+KGM:5540'
        if detail_data["weight_disc"] == 1:
            if detail_data["quantity"] <= 0:
                weight = detail_data["weight"] * 1
            else:
                weight = detail_data["weight"] * detail_data["quantity"]
        else:
            weight = detail_data["weight"]

        content_list.append("MEA+AAE+G+" + detail_data["weight_unit"] + ":" + str(weight).strip())

        if detail_data["volume"] > 0:
            # MEA+AAE+AAW+MTQ:68'
            content_list.append("MEA+AAE+AAW+" + detail_data["volume_unit"] + ":" + str(detail_data["volume"]))

        # SGP+01+916'
        content_list.append("SGP+" + "{:0>2d}".format(i) + "+" + str(detail_data["quantity"]))

        # if len(detail_data["remark"]) > 0:
        #     # FTX+AAI+++TEST ONLY'
        #     content_list.append("FTX+AAI+++" + detail_data["remark"])

    # END FOR
    i = 0
    for detail_data in data['GID']:
        i = i + 1
        # EQD+CN+01:230:ZZZ+4500:102:5+2+5'
        content_list.append("EQD+CN+" + "{:0>2d}".format(i) + ":230:ZZZ+" + detail_data["container_code"]
                            + ":102:5+2+5")

        # EQN+1:2'
        content_list.append("EQN+" + str(detail_data["container_qty"]) + ":2")
    # END FOR

    # TMD+3'
    content_list.append("TMD+" + data["transport_service_type"])

    # UNT+37+DCG2001'
    line = str(len(content_list)).strip()
    content_list.append("UNT+" + line + "+" + data["booking_id"])

    # UNZ+1+DCG2001'
    content_list.append("UNZ+1+" + data["booking_id"])

    return content_list


def save_to_file(filename, content_list):
    # 写之前，先检验文件是否存在，存在就删掉
    ftp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), LOCAL_UPLOAD_DIR)
    filename = os.path.join(ftp_path, filename)

    if os.path.exists(filename):
        os.remove(filename)

    # 以写的方式打开文件，如果文件不存在，就会自动创建
    with open(filename, 'w', encoding='utf-8') as f:
        for each_line in content_list:
            f.writelines(each_line + "'")
            f.write('\n')
    print("Finished file:" + filename)

    return
