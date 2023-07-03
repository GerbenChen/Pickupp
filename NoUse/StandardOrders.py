#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import Final
import sys
sys.path.append("./")
from Library.GlobalAdapter import *
import unittest
import Method.CommonMethod as CommonMethod
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
import configparser


class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class Standard_Order(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/StandardOrders.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Standard Others"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Standard_Order_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId, self.TestSuiteName)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    def test_Standard_HomeDelivery(self):
        totalstatus = True
        resultList = []

        try:
            #Step 1 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))

            #Step 2 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            #Step 3 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            # Step 4 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config, "HomeDelivery")
            resultList.extend((status, OrderID))

            # Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID, totalstatus)
            resultList.extend((status, filterstatus))

            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderID, da_id)
            resultList.extend((status, api_response))

            # Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))

            # Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((status, response))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        totalstatus = CommonMethod.CheckTotalStatus(resultList)
        resultList = CommonMethod.TranslateForStatus(resultList)
        AddResultByStep(totalstatus, self.testIds, "HomeDelivery", resultList, self.runId)

    def test_Standard_SelfPickUp(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            # Step 2 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            # Step 3 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            # Step 4 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config, "SelfPickUp")
            resultList.extend((status, OrderID))

            # Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID, totalstatus)
            resultList.extend((status, filterstatus))

            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderID, da_id)
            resultList.extend((status, api_response))

            # Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))

            # Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((status, response))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        totalstatus = CommonMethod.CheckTotalStatus(resultList)
        resultList = CommonMethod.TranslateForStatus(resultList)
        AddResultByStep(totalstatus, self.testIds, "SelfPickUp", resultList, self.runId)

    def test_Standard_HomeDelivery_Multiple(self):
        totalstatus = True
        resultList = []

        try:
            # Step 1 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            # Step 2 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            # Step 3 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            # Step 4 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config, "HomeDelivery", "Multiple")
            resultList.extend((status, OrderID))

            # Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID, totalstatus)
            resultList.extend((status, filterstatus))

            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderID, da_id)
            resultList.extend((status, api_response))

            # Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))

            # Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((status, response))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        totalstatus = CommonMethod.CheckTotalStatus(resultList)
        resultList = CommonMethod.TranslateForStatus(resultList)
        AddResultByStep(totalstatus, self.testIds, "HomeDeliveryMultiple", resultList, self.runId)

    def test_Standard_SelfPickUp_Multiple(self):
        totalstatus = True
        resultList = []

        try:
            #Step 1 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            #Step 2 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            #Step 3 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))

            # Step 4 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config, "SelfPickUp", "Multiple")
            resultList.extend((status, OrderID))

            # Step 5 : Check Order in Order List
            status_code, filterstatus, status = GetMerchantPortalOrderListByOrderNumber(OrderID, totalstatus)
            resultList.extend((status, filterstatus))

            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderID, da_id)
            resultList.extend((status, api_response))

            # Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((status, response))

            # Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((status, response))
        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        totalstatus = CommonMethod.CheckTotalStatus(resultList)
        resultList = CommonMethod.TranslateForStatus(resultList)
        AddResultByStep(totalstatus, self.testIds, "SelfPickUpMultiple", resultList, self.runId)


if __name__ == '__main__':
    unittest.main()
