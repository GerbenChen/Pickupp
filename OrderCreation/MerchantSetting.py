#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
from typing import Final
import unittest
import configparser
import Library.TestCaseHelper as TestCaseHelper
import Method.CommonMethod as CommonMethod

from Library.GlobalAdapter import *
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Method.CommonMethod import *
from Method.AdminPortalMethod import AdminMerchantPage
from Library.Config import dumplogger


class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class Merchant_Setting(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Merchant Setting"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_PUDOSettingWithSO(self):
        resultList = []
        try:
            #Step 1 : Get merchant id
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Merchant_SO_Setting")
            resultList.extend((FrameworkVar.ApiSpentTime, bool(merchant_id), merchant_id))

            #Step 2 : Update Merchant service type setting to default
            merchants_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting","Default")
            status_code, merchant_response, status = AdminMerchantAPI.UpdateMerchantSetting( self.setting_config,merchant_id,merchants_setting)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))

            #Step 3 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 5 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            #Step 6 : Dropoff Process
            dropoff_response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            #Step 7 : Compar PU/DO Setting between service type setting and Dropoff Process
            order_detail = DeliveryAgentAPI.GetAndCheckDAOrderDetail(order_id)
            compair_status, message = AdminMerchantPage.PUDOSettingCompair(order_detail, merchant_response)
            resultList.extend((FrameworkVar.ApiSpentTime, compair_status, message))
        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "6645", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PUDOSettingOnlySO(self):
        resultList = []
        try:
            #Step 1 : Get merchant id
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Merchant_SO_Setting")
            resultList.extend((FrameworkVar.ApiSpentTime, bool(merchant_id), merchant_id))

            #Step 2 : Update Merchant service type setting to default
            merchants_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting","Default")
            status_code, merchant_response, status = AdminMerchantAPI.UpdateMerchantSetting( self.setting_config,merchant_id,merchants_setting)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))

            #Step 3 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config,'four_hours',"CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 5 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            #Step 6 : Dropoff Process
            dropoff_response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            #Step 7 : Compar PU/DO Setting between service type setting and Dropoff Process
            order_detail = DeliveryAgentAPI.GetAndCheckDAOrderDetail(order_id)
            compair_status, message = AdminMerchantPage.PUDOSettingCompair(order_detail, merchant_response)
            resultList.extend((FrameworkVar.ApiSpentTime, compair_status, message))
        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "6646", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckCreditCardChargedPending(self):
        resultList = []
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Order_CreateCard_Setting')
        try:

            # Step 1 : Get merchant id
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Order_CreateCard_Setting")
            resultList.extend((FrameworkVar.ApiSpentTime, bool(merchant_id), merchant_id))

            # Step 2 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Check wallet charged display pending after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Pending", "CREDIT_CARD")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9130", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckCreditCardChargedSuccess(self):
        resultList = []
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Order_CreateCard_Setting')
        try:

            # Step 1 : Get merchant id
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Order_CreateCard_Setting")
            resultList.extend((FrameworkVar.ApiSpentTime, bool(merchant_id), merchant_id))

            # Step 2 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 4 : Check wallet charged display Success after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Success", "CREDIT_CARD")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9131", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckWalletChargedSuccess(self):
        resultList = []
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Merchant_SO_Setting')
        try:

            # Step 1 : Get merchant id
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Merchant_SO_Setting")
            resultList.extend((FrameworkVar.ApiSpentTime, bool(merchant_id), merchant_id))

            # Step 2 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "Wallet")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Check wallet charged display Success after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Success", "CREDIT")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9132", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckOrderInOrderListPage(self):
        resultList = []
        try:

            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # #Step 2 : Check Order in MP Order List Page
            filter_status, status = MerchantPortal.GetOrderListByOrderNumber(order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, filter_status))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9419", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
