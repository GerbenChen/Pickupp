#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
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


class TaxAndPickuppCareFeeCheck(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/InternationalExpress.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Tax And Pickupp Care Fee"
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
    def test_PickuppCareFee_SG(self):
        totalstatus = True
        resultList = []

        try:
            # Step 1 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))

            # Step 2 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 3 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            # Step 4 : Create Next Day Order of MY
            api_response, order_id, status = MerchantPortal.CreatePickuppCareOrder(self.config, "SG")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 6 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 7 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Check Pickupp Care Fee By Order Number
            check_result, status = OrderMethod.GetAndCheckOrderFee(order_id, "0.70", "")
            resultList.extend((FrameworkVar.ApiSpentTime, status, check_result))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10499", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PickuppCareFee_HK(self):
        totalstatus = True
        resultList = []

        try:
            # Step 1 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))

            # Step 2 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 3 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            # Step 4 : Create Next Day Order of MY
            api_response, order_id, status = MerchantPortal.CreatePickuppCareOrder(self.config, "HK")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 6 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 7 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Check Pickupp Care Fee By Order Number
            check_result, status = OrderMethod.GetAndCheckOrderFee(order_id, "0.60", "0.0060")
            resultList.extend((FrameworkVar.ApiSpentTime, status, check_result))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10500", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
