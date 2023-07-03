#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import Final
import unittest
import sys
sys.path.append("./")
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

class Order_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/NewCreateOrderCondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "New Order Flow"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
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

    def test_NewCreateOrderInternationalLite(self):
        totalstatus = True
        resultList = []
        mode="lite"
        ParcelList = ["small","medium","large","manual"]
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        resultList.extend((bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 3 : Get_auth
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 4 : Create an order
        status_code, OrderNumber, status = New_CreateOrder_international(self.config,mode,totalstatus)
        resultList.extend((status, OrderNumber))
        #Step 5 : Check Order in Order List
        status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
        resultList.extend((status, filterstatus))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"International",resultList,self.runId)

    def test_NewCreateOrderExpressLite(self):
        totalstatus = True
        resultList = []
        mode="lite"
        ParcelList = ["small","medium","large","manual"]
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        resultList.extend((bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 3 : Get_auth
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        for Parcel in ParcelList:
            #Step 4 : Create an order
            status_code, OrderNumber, status = New_CreateOrder_express(self.config,Parcel,mode,totalstatus)
            resultList.extend((status, OrderNumber))
            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
            resultList.extend((status, filterstatus))

        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Express",resultList,self.runId)

    def test_NewCreateOrderStandardLite(self):
        totalstatus = True
        resultList = []
        mode="lite"
        ParcelList = ["small","medium","large","manual"]
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        resultList.extend((bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 3 : Get_auth
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        for Parcel in ParcelList:
            #Step 4 : Create an order
            status_code, OrderNumber, status = New_CreateOrder_standard(self.config,Parcel,mode,totalstatus)
            resultList.extend((status, OrderNumber))
            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
            resultList.extend((status, filterstatus))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Standard",resultList,self.runId)

    def test_NewCreateOrderInternationalExpert(self):
        totalstatus = True
        resultList = []
        mode="expert"
        ParcelList = ["small","medium","large","manual"]
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        resultList.extend((bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 3 : Get_auth
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 4 : Create an order
        status_code, OrderNumber, status = New_CreateOrder_international(self.config,mode,totalstatus)
        resultList.extend((status, OrderNumber))
        #Step 5 : Check Order in Order List
        status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
        resultList.extend((status, filterstatus))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"International",resultList,self.runId)

    def test_NewCreateOrderExpressExpert(self):
        totalstatus = True
        resultList = []
        mode="expert"
        ParcelList = ["small","medium","large","manual"]
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        resultList.extend((bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 3 : Get_auth
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        for Parcel in ParcelList:
            #Step 4 : Create an order
            status_code, OrderNumber, status = New_CreateOrder_express(self.config,Parcel,mode,totalstatus)
            resultList.extend((status, OrderNumber))
            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
            resultList.extend((status, filterstatus))

        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Express",resultList,self.runId)

    def test_NewCreateOrderStandardExpert(self):
        totalstatus = True
        mode="expert"
        resultList = []
        ParcelList = ["small","medium","large","manual"]
        #Step 1 : Get_auth_portal
        response = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        resultList.extend((bool(response), response))
        #Step 2 : Get_auth_admin
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        #Step 3 : Get_auth
        response = GetAdminAuth(self.setting_config, 'Admin_Setting')
        resultList.extend((bool(response), response))
        for Parcel in ParcelList:
            #Step 4 : Create an order
            status_code, OrderNumber, status = New_CreateOrder_standard(self.config,Parcel,mode,totalstatus)
            resultList.extend((status, OrderNumber))
            #Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderNumber,totalstatus)
            resultList.extend((status, filterstatus))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Standard",resultList,self.runId)

if __name__ == '__main__':
    unittest.main()  
