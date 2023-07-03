#!/usr/bin/python
# -*- coding: UTF-8 -*-
from distutils.command.config import config
import sys
sys.path.append("./")
from Method.OrderMethod import *
from typing import Final
import unittest
import configparser
import Method.CommonMethod as CommonMethod
import Library.TestCaseHelper as TestCaseHelper
from Core.ShopifyAPIQuery import *
from Library.GlobalAdapter import *
from Method.CommonMethod import *
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
from Library.Config import dumplogger
from random import randint

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class OrderAttributesAPIFlow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/condition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "OrderAttributes API Flow"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.AuthVar.ShopAuth = GetShopPortalAuth(self.setting_config, 'ShopControl_Setting_%s' % GlobalAdapter.FrameworkVar.Environment)
        LinkShopify(self.setting_config)
        self.test_case_time_start = time.time()
        #Updata merchant setting to Turn on all Special setting
        merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
        merchants_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting", "TurnOnAllSpecialSetting")
        AdminMerchantAPI.UpdateMerchantSetting(self.setting_config, merchant_id, merchants_setting)
        self.PromotionStatusCode, self.PromotionCode,self.PromotionStatus, self.PromotionId = PromotionKeyCreate(1,self.config['PromotionTypeValue']['name'],self.config['PromotionTypeValue']['value'],self.config['PromotionTypeValue']['category'])

    @classmethod
    def tearDownClass(self):
        UnlinkShopify(self.setting_config)
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
        merchants_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting", "TurnOffAllSpecialSetting")
        AdminMerchantAPI.UpdateMerchantSetting(self.setting_config, merchant_id, merchants_setting)
        removePromotionKey(self.PromotionId)
        CommonMethod.DeInitialAPIVar()

    def test_OrderAttributes4Hours(self):
        totalstatus = True
        resultList = []
        try:
            #
            # Step 1 : Create an Order and Get OrderID 
            status_code, statusList, status = CreateOrder(self.config,'4Hours',totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))
  
        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13183", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderAttributesExchange(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an Order and Get Order Number
            status_code, statusList, status = CreateOrder(self.config,'Exchange',totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13185", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderAttributesExpress(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an Order and Get Order Number
            status_code, statusList, status = CreateOrder(self.config,'Express',totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))
           
        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13184", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderAttributesNextDay(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an Order and Get Order Number
            status_code, statusList, status = CreateOrder(self.config,'NextDay',totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13188", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderAttributesSameDay(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an Order and Get Order Number
            status_code, statusList, status = CreateOrder(self.config,'SameDay',totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13187", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderAttributesCollection(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an Order and Get Order Number
            status_code, statusList, status = CreateOrder(self.config,'Collection',totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13186", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderAttributesFirstLeg(self):
        totalstatus = True
        resultList = []
        try:
            # Check How Many days is Workday
            Getdays = CommonMethod.CheckHowManyDaysIsWorkday()
            # Step 1 : Create an Order and Get Order Number
            status_code, statusList, status = ScheduleBulkCollection(self.config,'FirstLeg',totalstatus,Getdays)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13189", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderAttributesLastLeg(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an Order and Get Order Number
            status_code, statusList, status = AdminCreateOrder(self.config,'LastLeg',totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13190", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_MultiParcelInternationalExpressSG(self):
        totalstatus = True
        resultList = []
        mode="lite"
        region = "SG"
        try:
            # Step 1 : Create an order
            status_code, statusList, status = InternationalHKtoOther(self.config,region,mode,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13208", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_ShopifyOrderCreation(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Login Shopify and Create an Order and Went to MP > Shopify > Send with Pickupp > Bulk Create Sales Requests
            StatusCode , OrderStatusList, status = ShopifyCreateOrder(totalstatus)
            StatusCode , OrderID , status = BulkCreateOrder(self.config, float(OrderStatusList[2])/float(OrderStatusList[3]) , OrderStatusList[0], totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderID))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(OrderID,Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),OrderID)
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),OrderID)
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),OrderID)
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),OrderID)
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),OrderID)
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13209", resultList, self.test_case_time_start)
    
    @TestCaseHelper.TestTimed
    def test_ShopOrderCreateion(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create Shop order and login to Shop account to create customer's order 
            status_code, statusList, status = PurchaseOrder(self.config,"creditcard","",1,totalstatus)
            status_code, PurchaseList, status = PortalShopOrder(self.config,"PortalShopOrder",statusList,4,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, PurchaseList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatusByShopAuth(PurchaseList[3],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),PurchaseList[3])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),PurchaseList[3])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),PurchaseList[3])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),PurchaseList[3])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),PurchaseList[3])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))

        except Exception as err:
            dumplogger.exception(err)

        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13412", resultList, self.test_case_time_start)

    def test_OrderAttributesPromotion(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an Order and Get OrderID 
            status_code, statusList, status = CreateOrder(self.config,'4Hours',totalstatus,promocode=self.PromotionCode[0],promoid=self.PromotionId)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Mapping Input Data and Database Data - Backbone Waypoint Table - PICK
            response = GetBackBoneOrderStatus(statusList[0],Datamapping=True)
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            WaypointPickcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'PICK'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointPickresponse = execute_postgresql_fetchone(connection,WaypointPickcommand)
            WaypointPickResult = WaypointPickCheckFromAPIResp(response)
            WaypointPickResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointPickresponse)
            CompairStatus = CompairTwoDict(WaypointPickResult,WaypointPickResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,'''Except result: %s
                                                                     Actual result: %s'''%(WaypointPickResult,WaypointPickResp)))
            # Step 3 : Mapping Input Data and Database Data - Backbone Waypoint Table - DROP
            WaypointDropcommand = """select %s from "backbone"."Waypoints" where order_id = '%s' and type = 'DROP'""" % (",".join(GlobalAdapter.CommonVar.WaypointKey),statusList[0])
            WaypointDropresponse = execute_postgresql_fetchone(connection,WaypointDropcommand)
            WaypointDropResult = WaypointDROPCheckFromAPIResp(response)
            WaypointDropResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.WaypointKey,WaypointDropresponse)
            CompairStatus = CompairTwoDict(WaypointDropResult,WaypointDropResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(WaypointDropResult,WaypointDropResp)))
            # Step 4 : Mapping Input Data and Database Data - Backbone Orders Table
            Orderscommand = """select %s  from backbone."Orders" where id = '%s' """ % (",".join(GlobalAdapter.CommonVar.OrdersKey),statusList[0])
            Ordersresponse = execute_postgresql_fetchone(connection,Orderscommand)
            DecodeOrdersResponse = DecodeDecimalToStringAndReturnTuple(Ordersresponse)
            OrdersResult = OrdersCheckFromAPIResp(response)
            OrdersResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrdersKey,DecodeOrdersResponse)
            CompairStatus = CompairTwoDict(OrdersResult,OrdersResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrdersResult,OrdersResp)))
            # Step 5 : Mapping Input Data and Database Data - Backbone OrderProperties Table
            OrderPropertiescommand = """select %s  from backbone."OrderProperties" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.OrderPropertiesKey),statusList[0])
            OrderPropertiesresponse = execute_postgresql_fetchone(connection,OrderPropertiescommand)
            DecodeOrderPropertiesResponse = DecodeDecimalToStringAndReturnTuple(OrderPropertiesresponse)
            OrderPropertResult = OrderPropertiesCheckFromAPIResp(response)
            OrderPropertiesResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.OrderPropertiesKey,DecodeOrderPropertiesResponse)
            CompairStatus = CompairTwoDict(OrderPropertResult,OrderPropertiesResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(OrderPropertResult,OrderPropertiesResp)))
            # Step 6 : Mapping Input Data and Database Data - Backbone ReferenceNumber Table
            ReferenceNumbercommand = """select %s  from backbone."ReferenceNumbers" where order_id ='%s'""" % (",".join(GlobalAdapter.CommonVar.ReferenceNumberKey),statusList[0])
            ReferenceNumberresponse = execute_postgresql_fetchone(connection,ReferenceNumbercommand)
            ReferenceNumberResult= ReferenceNumberCheckFromAPIResp(response,"CLIENT_REFERENCE_NUMBER")
            ReferenceNumberResp = ReplaceTwoTupleToDict(GlobalAdapter.CommonVar.ReferenceNumberKey,ReferenceNumberresponse)
            CompairStatus = CompairTwoDict(ReferenceNumberResult,ReferenceNumberResp)
            if CompairStatus == True:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, '''Except result: %s
                                                                     Actual result: %s'''%(ReferenceNumberResult,ReferenceNumberResp)))
  
        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13482", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()  
