#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import Final
import unittest
import sys
sys.path.append("./")
# import os
# root_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
from Library.GlobalAdapter import *
import Method.CommonMethod as CommonMethod
from Method.CommonMethod import*
from Method.OrderMethod import *
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
import configparser
from Library.Config import dumplogger
import Library.TestCaseHelper as TestCaseHelper

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class Unbundle_behavior(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/UnbundleBehaviorConfig.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Unbundle Behavior"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.CommonVar.DAUrl = self.setting_config['DA_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_UnbundleBeforeAssign(self):
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
            #Step 4 : Create Order and Get OrderID
            OrderIDList = []
            OrderNumberList = []
            for i in range(2):
                status_code, OrderStatus, status = CreateOrder(self.config,'4Hours',totalstatus,Single=False)
                OrderIDList.append(OrderStatus[0])
                OrderNumberList.append(OrderStatus[1])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderIDList))
            #Get MP Order Price
            MPOrderPrice = GetMerchantOrderPrice(OrderNumberList[0])
            #Wait for Cronjob 60s
            time.sleep(60)
            #Step 5: Get Bundle ID
            BundleID,status = GetBundleIDInOrder(OrderIDList[0])
            resultList.extend((FrameworkVar.ApiSpentTime, status, BundleID))
            #Step 6: Remove order out of bundle order
            UnbundleResponse, status = UnbundleOrder(BundleID,OrderNumberList[0])
            OthersBundleIDList = UnbundleGetAllOrderIDFromResp(UnbundleResponse)
            if OrderIDList[1] in OthersBundleIDList:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The other order was equal to other, OrderID:" + OrderIDList[1]))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The other order was not equal to other, OrderID:" + OthersBundleIDList))
            #Step 7: Get Unbundle order Price and need to equal before bundle
            BundleOrderPrice,status = GetBundleOrderTotalPrice(BundleID)
            UnbundlePrice = GetTripsPriceInOrder(OrderIDList[0])
            if MPOrderPrice == UnbundlePrice and BundleOrderPrice != UnbundlePrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "Before Unbundle Price: %s, Bundle Price: %s, After Unbundle Price:%s"%(MPOrderPrice,BundleOrderPrice,UnbundlePrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "Before Unbundle Price: %s, Bundle Price: %s, After Unbundle Price:%s"%(MPOrderPrice,BundleOrderPrice,UnbundlePrice)))
            #Step 8: Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderStatus[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            #Step 9: Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10: Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11: Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9539", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_UnbundleCancelOneOrder(self):
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
            #Step 4 : Create Order and Get OrderID
            OrderIDList = []
            OrderNumberList = []
            for i in range(2):
                status_code, OrderStatus, status = CreateOrder(self.config,'4Hours',totalstatus,Single=False)
                OrderIDList.append(OrderStatus[0])
                OrderNumberList.append(OrderStatus[1])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderIDList))
            #Get MP Order Price
            MPOrderPrice = GetMerchantOrderPrice(OrderNumberList[1])
            #Wait for Cronjob 30s
            time.sleep(30)
            #Step 5: Get Bundle ID
            BundleID,status = GetBundleIDInOrder(OrderIDList[0])
            resultList.extend((FrameworkVar.ApiSpentTime, status, BundleID))
            #Cancel one Order on Bundle Order
            response, status = AdminCancelOrder(self.setting_config['Merchant Entity']['EntityID'], OrderIDList[0])
            #Get Bundle Price
            BundleOrderPrice,status = GetBundleOrderTotalPrice(BundleID)
            #Step 6 : Remove order out of bundle order
            UnbundleResponse, status = UnbundleOrder(BundleID,OrderNumberList[0])
            OthersBundleIDList = UnbundleGetAllOrderIDFromResp(UnbundleResponse)
            if OrderIDList[1] in OthersBundleIDList:
                resultList.extend((FrameworkVar.ApiSpentTime, True, OrderIDList[1]))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, OthersBundleIDList[1]))
            #Step 7: Get Unbundle order Price and need to equal before bundle
            UnbundlePrice = GetTripsPriceInOrder(OrderIDList[1])
            if MPOrderPrice == UnbundlePrice and BundleOrderPrice != UnbundlePrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "Before Unbundle Price: %s, Bundle Price: %s, After Unbundle Price:%s"%(MPOrderPrice,BundleOrderPrice,UnbundlePrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "Before Unbundle Price: %s, Bundle Price: %s, After Unbundle Price:%s"%(MPOrderPrice,BundleOrderPrice,UnbundlePrice)))
            #Step 8: Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderIDList[1],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            #Step 9: Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10: Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11: Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9540", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
