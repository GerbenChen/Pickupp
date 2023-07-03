#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from typing import Final
import sys
sys.path.append("./")
from Library.GlobalAdapter import *
import unittest
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from Method.CommonMethod import *
import configparser

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class Order_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/common_setting.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/TierErrorHandling.ini')
        self.TestSuiteName = "Tier Error Handling"
        GlobalAdapter.CommonVar.AdminUrl = self.config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.config)
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)

    def tearDown(self):
        special_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        special_setting["pay_on_success"] = self.setting_config['TierDefault']['pay_on_success'],
        special_setting["cash_on_delivery"] = self.setting_config['TierDefault']['cash_on_delivery'],
        special_setting["core"] = self.setting_config['TierDefault']['core'],
        Special_Settings(special_setting,self.config['Tier']['MerchantID'])

        capability_limitation = CommonMethod.GetJsonData("./Config/Tier_Setting", "Default")
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['TierDefault']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['TierDefault']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['TierDefault']['can_cod'],
        capability_limitation["core"] = self.setting_config['TierDefault']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['TierDefault']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['TierDefault']['max_width'],
        capability_limitation["max_height"] = self.setting_config['TierDefault']['max_height'],
        capability_limitation["max_length"] = self.setting_config['TierDefault']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['TierDefault']['weight_threshold']
        TierCapability(capability_limitation,self.config['Tier']['AgentTierID'], True)
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

    def test_POS_True(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        special_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        special_setting["pay_on_success"] = self.setting_config['SpecialSetting_pay_on_success']['pay_on_success']
        special_setting["cash_on_delivery"] = self.setting_config['SpecialSetting_pay_on_success']['cash_on_delivery']
        special_setting["core"] = self.setting_config['SpecialSetting_pay_on_success']['core']
        status_code, response, status = Special_Settings(special_setting,self.config['Tier']['MerchantID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"SperialSetting_POS",resultList,self.runId)

    def test_Core_True(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        special_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        special_setting["pay_on_success"] = self.setting_config['SpecialSetting_core']['pay_on_success']
        special_setting["cash_on_delivery"] = self.setting_config['SpecialSetting_core']['cash_on_delivery']
        special_setting["core"] = self.setting_config['SpecialSetting_core']['core']
        status_code, response, status = Special_Settings(special_setting,self.config['Tier']['MerchantID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"SperialSetting_Core",resultList,self.runId)

    def test_Cod_True(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        special_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        special_setting["pay_on_success"] = self.setting_config['SpecialSetting_cash_on_delivery']['pay_on_success']
        special_setting["cash_on_delivery"] = self.setting_config['SpecialSetting_cash_on_delivery']['cash_on_delivery']
        special_setting["core"] = self.setting_config['SpecialSetting_cash_on_delivery']['core']
        status_code, response, status = Special_Settings(special_setting,self.config['Tier']['MerchantID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"SperialSetting_COD",resultList,self.runId)

    def test_weight_overrange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Limitation_weight']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Limitation_weight']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Limitation_weight']['can_cod'],
        capability_limitation["core"] = self.setting_config['Limitation_weight']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Limitation_weight']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Limitation_weight']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Limitation_weight']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Limitation_weight']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Limitation_weight']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,1)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Limitation_weight",resultList,self.runId)

    def test_max_concurrent_trip_overrange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Limitation_max_concurrent_trip']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Limitation_max_concurrent_trip']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Limitation_max_concurrent_trip']['can_cod'],
        capability_limitation["core"] = self.setting_config['Limitation_max_concurrent_trip']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Limitation_max_concurrent_trip']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Limitation_max_concurrent_trip']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Limitation_max_concurrent_trip']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Limitation_max_concurrent_trip']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Limitation_max_concurrent_trip']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Limitation_MaxConcurrentTrip",resultList,self.runId)

    def test_width_overrange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Limitation_max_width']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Limitation_max_width']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Limitation_max_width']['can_cod'],
        capability_limitation["core"] = self.setting_config['Limitation_max_width']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Limitation_max_width']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Limitation_max_width']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Limitation_max_width']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Limitation_max_width']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Limitation_max_width']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,1,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Limitation_width",resultList,self.runId)

    def test_height_overrange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Limitation_max_height']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Limitation_max_height']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Limitation_max_height']['can_cod'],
        capability_limitation["core"] = self.setting_config['Limitation_max_height']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Limitation_max_height']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Limitation_max_height']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Limitation_max_height']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Limitation_max_height']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Limitation_max_height']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,1,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Limitation_height",resultList,self.runId)

    def test_length_overrange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Limitation_max_length']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Limitation_max_length']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Limitation_max_length']['can_cod'],
        capability_limitation["core"] = self.setting_config['Limitation_max_length']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Limitation_max_length']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Limitation_max_length']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Limitation_max_length']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Limitation_max_length']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Limitation_max_length']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,1,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Limitation_length",resultList,self.runId)

    def test_weight_threshold_overrange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Limitation_weight_threshold']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Limitation_weight_threshold']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Limitation_weight_threshold']['can_cod'],
        capability_limitation["core"] = self.setting_config['Limitation_weight_threshold']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Limitation_weight_threshold']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Limitation_weight_threshold']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Limitation_weight_threshold']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Limitation_weight_threshold']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Limitation_weight_threshold']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        if status == False:
            status = totalstatus
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Limitation_WeightThreshold",resultList,self.runId)

    def test_Agent_Core(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Capability_core']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Capability_core']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Capability_core']['can_cod'],
        capability_limitation["core"] = self.setting_config['Capability_core']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Capability_core']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Capability_core']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Capability_core']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Capability_core']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Capability_core']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Capability_Core",resultList,self.runId)

    def test_Agent_COD(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Capability_can_cod']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Capability_can_cod']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Capability_can_cod']['can_cod'],
        capability_limitation["core"] = self.setting_config['Capability_can_cod']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Capability_can_cod']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Capability_can_cod']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Capability_can_cod']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Capability_can_cod']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Capability_can_cod']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Capability_COD",resultList,self.runId)

    def test_Agent_POS(self):
        totalstatus = True
        resultList = []
        #Step 1 : Set Special Setting
        capability_limitation = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Special_Setting")
        capability_limitation["max_weight"] = self.setting_config['Capability_pay_on_success']['max_weight'],
        capability_limitation["max_concurrent_trip"] = self.setting_config['Capability_pay_on_success']['max_concurrent_trip'],
        capability_limitation["can_cod"] = self.setting_config['Capability_pay_on_success']['can_cod'],
        capability_limitation["core"] = self.setting_config['Capability_pay_on_success']['core'],
        capability_limitation["pay_on_success"] = self.setting_config['Capability_pay_on_success']['pay_on_success'],
        capability_limitation["max_width"] = self.setting_config['Capability_pay_on_success']['max_width'],
        capability_limitation["max_height"] = self.setting_config['Capability_pay_on_success']['max_height'],
        capability_limitation["max_length"] = self.setting_config['Capability_pay_on_success']['max_length'],
        capability_limitation["weight_threshold"] = self.setting_config['Capability_pay_on_success']['weight_threshold']
        status_code, response, status = Special_Settings(capability_limitation,self.config['Tier']['AgentTierID'])
        resultList.extend((status, response))
        #Step 2 : Create an Order
        status_code, OrderID, status = CreateOrder(self.setting_config,'4Hours',totalstatus,100,100,100,100)
        resultList.extend((status, OrderID))
        #Step 3 : Get DA Accesskey
        access_key = GetDeliveryAgentAccessKey(self.setting_config, "DA_Setting_Receive")
        #Step 4 : DA Receive Order
        status_code, response, status = DeliveryAgentReceive(OrderID,totalstatus)
        resultList.extend((status, response))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"Capability_POS",resultList,self.runId)

if __name__ == '__main__':
    unittest.main()
