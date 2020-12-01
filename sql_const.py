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
             "country.country, " \
             "booking.delivery_port," \
             "country_port.name," \
             "booking.transport_service_type, " \
             "booking.transport_service_mode, " \
             "booking.scheduled_date, " \
             "booking.voyage_name," \
             "booking.voyage_no, " \
             "booking.email, " \
             "booking.contact, " \
             "booking.telephone, " \
             "booking.fax, " \
             "booking.booking_date, " \
             "carrier.contract_no, " \
             "shipper.business_name, " \
             "shipper.address1, " \
             "shipper.address2, " \
             "shipper.town, " \
             "shipper.country, " \
             "shipper.postcode " \
             "FROM booking, carrier, country_port, country, shipper " \
             "WHERE booking.status = 0 " \
             "AND booking.carrier_id = carrier.id " \
             "AND booking.delivery_country = country_port.country_code " \
             "AND booking.delivery_port = country_port.port_code " \
             "AND booking.delivery_country = country.code " \
             "AND booking.shipper_code = shipper.code " \
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

UPDATE_BOOKING_STATUS_SQL = "UPDATE booking " \
                    "SET booking.status = '%d' " + ", error = '%s' "  \
                    "WHERE booking.booking_id = '%s' "

SELECT_COUNTRY_SQL = "SELECT country FROM country WHERE country.code = '%s'"

SELECT_COUNTRY_PORT_SQL = "SELECT name FROM country_port  " \
                          "WHERE country_port.country_code = '%s' " \
                          "AND  country_port.port_code = '%s' "

