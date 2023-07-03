#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
from typing import Final

import unittest
import Method.CommonMethod as CommonMethod
import Method.OrderMethod as OrderMethod
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
import configparser
from Library.GlobalAdapter import *
from Library.Config import dumplogger
import Library.TestCaseHelper as TestCaseHelper

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class AdminOrderDetailPage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Admin Order Detail Page"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Order_CreateCard_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_EditOrderDetail(self):
        resultList = []

        try:
            # Step 1 : Create order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config,'four_hours',"CreditCard", True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Update Order detail from admin Order detail page
            api_response, status = AdminOrderAPI.UpdateOrderDetail(order_id, api_response)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13363", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
