#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   sql_const.py    
@Contact :   thomaslzb@hotmail.com
@License :   (C)Copyright 2020-2022, Zibin Li

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
25/11/2020 12:36   lzb       1.0         None
"""


BOOKING_SQL = "SELECT booking.booking_id, " \
             "booking.receipt_country, " \
             "booking.receipt_port, " \
             "booking.delivery_country, " \
             "booking.delivery_port," \
             "booking.transport_service_type, " \
             "booking.transport_service_mode, " \
             "booking.scheduled_date, " \
             "booking.voyage_name," \
             "booking.voyage_no, " \
             "booking.confirm_email, " \
             "booking.booking_contact, " \
             "carrier.contract_no " \
             "FROM booking, carrier " \
             "WHERE booking.status = 0 " \
             "AND booking.carrier_id = carrier.id " \
             "LIMIT 1"

BOOKING_DETAIL_SQL = "SELECT booking_detail.product_description, " \
             "booking_detail.container_code, " \
             "booking_detail.container_qty, " \
             "booking_detail.weight, " \
             "booking_detail.weight_disc, " \
             "booking_detail.weight_unit, " \
             "booking_detail.quantity,  " \
             "booking_detail.volume, " \
             "booking_detail.volume_unit, " \
             "booking_detail.remark " \
             "FROM booking_detail " \
             "WHERE booking_detail.booking_id = '%s' "

UPDATE_CANCEL_SQL = "UPDATE booking " \
                    "SET booking.status = '%d' "  \
                    "WHERE booking.booking_id = '%s' "

