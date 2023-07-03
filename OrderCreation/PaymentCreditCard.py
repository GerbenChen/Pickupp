#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from typing import Final
import unittest
import sys
sys.path.append("./")
import Method.CommonMethod as CommonMethod
import configparser
import Library.TestCaseHelper as TestCaseHelper

from Library.GlobalAdapter import *
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Method.CommonMethod import *
from Library.Config import dumplogger


class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class CreditCard_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.international_config = Newconfigparser()
        self.international_config.read('./Config/InternationalExpress.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Payment CreditCard"
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
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_CreateCard_StandardOrder(self):
        totalstatus = True
        resultList = []
        try:
            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config,'four_hours',"CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 5 : Dropoff Order
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "8713", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CreateCard_ExpressOrder(self):
        totalstatus = True
        resultList = []
        try:
            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config,'express',"CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 5 : Dropoff Order
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "8714", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CreateCard_InternationalOrder(self):
        try:
            totalstatus = True
            resultList = []
            mode = "lite"
            region = "SG"

            # Step 1 : Create an order
            api_response, status = OrderAPI.InternationalOrder(self.international_config, region, mode, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(api_response, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 4 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 5 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

        except KeyError as err:
            dumplogger.exception(err)
        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "8715", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()
