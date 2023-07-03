#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from typing import OrderedDict
import sys
sys.path.append("./")
import numpy as np
import os
from Core.ApiQuery import*
from Library.Config import dumplogger
from Method.CommonMethod import *
import json
def LoadOrderDictByServiceType(ServiceType):
    '''
        Call .npy file and using Service type to get OrderID
    '''
    filename= os.getcwd()+"./Config/OrderDict.npy"
    dumplogger.info(filename)
    OrderDictTemp = np.load(filename,allow_pickle=True)
    OrderDict = OrderDictTemp.item()
    return OrderDict[ServiceType]

def CheckTheOrderInPoolOrNot(OrderID):
    AllOrder = GetAdminPoolOrders()
    if OrderID in AllOrder:
        return "The Order In Pool", True
    else:
        return "The Order Not In Pool", False

def CompareWithValue(Insidestatus,comparestatus):
    if Insidestatus == comparestatus:
        return True
    elif Insidestatus in comparestatus:
        return True
    else:
        return False


def CheckOrderReleaseTime(order_response, order_id, check_status):
    ''' CheckOrderReleaseTime : Check order release time in Job
            Input argu:
                order_trips - order list in job
                order_id - which order id you add to job this time
                check_status - check status you want
            Return code:
                return order id and boolean
    '''
    try:
        order_trips = order_response['data']['trips']
        if order_trips:
            for raw in range(len(order_trips)):
                if order_trips[raw]['order']['order_number'] == order_id:
                    if order_trips[raw]['release_time']:
                        return order_trips[raw]['release_time'], check_status
                    elif check_status:
                        return order_id, check_status
                    else:
                        check_status = False
        else:
            check_status = False
    except KeyError as err:
        dumplogger.exception(err)
        check_status = False
    except Exception as err:
        dumplogger.exception(err)
        check_status = False

    return order_response, check_status


def GetAndCheckOrderFee(order_id, fee_price, fee_cofficient):
    check_result = ""
    result = False
    try:
        # #Get Order item declared value
        # order_detail = MerchantPortal.GetOrderDetail(order_number)
        # declared_value = order_detail['items'][0]['declared_value']
        #
        #Get system fee cofficient setting
        order_number = GetOrderNumber(order_id)
        query_fee_price, query_fee_cofficient = MerchantPortal.GetOrderFees(order_number)
        #
        # order_fee_price = math.ceil(round(float(declared_value) * float(query_fee_cofficient),3) * 10) / 10.0

        if query_fee_cofficient == fee_cofficient:
            check_result = "The fees are match up setting. Fee cofficient : %s and Fee price %s" % (str(query_fee_cofficient), str(fee_price))
            result = True
        else:
            check_result = "The fees are not match up setting. Setting Fee price :%s and fee cofficient : %s, but system return Fee price :%s, fee cofficient is : %s" % (str(fee_price), str(fee_cofficient),str(fee_price),str(query_fee_cofficient))
            result = False
    except Exception as err:
        dumplogger.exception(err)
        check_result = "Can't match up fees, please check api response data"

    return check_result, result


def GetAndCheckJobReturnMessage(api_response, status, error_message):
    check_result = ""
    try:
        if api_response['meta']['error_message'] == error_message:
            status = True
            check_result = api_response['meta']['error_message']
        else:
            status = False
            check_result = "Can't find target error message, target message : %s, api response : %s" % (error_message,api_response['meta']['error_message'])
    except Exception as err:
        dumplogger.exception(err)
        check_result = "Can't match error message, please check api response data"

    return check_result, status

def GetSublistValueInList(Subvalue,Checklist):
    try:
        for sublist in Checklist:
            if sublist[0] == Subvalue:
                return sublist, True
        return "Value not found!" , False
    except Exception as err:
        dumplogger.exception(err)

def WaypointPickCheckFromAPIResp(Resp):
    CheckList = []
    for value in GlobalAdapter.CommonVar.WaypointKey:
        CheckList.append(Resp['data']['order']['waypoints'][0][value])
    ResultDict = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,tuple(CheckList))
    return ResultDict

def WaypointDROPCheckFromAPIResp(Resp):
    CheckList = []
    for value in GlobalAdapter.CommonVar.WaypointKey:
        CheckList.append(Resp['data']['order']['waypoints'][1][value])
    ResultDict = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,tuple(CheckList))
    return ResultDict

def OrdersCheckFromAPIResp(Resp):
    CheckList = []
    for value in GlobalAdapter.CommonVar.OrdersKey:
        CheckList.append(Resp['data']['order'][value])
    ResultDict = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,tuple(CheckList))
    return ResultDict

def OrderPropertiesCheckFromAPIResp(Resp):
    CheckList = []
    for value in GlobalAdapter.CommonVar.OrderPropertiesKey:
        CheckList.append(Resp['data']['order']['property'][value])
    ResultDict = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,tuple(CheckList))
    return ResultDict

def ReferenceNumberCheckFromAPIResp(Resp,key):
    CheckList = []
    for index in range(len(Resp['data']['order']['reference_numbers'])):
        if Resp['data']['order']['reference_numbers'][index]["key"] == key:
            UsingIndex = index
    for value in GlobalAdapter.CommonVar.ReferenceNumberKey:
        CheckList.append(Resp['data']['order']['reference_numbers'][UsingIndex][value])
    ResultDict = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,tuple(CheckList))
    return ResultDict

def UnbundleGetAllOrderIDFromResp(Resp):
    OrderIDList = []
    for index in range(len(Resp['data']['bundle']['trips'])):
        OrderIDList.append(Resp['data']['bundle']['trips'][index]['order_id'])
    return OrderIDList
