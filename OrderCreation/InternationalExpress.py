#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import unittest
import Library.GlobalAdapter as GlobalAdapter
import Method.CommonMethod as CommonMethod
import Library.TestCaseHelper as TestCaseHelper
from Method.OrderMethod import *
from typing import Final
from Core.ApiQuery import*
from datetime import date
from Library.DBConnector import*
from Library.Config import dumplogger
from Utility.testrail import*
from Library.GlobalAdapter import *
import configparser
from Method.CommonMethod import *

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class InternationalExpress(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/InternationalExpress.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "International Express"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_SingleInternationalExpressSG(self):
        totalstatus = True
        resultList = []
        mode="lite"
        region = "SG"
        try:
            #Step 1 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))
            #Step 3 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))
            #Step 4 : Create an order
            status_code, OrderList, status = InternationalHKtoOther(self.config,region,mode,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderList))
            #Step 5 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            #Step 6 : Enroute
            response, status  = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "7771", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_MultiParcelInternationalExpressSG(self):
        totalstatus = True
        resultList = []
        mode="lite"
        region = "SG"
        try:
            # Step 1 : Create an order
            status_code, statusList, status = InternationalHKtoOther(self.config,region,mode,totalstatus,Multi=True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 2 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 3 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 4 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 5 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 6 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 7 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 8 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12126", resultList, self.test_case_time_start)

'''

    def test_International_TW(self):
        totalstatus = True
        resultList = []
        mode="lite"
        region = "TW"
        #Step 1 : Get_auth_portal
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
        #Step 2 : Get_auth_admin
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
        #Step 3 : Get_auth
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
        #Step 4 : Create an order
        status_code, OrderList, status = InternationalHKtoOther(self.config,region,mode,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderList))
        #Step 5 : Assign to DA
        da_id = GetDAId(self.setting_config, "DA_Setting")
        status_code, TripID, status = AssignToDeliveryAgent(OrderList[0],da_id,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
        #Step 6 : Enroute
        status_code, response, status = enroute(TripID, OrderList[0], totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Step 7 : Dropoff Process
        status_code, response, status = dropoff_process(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Step 8 : Dropoff
        status_code, response, status = dropoff(TripID, OrderList[0], totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"International_TW",resultList,self.runId)

    def test_International_MY(self):
        totalstatus = True
        resultList = []
        mode="lite"
        region = "MY"
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 3 : Get_auth
        response = GetDAAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 4 : Create an order
        status_code, OrderID, status = New_create_order_international(self.config,region,mode,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderID))
        #Step 5 : Check Order in Order List
        status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, filterstatus))
        #Step 6 : Assign to DA
        da_id = GetDAId(self.setting_config, "DA_Setting")
        status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
        #Step 7 : Enroute
        status_code, response, status = enroute(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Step 8 : Dropoff Process
        status_code, response, status = dropoff_process(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        status_code, response, status = dropoff(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"International_MY",resultList,self.runId)
    
    def test_International_JP(self):
        totalstatus = True
        resultList = []
        mode="lite"
        region = "JP"
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 3 : Get_auth
        response = GetDAAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 4 : Create an order
        status_code, OrderID, status = New_create_order_international(self.config,region,mode,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderID))
        #Step 5 : Check Order in Order List
        status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, filterstatus))
        #Step 6 : Assign to DA
        da_id = GetDAId(self.setting_config, "DA_Setting")
        status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
        #Step 7 : Enroute
        status_code, response, status = enroute(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Step 8 : Dropoff Process
        status_code, response, status = dropoff_process(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        status_code, response, status = dropoff(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"International_JP",resultList,self.runId)
    
    def test_International_CN(self):
        totalstatus = True
        resultList = []
        mode="lite"
        region = "CN"
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 3 : Get_auth
        response = GetDAAuth(self.setting_config)
        resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))
        #Step 4 : Create an order
        status_code, OrderID, status = New_create_order_international(self.config,region,mode,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderID))
        #Step 5 : Check Order in Order List
        status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, filterstatus))
        #Step 6 : Assign to DA
        da_id = GetDAId(self.setting_config, "DA_Setting")
        status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
        #Step 7 : Enroute
        status_code, response, status = enroute(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Step 8 : Dropoff Process
        status_code, response, status = dropoff_process(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        status_code, response, status = dropoff(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"International_CN",resultList,self.runId)
'''
if __name__ == '__main__':
    unittest.main()  