#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   files.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li
写EDI的文件
@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
27/11/2020 09:33   lzb       1.0         None
"""
import os
import datetime
from const import *


def handle_edi_file(data):
    """
    将数据，写入到EDI FILE 中
    :param data: EDI FILE 的数据
    :return:
    """
    filename = data["booking_id"] + ".txt"

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
    content_list.append("com+" + data["email"] + ":EM")

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

    # DTM+196:20201210:102'
    content_list.append("DTM+196:" + data["scheduled_date"] + ":102")

    # LOC+7+GBFXT:181:6:Felixstowe'
    content_list.append("LOC+7:" + data["delivery_country"] + data["delivery_port"] + ":181:6:Felixstowe")

    # LOC+9+TWKHH:139:6:Kaohsiung+TW:162:5:Taiwan'
    content_list.append("LOC+9:" + data["scheduled_date"] + ":102")

    # LOC+11+GBFXT:139:6:Felixstowe+GB:162:5:United Kingdom'
    # NAD+ZZZ+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    # CTA+IC+:THOMAS LI'
    # NAD+CZ+++BOWER GREEN LIMITED '
    # NAD+CN+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    # NAD+NI+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    # CTA+IC+:THOMAS'
    # COM+?+004407421900978:TE'
    # COM+mark@dcglogistics.com:EM'
    # NAD+CA+EGLV:160:86+EVERGREEN MARINE CORP (M) SDN BHD'
    # NAD+FW+++DCG LOGISTICS LTD+7 Floor North Tower+Hubei Building Binhe road+ShenZhen+CN'
    # CTA+ICTHOMAS LI'
    # COM+?+00861581388333:TE'
    # COM+mark@dcglogistics.com:EM'
    # GID+1+916:5L:67:6:Textile Bags'
    # FTX+AAA+++LINEN FABRIC CHAIR'
    # MEA+AAE+G+KGM:5540'
    # MEA+AAE+AAW+MTQ:68'
    # SGP+01+916'
    # EQD+CN+01:230:ZZZ+4500:102:5+2+5'
    # EQN+1:2'
    # TMD+3'
    # UNT+37+DCG2001'
    # UNZ+1+DCG2001'

    # 写文件
    write_to_file(filename, content_list)

    return


def write_to_file(filename, content_list):
    # 写之前，先检验文件是否存在，存在就删掉
    ftp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), FTP_UPLOAD_DIR)
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
