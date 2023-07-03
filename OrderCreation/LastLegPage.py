#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
from typing import Final
import unittest
import configparser
import Library.TestCaseHelper as TestCaseHelper

from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Method.CommonMethod import *
from Library.GlobalAdapter import *
from Library.Config import dumplogger

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class LastLegPage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/StandardOrders.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "LastLeg Page"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'LastLeg_Account_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_LastLeg_CheckTripPoolList(self):
        totalstatus = True
        resultList = []
        try:

            #Step 1 : Get Merchant portal auth
            resultList.extend((FrameworkVar.ApiSpentTime, bool(GlobalAdapter.AuthVar.MerchantPortalAuth), GlobalAdapter.AuthVar.MerchantPortalAuth))

            #Step 2 : Get Admin Auth
            resultList.extend((FrameworkVar.ApiSpentTime, bool(GlobalAdapter.AuthVar.AdminAuth), GlobalAdapter.AuthVar.AdminAuth))

            #Step 3 : Create an order
            api_response, order_id, status = MerchantPortal.CreateStandardOrder(self.config, "SelfPickUp")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 4 : Check Order in Trip Pool List and Get New Trip id
            new_trip_id, status = AdminLastLegAPI.GetTripPoolListByOrderNumber(self.setting_config, order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, new_trip_id))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9548", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_LastLeg_CheckBundlePoolList(self):
        totalstatus = True
        resultList = []
        try:

            #Step 1 : Get Merchant portal auth
            resultList.extend((FrameworkVar.ApiSpentTime, bool(GlobalAdapter.AuthVar.MerchantPortalAuth), GlobalAdapter.AuthVar.MerchantPortalAuth))

            #Step 2 : Get Admin Auth
            resultList.extend((FrameworkVar.ApiSpentTime, bool(GlobalAdapter.AuthVar.AdminAuth), GlobalAdapter.AuthVar.AdminAuth))

            #Step 3 : Create an order
            api_response, order_id, status = MerchantPortal.CreateStandardOrder(self.config, "SelfPickUp")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 4 : Check Order in Trip Pool List and Get New Trip id
            new_trip_id, status = AdminLastLegAPI.GetTripPoolListByOrderNumber(self.setting_config, order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, new_trip_id))

            #Step 5 : Get Bundle id By New Trip id
            bundle_id, status = AdminLastLegAPI.GetBundleIdByNewTripId(self.setting_config, new_trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, bool(bundle_id), bundle_id))

            #Step 6 : Check Order in Bundle Pool List
            service_offering_id, status = AdminLastLegAPI.GetBundleListByBundleId(self.setting_config, bundle_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, service_offering_id))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9549", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
