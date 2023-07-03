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
import random
import string

from psycopg2 import OperationalError
from datetime import datetime, timedelta
from Library.DBConnector import connect_postgresql, execute_postgresql_fetchone
from Library.Config import dumplogger
from Utility.testrail import *
from datetime import date, datetime, timedelta

def CheckTotalStatus(resultList):
    '''
        The ID of the test status. The default system statuses have the following IDs:
            1: Passed
            2: Blocked, retest
            3: Untested (not allowed when adding a new result)
            5: Failed
    '''
    try:
        for index in resultList:
            if index == False:
                return 5
            elif str(index).lower() in ["blocked","retest"]:
                return 2
            elif str(index).lower() == "untested":
                return 3
        return 1
    except Exception as err:
        dumplogger.exception(err)

def TranslateForStatus(resultList):
    '''
        The ID of the test status. The default system statuses have the following IDs:
            1: Passed
            2: Blocked
            3: Untested (not allowed when adding a new result)
            4: Retest
            5: Failed
    '''
    FinalResult = []
    try:
        for index in resultList:
            if index == True:
                FinalResult.append(1)
            elif index == False:
                FinalResult.append(5)
            elif str(index).lower() == "blocked":
                FinalResult.append(2)
            elif str(index).lower() == "untested":
                FinalResult.append(3)
            elif str(index).lower() == "retest":
                FinalResult.append(3)
            else:
                FinalResult.append(index)
        return FinalResult
    except Exception as err:
        dumplogger.exception(err)

def GetDeliveryAgentAccessKey(setting_config, da_info):
    ''' GetAccessKeyOfDA : Get da access key from database
            Input argu:
                setting_config - which env setting you use this time.
                condition_name - which condition name from setting_config, you want to use
            Return code:
                access_key - token key format [email:session] and base64 encode
    '''

    # login da first
    r = requests.post(setting_config['Gateway_Url']['url'] + "v2/agent/login", data={"email":setting_config[da_info]['email'], "password":setting_config[da_info]['password']})

    if r.status_code == 201:
        try:
            # Conneted and SetUp Database
            connection = connect_postgresql()

            # Get DA id by api
            da_id = ApiQuery.GetDAId(setting_config, da_info)

            if da_id:
                # Use delivery_agent_id from setting_config
                command = """select dat.access_key from uat.agent."DeliveryAgentAccessTokens" dat where dat.delivery_agent_id = '%s' and dat.access_key notnull and dat.access_key <> ''""" % str(da_id)
                response = execute_postgresql_fetchone(connection, command)
            else:
                message = "Get DA ID Fail"
        except OperationalError:
            message = "Connect to SQL server failed, please check the root cause."
            dumplogger.exception(message)

        # token string base64 encode
        token_string = "%s:" % setting_config[da_info]['email'] + response[0]
        token_string_bytes = token_string.encode("UTF-8")
        key_byte = base64.b64encode(token_string_bytes)
        access_key = key_byte.decode("UTF-8")
    else:
        message = "Connect to login api failed, please check the root cause."
        dumplogger.error(message)

    return access_key

def GetOrderData(order_id):
    ''' GetOrderData : Get create time from database by order_id
            Input argu:
                order_id - which order you want to check this time
            Return code:
                order_dict - token key format [email:session] and base64 encode
    '''
    order_dict = {}
    try:
        # Conneted and SetUp Database
        connection = connect_postgresql()
        # Use delivery_agent_id from setting_config
        command = """SELECT ord.order_number, ord.status, ord.created_at FROM "order".orders ord where ord.order_number = '%s'""" % str(order_id)
        response = execute_postgresql_fetchone(connection, command)
    except OperationalError:
        message = "Connect to SQL server failed, please check the root cause."
        dumplogger.exception(message)

    # token string base64 encode
    for row in response:
        order_dict = {row[0]:{"status":row[1], "created_time":datetime.strftime(row[2], '%Y-%m-%d %H:%M:%S')}}

    return order_dict

def GetJobSettingTime():
    release_time = datetime.utcnow().isoformat() + 'Z'
    start_time = (datetime.utcnow() + timedelta(minutes=1)).isoformat()[:-4] + 'Z'
    end_time = (datetime.utcnow() + timedelta(hours=4)).isoformat() + 'Z'
    cutoff_time = (datetime.utcnow() + timedelta(hours=4)).isoformat() + 'Z'
    time_dict = {"release_time":release_time, "start_time":start_time, "end_time":end_time, "cutoff_time":cutoff_time}
    return time_dict

def GetJsonData(file_name, dict_key):
    try:
        # root_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
        # windows_dir = root_path + '\\Config\\'
        # linux_dir = root_path + '/Config/'
        # log_dir = windows_dir if os.name == 'nt' else linux_dir
        # with open(log_dir + file_name + ".json", 'r') as file:
        with open(file_name + ".json", 'r') as file:
            data = json.load(file)
        return data[dict_key]
    except Exception as err:
        dumplogger.exception(err)

def CompairTwoDict(source_dict, target_dict):

    try:
        if list(dictdiffer.diff(target_dict, source_dict)):
            return list(dictdiffer.diff(target_dict, source_dict))
        else:
            return True
    except Exception as err:
        dumplogger.exception(err)

def DeInitialAPIVar():
    ''' DeInitialHttpAPI : API deinitial for HTTP request
    '''
    ##Restore global adapter to avoid error for next case
    GlobalAdapter.AuthVar.MerchantPortalAuth = ""
    GlobalAdapter.AuthVar.AdminAuth = ""
    GlobalAdapter.AuthVar.DAAuth = ""
    GlobalAdapter.AuthVar.ShopAuth = ""

def CleanTrips(da_id):
    '''
        1. Status : ACCEPTED, ENROUTE
    '''
    try:
        AcceptedList = ApiQuery.TripsSolution.CheckAdminTripsList(da_id,"ACCEPTED")
        for index in range(len(AcceptedList)):
            ApiQuery.TripsSolution.ClickAllTripsToEnroute(da_id,AcceptedList[index])

        EnrouteList = ApiQuery.TripsSolution.CheckAdminTripsList(da_id,"ENROUTE")
        for index in range(len(EnrouteList)):
            ApiQuery.TripsSolution.ClickAllTripsToDropoff(da_id,EnrouteList[index])
    except Exception as err:
        dumplogger.exception(err)

def ResponseHandler(status_code, return_message):
    '''
        ResponseHandler : To make response format
        input:
            status_code, return_message
        return :
         response format like {status code : 200, return message : Drop off order success}
    '''
    return {"status_code ": status_code, "return_message ": return_message}

def GetTestCaseSpentTime(start_time, end_time):
    '''
        GetTestCaseSpentTime : To make response format
        input:
            start_time, start_time
        return :
         response time flot
    '''

    dt = str((end_time - start_time) * 1.00)
    test_case_spent_time = dt[:(dt.find(".") + 4)]

    return "%s s" % test_case_spent_time

def UpdateResultToTestrail(run_id, test_ids_list, test_case_id, result_list, test_case_time_start):
    '''
        UpdateResultToTestrail : update result to testrail
            input:
                run_id - Test case build run id
                test_ids_list - Test case id list from testrail
                test_case_id -  Test case id now you running
                result_list - Test case result
                test_case_time_start - Test case start time
            return :
                response time flot
    '''

    try:
        test_case_time_end = time.time()
        dt = str((test_case_time_end - test_case_time_start) * 1.00)
        test_case_spent_time = str(dt[:(dt.find(".") + 4)]) + " s"

        dumplogger.info("Prepare Get Test Case Info from Test Rails")
        test_id, case_step_counts = GetTestCaseInfoWithCaseID(test_ids_list, test_case_id)
        result_list = CheckResultStepAmount(result_list, case_step_counts)

        total_status = CheckTotalStatus(result_list)
        final_result_list = TranslateForStatus(result_list)

        dumplogger.info("Prepare add results to test rails , test case id: %s" % test_case_id)
        AddResultByStep(total_status, test_case_spent_time, run_id, test_id, case_step_counts, final_result_list)
    except Exception as err:
        dumplogger.exception("Update result to testrail fail, please check logger.")
        dumplogger.exception(err)

class Auth:

    def CheckAuthSuccessfully(auth):
        message = ""
        have_auth = False
        if auth and ("Basic" in auth):
            have_auth = True
            message = "Get auth successfully"
        else:
            have_auth = False
            message = "Can't get auth, please check Api logger"

        return have_auth, message

def CheckHowManyDaysIsWorkday(dayvalue=1):
    while True:
        tomorrow = date.today()+ timedelta(dayvalue)
        checkvalue = numpy.is_busday(tomorrow)
        if checkvalue == True:
            return dayvalue
        else:
            dayvalue+=1

def WriteDataInConfigFlie(config,configpath,conditionlist,conditionpath,Value):
    config[conditionlist][conditionpath]=Value
    with open(configpath, 'w') as configfile:
        config.write(configfile)

def ReplaceTwoTupleToDict(Key,Value):
    resultDictionary = {Key[i] : Value[i] for i, _ in enumerate(Value)}
    return resultDictionary

def ReadConfigAndPutInDict(Config,condition,Key,addcondition): 
    InputDatalist = []
    conditionchoose = "condition_" + condition
    for value in Key:
        try:
            InputDatalist.append(Config[conditionchoose][value])
        except:
            pass
    FinalList = addcondition + InputDatalist
    resultDictionary = ReplaceTwoTupleToDict(Key,tuple(FinalList))
    return resultDictionary

def DecodeDecimalToStringAndReturnTuple(Value):
    ReturnList = []
    for i in Value:
        if str(i).isdecimal() == True:
            if i == Value[-1]:
                # for entityid, userid and servicetime are same type(Decimal), but entity and user need to be string
                ReturnList.append(i)
            else:
                ReturnList.append(str(i))
        else:
            if isinstance(i,(bool,int)) == True:
                ReturnList.append(i)
            else:
                ReturnList.append(str(i))

    return tuple(ReturnList)

def GenClientReferenceNumber():
    '''
        GenClientReferenceNumber :
            generation with upper case letters and digits to provide identification data
            return :
                response client reference number
    '''
    client_reference_number = 'AUTOQA' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    return client_reference_number


def GetParcelRandomWLH():
    '''
        Refer to https://hk.pickupp.io/en/faq SPEC
    '''
    total = 149
    weight = random.randrange(1, 20)
    width = random.randrange(1, total - 2)
    lengthtmp = total - width
    length = random.randrange(1, lengthtmp - 1)
    heighttmp = lengthtmp - length
    height = random.randrange(1, heighttmp)
    return width, length, height, weight
