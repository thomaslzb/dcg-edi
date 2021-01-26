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


BOOKING_SQL = "SELECT  TOP 1 booking.booking_id, " \
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
             "shipper.postcode, " \
             "carrier.env_id " \
             "FROM booking, carrier, country_port, country, shipper " \
             "WHERE booking.status = ? " \
             "AND booking.carrier_id = carrier.id " \
             "AND booking.delivery_country = country_port.country_code " \
             "AND booking.delivery_port = country_port.port_code " \
             "AND booking.delivery_country = country.code " \
             "AND booking.shipper_code = shipper.code "

BOOKING_DETAIL_SQL = "SELECT booking_detail.product_description, " \
             "booking_detail.container_code, " \
             "booking_detail.container_qty, " \
             "booking_detail.weight, " \
             "booking_detail.weight_disc, " \
             "booking_detail.weight_unit, " \
             "booking_detail.quantity,  " \
             "booking_detail.volume, " \
             "booking_detail.volume_unit, " \
             "booking_detail.remark, " \
             "container.ISO_1995 " \
             "FROM booking_detail, container " \
             "WHERE booking_detail.booking_id = ? " \
             "AND booking_detail.container_code = container.ISO_1984"

UPDATE_BOOKING_STATUS_SQL = "UPDATE booking " \
                    "SET booking.status = ?, error = ? "  \
                    "WHERE booking.booking_id = ? "

SELECT_COUNTRY_SQL = "SELECT country FROM country WHERE country.code = ?"

SELECT_COUNTRY_PORT_SQL = "SELECT name FROM country_port  " \
                          "WHERE country_port.country_code = ? " \
                          "AND  country_port.port_code = ? "

SELECT_BOOKING_SQL = "SELECT  TOP 1 booking.status " \
                     "FROM booking " \
                     "WHERE booking.booking_id = ? " \

INSERT_BOOKING_RESULT = "INSERT INTO booking_result  " \
                            "(booking_id, carrier_booking_number,confirm_datetime, " \
                            "voyage_name, voyage_no, receipt_country, receipt_port, " \
                            "start_date, delivery_country, delivery_port, delivery_date, " \
                            "message_code) " \
                            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

INSERT_ROUTE_TIMETABLE = "INSERT INTO route_timetable " \
                         "(message_code, message_date, route_name, " \
                         "voyage_name, voyage_no, " \
                         "place_of_delivery, place_of_delivery_date, " \
                         "place_of_receipt, place_of_receipt_date, " \
                         "place_of_loading, place_of_loading_date," \
                         "place_of_discharge, place_of_discharge_date, carrier_company) " \
                         "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


