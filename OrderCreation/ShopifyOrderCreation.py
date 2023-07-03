#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
from typing import Final
import unittest
import Method.CommonMethod as CommonMethod
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
import configparser
from Library.GlobalAdapter import *
from Core.ShopifyAPIQuery import *
import re
from Library.Config import dumplogger
import Library.TestCaseHelper as TestCaseHelper

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class ShopifyOrderCreated(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ShopifyOrderCreation.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Shopify Automation Test"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        self.test_case_time_start = time.time()
        LinkShopify(self.setting_config)

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        UnlinkShopify(self.setting_config)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_ShopifyOrderCreationNotFulfilled(self):
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
            #Step 4 : Login Shopify and Create an Order
            StatusCode , OrderStatusList, status = ShopifyCreateOrder(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatusList))
            #Step 5 : Went to MP > Shopify > Send with Pickupp > Bulk Create Sales Requests
            StatusCode , OrderID, status = BulkCreateOrder(self.config, float(OrderStatusList[2])/float(OrderStatusList[3]) , OrderStatusList[0], totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderID))
            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderID,da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            #Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10: Check Status on Shopify
            OrderName=re.findall("\d+",OrderStatusList[0])
            StatusCode , ShopifyOrderStatusList, status = GetShopifyOrderStatus(OrderStatusList[4],totalstatus)
            if (ShopifyOrderStatusList[0] == None and
                ShopifyOrderStatusList[1] == self.config['ShopifyExpectedResult']['PaymentStatus'] and
                 ShopifyOrderStatusList[2] == OrderStatusList[2]):
                resultList.extend((FrameworkVar.ApiSpentTime, True, ShopifyOrderStatusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, ShopifyOrderStatusList))
        except Exception as err:
            dumplogger.exception(err)

        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10482", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_ShopifyOrderCreationFulfilled(self):
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
            #Step 4 : Login Shopify and Create an Order
            StatusCode , OrderStatusList, status = ShopifyCreateOrder(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatusList))
            #Step 5 : Went to MP > Shopify > Send with Pickupp > Bulk Create Sales Requests
            StatusCode , OrderID, status = OutBoundFulfillment(self.config, float(OrderStatusList[2])/float(OrderStatusList[3]) , OrderStatusList[0], OrderStatusList[4], totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderID))
            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(OrderID,da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            #Step 7 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10: Check Status on Shopify
            OrderName=re.findall("\d+",OrderStatusList[0])
            StatusCode , ShopifyOrderStatusList, status = GetShopifyOrderStatus(OrderStatusList[4],totalstatus)
            if (ShopifyOrderStatusList[0] == self.config['ShopifyFulfillmentExpectedResult']['FulfillmentStatus'] and
                ShopifyOrderStatusList[1] == self.config['ShopifyFulfillmentExpectedResult']['PaymentStatus'] and
                 ShopifyOrderStatusList[2] == OrderStatusList[2]):
                resultList.extend((FrameworkVar.ApiSpentTime, True, ShopifyOrderStatusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, ShopifyOrderStatusList))
        except Exception as err:
            dumplogger.exception(err)

        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11000", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()  