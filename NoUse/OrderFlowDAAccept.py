#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import Final
import sys
sys.path.append("./")
import unittest
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
import configparser
from Method.CommonMethod import*
from Method.OrderMethod import*
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
        self.config.read('./Config/condition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Order Flow DA Accept"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)

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

    def test_OrderFlow4Hours(self):
        totalstatus = True
        resultList = []
        #Step 1 : Get Accesskey
        Accesskey = GetDeliveryAgentAccessKey(self.setting_config,"DA_Setting_Receive")
        resultList.extend((totalstatus, Accesskey))
        #Step 2 : Scan Order By Service Type and Check exist or not
        OrderID = LoadOrderDictByServiceType("4Hours")
        response, status = CheckTheOrderInPoolOrNot(OrderID)
        resultList.extend((status, response))
        #Step 3 : DA Accept
        status_code, tripid, status = DeliveryAgentReceive(OrderID,Accesskey,totalstatus)
        resultList.extend((status, response))
        #Step 4 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((status, response))
        #Step 5 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((status, response))
        response, status = DropOff(tripid)
        resultList.extend((status, response))
        #Step 6 : Payrolls
        status = 3
        response = ""
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"4Hours",resultList,self.runId)

    def test_OrderFlowExchange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Get Accesskey
        Accesskey = GetDeliveryAgentAccessKey(self.setting_config,"DA_Setting_Receive")
        resultList.extend((totalstatus, Accesskey))
        #Step 2 : Scan Order By Service Type and Check exist or not
        OrderID = LoadOrderDictByServiceType("Exchange")
        response, status = CheckTheOrderInPoolOrNot(OrderID)
        resultList.extend((status, response))
        #Step 3 : DA Accept
        status_code, tripid, status = DeliveryAgentReceive(OrderID,Accesskey,totalstatus)
        resultList.extend((status, response))
        #Step 4 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((status, response))
        #Step 5 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((status, response))
        response, status = DropOff(tripid)
        resultList.extend((status, response))
        #Step 6 : Payrolls
        status = 3
        response = ""
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Exchange",resultList,self.runId)

    def test_OrderFlowExpress(self):
        totalstatus = True
        resultList = []
        #Step 1 : Get Accesskey
        Accesskey = GetDeliveryAgentAccessKey(self.setting_config,"DA_Setting_Receive")
        resultList.extend((totalstatus, Accesskey))
        #Step 2 : Scan Order By Service Type and Check exist or not
        OrderID = LoadOrderDictByServiceType("Express")
        response, status = CheckTheOrderInPoolOrNot(OrderID)
        resultList.extend((status, response))
        #Step 3 : DA Accept
        status_code, tripid, status = DeliveryAgentReceive(OrderID,Accesskey,totalstatus)
        resultList.extend((status, response))
        #Step 4 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((status, response))
        #Step 5 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((status, response))
        response, status = DropOff(tripid)
        resultList.extend((status, response))
        #Step 6 : Payrolls
        status = 3
        response = ""
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Express",resultList,self.runId)

    def test_OrderFlowNextDay(self):
        totalstatus = True
        resultList = []
        #Step 1 : Get Accesskey
        Accesskey = GetDeliveryAgentAccessKey(self.setting_config,"DA_Setting_Receive")
        resultList.extend((totalstatus, Accesskey))
        #Step 2 : Scan Order By Service Type and Check exist or not
        OrderID = LoadOrderDictByServiceType("NextDay")
        response, status = CheckTheOrderInPoolOrNot(OrderID)
        resultList.extend((status, response))
        #Step 3 : DA Accept
        status_code, tripid, status = DeliveryAgentReceive(OrderID,Accesskey,totalstatus)
        resultList.extend((status, response))
        #Step 4 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((status, response))
        #Step 5 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((status, response))
        response, status = DropOff(tripid)
        resultList.extend((status, response))
        #Step 6 : Payrolls
        status = 3
        response = ""
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"NextDay",resultList,self.runId)

    def test_OrderFlowSameDay(self):
        totalstatus = True
        resultList = []
        #Step 1 : Get Accesskey
        Accesskey = GetDeliveryAgentAccessKey(self.setting_config,"DA_Setting_Receive")
        resultList.extend((totalstatus, Accesskey))
        #Step 2 : Scan Order By Service Type and Check exist or not
        OrderID = LoadOrderDictByServiceType("SameDay")
        response, status = CheckTheOrderInPoolOrNot(OrderID)
        resultList.extend((status, response))
        #Step 3 : DA Accept
        status_code, tripid, status = DeliveryAgentReceive(OrderID,Accesskey,totalstatus)
        resultList.extend((status, response))
        #Step 4 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((status, response))
        #Step 5 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((status, response))
        response, status = DropOff(tripid)
        resultList.extend((status, response))
        #Step 6 : Payrolls
        status = 3
        response = ""
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"SameDay",resultList,self.runId)

    def test_OrderFlowCollection(self):
        totalstatus = True
        resultList = []
        #Step 1 : Get Accesskey
        Accesskey = GetDeliveryAgentAccessKey(self.setting_config,"DA_Setting_Receive")
        resultList.extend((totalstatus, Accesskey))
        #Step 2 : Scan Order By Service Type and Check exist or not
        OrderID = LoadOrderDictByServiceType("Collection")
        response, status = CheckTheOrderInPoolOrNot(OrderID)
        resultList.extend((status, response))
        #Step 3 : DA Accept
        status_code, tripid, status = DeliveryAgentReceive(OrderID,Accesskey,totalstatus)
        resultList.extend((status, response))
        #Step 4 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((status, response))
        #Step 5 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((status, response))
        response, status = DropOff(tripid)
        resultList.extend((status, response))
        #Step 6 : Payrolls
        status = 3
        response = ""
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Collection",resultList,self.runId)

if __name__ == '__main__':
    unittest.main()  
