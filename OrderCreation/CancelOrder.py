#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
# import os
# root_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
import time
from typing import Final
import unittest
import Method.CommonMethod as CommonMethod
import configparser
import Library.TestCaseHelper as TestCaseHelper

from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Library.GlobalAdapter import *
from Library.Config import dumplogger

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class CancelOrder(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/condition.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "DA Flow"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_AdminCancelOrder_BeforeAccept(self):
        resultList = []

        try:
            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            response = AdminOrderAPI.CancelOrder(merchant_id, order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))

            # Step 3 : Check Order Status Changed in MP
            order_status, status = MerchantPortal.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            # Step 4 : Check Order Status Changed in AP
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10950", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_MerchantCancelOrder_BeforeAccept(self):
        resultList = []

        try:
            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Cancel Order
            response, status = MerchantPortal.CancelOrder(order_id,"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 3 : Check Order Status Changed in MP
            order_status, status = MerchantPortal.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            # Step 4 : Check Order Status Changed in AP
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10951", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_AdminCancelOrder_AfterAccept(self):
        resultList = []

        try:
            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            response = AdminOrderAPI.CancelOrder(merchant_id, order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))

            # Step 4 : Check Order Status Changed in MP
            order_status, status = MerchantPortal.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            # Step 5 : Check Order Status Changed in AP
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10952", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_MerchantCancelOrder_AfterAccept(self):
        resultList = []

        try:
            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Cancel Order
            response, status = MerchantPortal.CancelOrder(order_id,"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Check Order Status Changed in MP
            order_status, status = MerchantPortal.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            # Step 5 : Check Order Status Changed in AP
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10953", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
