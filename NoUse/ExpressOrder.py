#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
from typing import Final
import unittest
import Method.CommonMethod as CommonMethod
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
import configparser
from Library.GlobalAdapter import *

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class Express_Order(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/InternationalExpress.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Express Orders"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    def CheckTotalStatus(self,resultList):
        for index in resultList:
            if index == False:
                return 5
        return 1   
    def TranslateForStatus(self,resultList):
        FinalResult = []
        for index in resultList:
            if index == True:
                FinalResult.append(1)
            elif index == False:
                FinalResult.append(5)
            else:
                FinalResult.append(index)
        return FinalResult

    def test_ExpressSmall(self):
        totalstatus = True
        resultList = []
        mode="lite"

        try:
            #Step 1 : Get_auth_portal
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
            #Step 2 : Get_auth_admin
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
            #Step 3 : Get_auth
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
            #Step 4 : Create an order
            status_code, OrderList, status = ExpressSingleOrder(self.config,"small",mode,totalstatus)
            resultList.extend((status, OrderList))
            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderList[1],totalstatus)
            resultList.extend((status, filterstatus))
            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderList[0],da_id)
            resultList.extend((status, api_response))
            #Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))
            #Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((status, response))
            response, status = DropOff(tripid)
            resultList.extend((status, response))
        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"ExpressSmall",resultList,self.runId)

    def test_ExpressMedium(self):
        totalstatus = True
        resultList = []
        mode="lite"
        try:
            #Step 1 : Get_auth_portal
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
            #Step 2 : Get_auth_admin
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
            #Step 3 : Get_auth
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
            #Step 4 : Create an order
            status_code, OrderList, status = ExpressSingleOrder(self.config,"medium",mode,totalstatus)
            resultList.extend((status, OrderList))
            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderList[1],totalstatus)
            resultList.extend((status, filterstatus))
            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderList[0],da_id)
            resultList.extend((status, api_response))
            #Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))
            #Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((status, response))
            response, status = DropOff(tripid)
            resultList.extend((status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"ExpressMedium",resultList,self.runId)
    
    def test_ExpressLarge(self):
        totalstatus = True
        resultList = []
        mode="lite"

        try:
            #Step 1 : Get_auth_portal
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
            #Step 2 : Get_auth_admin
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
            #Step 3 : Get_auth
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
            #Step 4 : Create an order
            status_code, OrderList, status = ExpressSingleOrder(self.config,"large",mode,totalstatus)
            resultList.extend((status, OrderList))
            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderList[1],totalstatus)
            resultList.extend((status, filterstatus))
            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderList[0],da_id)
            resultList.extend((status, api_response))
            #Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))
            #Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((status, response))
            response, status = DropOff(tripid)
            resultList.extend((status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"ExpressLarge",resultList,self.runId)

    def test_ExpressMultiple(self):
        totalstatus = True
        resultList = []

        try:
            #Step 1 : Get_auth_portal
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))

            #Step 2 : Get_auth_admin
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))

            #Step 3 : Get_auth
            resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))

            #Step 4 : Create an order
            status_code, OrderID, status = OrderAPI.CreateExpressOrder(self.config, "Multiple", "Multiple")
            resultList.extend((status, OrderID))

            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID,totalstatus)
            resultList.extend((status, filterstatus))

            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderID,da_id)
            resultList.extend((status, api_response))

            #Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))

            #Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((status, response))
            response, status = DropOff(tripid)
            resultList.extend((status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"ExpressMultiple",resultList,self.runId)


if __name__ == '__main__':
    unittest.main()  