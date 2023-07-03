#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
sys.path.append("./")
import base64
import os
import requests
import json
import dictdiffer
import Library.GlobalAdapter as GlobalAdapter
import Core.ApiQuery as ApiQuery
import numpy
from psycopg2 import OperationalError
from datetime import datetime, timedelta
from Library.DBConnector import connect_postgresql, execute_postgresql_fetchall
from Library.Config import dumplogger
from Utility.testrail import *
from datetime import date, datetime, timedelta

def GetBackBoneOrderData(command):
    ''' GetBackBoneOrderData : Get order data from Backbone table
            Return code:
                order_dict - token key format {order_id:old_order_status:bb_order_status:bb_trip_status:bb_parcel_status}
    '''
    order_dict = {}
    try:
        # Conneted and SetUp Database
        connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
        response = execute_postgresql_fetchall(connection, command)
        dumplogger.info(response)
    except OperationalError:
        message = "Connect to SQL server failed, please check the root cause."
        dumplogger.exception(message)

    # token string base64 encode
    for row in response:
        order_dict.update({row[0]:{"order_id":row[0], "old_order_status":row[1], "bb_order_status":row[2], "bb_trip_status":row[3], "bb_parcel_status":row[4]}})

    return order_dict
