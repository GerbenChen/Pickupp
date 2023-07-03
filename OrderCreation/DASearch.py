#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
import unittest
import Method.CommonMethod as CommonMethod
import configparser
import Library.TestCaseHelper as TestCaseHelper

from typing import Final
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Library.GlobalAdapter import *
from Library.Config import dumplogger
from Method.DeliveryAgentMethod import SearchMethod

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class DASearch(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "DA App Search"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")
        self.test_case_time_start = time.time()


    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_SearchOrderByPartNumber(self):
        resultList = []

        try:
            #Step 1 : Search order by part of order number
            status, api_response = SearchMethod.SearchOrder("HK", 100)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12282", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_SearchOrderByMerchant(self):
        resultList = []

        try:
            #Step 1 : Search order by Merchant
            status, api_response = SearchMethod.SearchOrder("archer", 100)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12283", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_SearchOrderByRecipient(self):
        resultList = []
        try:

            #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 3 : Search order by Recipient
            status, api_response = SearchMethod.SearchOrder("archer", 100)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12284", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_SearchOrderByFullOrder(self):
        resultList = []
        try:

            #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 3 : Search order by Full Order number
            status, api_response = SearchMethod.SearchOrder(order_number, 100)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12285", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_SearchOrderByUnreasonableNumber(self):
        resultList = []
        try:
            #Step 1 : Search order by Unreasonable Number
            status, api_response = SearchMethod.SearchOrder("123AA557788##", 100, "Unreasonable")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12286", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
