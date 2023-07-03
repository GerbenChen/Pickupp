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

from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Method.AdminPortalMethod import AdminMerchantPage
from Method.MerchantPortalMethod import PaymentProfilePage
from Library.GlobalAdapter import *
from Library.Config import dumplogger
import Library.TestCaseHelper as TestCaseHelper

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class RefundOrder(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/condition.ini')
        self.international_config = Newconfigparser()
        self.international_config.read('./Config/InternationalExpress.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Refund Order"
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
    def test_RefundOrder_CreditCard(self):
        totalstatus = True
        resultList = []

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3: Enroute
            response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            response = AdminOrderAPI.CancelOrder(merchant_id, order_id, 30)
            resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))

            # Step 5 : Check wallet charged display Cancelled after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Success", "CREDIT_CARD")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

            # Step 6 : Check Order Transaction History in MP
            check_status, data_description = PaymentProfilePage.GetAndCheckTransactionHistory(order_id, "30")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11334", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_RefundOrder_Wallet(self):
        totalstatus = True
        resultList = []

        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Merchant_SO_Setting')

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "Wallet")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3: Enroute
            response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            api_response, status = AdminOrderAPI.CancelOrder(merchant_id, order_id, 60)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Check wallet charged display Cancelled after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Success", "CREDIT")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

            # Step 6 : Check Order Transaction History in MP
            check_status, data_description = PaymentProfilePage.GetAndCheckTransactionHistory(order_id, "60")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11335", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_RefundOrder_PromoCredit(self):
        totalstatus = True
        resultList = []

        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Payments_Setting')

        try:
            # Step 1 : Create an order
            status_code, statusList, status = CreateOrder(self.config, 'PromoCredit', totalstatus, "All", Single=False)
            order_id = statusList[0]
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3: Enroute
            response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            api_response, status = AdminOrderAPI.CancelOrder(merchant_id, order_id, 30)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Check wallet charged display Cancelled after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Success", "CREDIT_CARD")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

            # Step 6 : Check Order Transaction History in MP
            check_status, data_description = PaymentProfilePage.GetAndCheckTransactionHistory(order_id, "30")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11336", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_RefundOrder_ExpressOrder(self):
        totalstatus = True
        resultList = []

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'express', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3: Enroute
            response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            api_response, status = AdminOrderAPI.CancelOrder(merchant_id, order_id, 30)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Check wallet charged display Cancelled after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Success", "CREDIT_CARD")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

            # Step 6 : Check Order Transaction History in MP
            check_status, data_description = PaymentProfilePage.GetAndCheckTransactionHistory(order_id, "30")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11337", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_RefundOrder_InternationalOrder(self):
        totalstatus = True
        resultList = []
        mode = "lite"
        region = "SG"
        try:
            # Step 1 : Create an order
            status_code, orderlist, status = InternationalHKtoOther(self.international_config, region, mode, totalstatus)
            order_id = orderlist[0]
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_id))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3: Enroute
            response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            api_response, status = AdminOrderAPI.CancelOrder(merchant_id, order_id, 30)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Check wallet charged display Cancelled after order created
            check_status, data_description = AdminMerchantPage.GetAndCheckWallerHistory(order_id, merchant_id, "Success", "CREDIT_CARD")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

            # Step 6 : Check Order Transaction History in MP
            check_status, data_description = PaymentProfilePage.GetAndCheckTransactionHistory(order_id, "30")
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, data_description))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11338", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()
