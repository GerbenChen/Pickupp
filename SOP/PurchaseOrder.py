#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time
from typing import Final
import unittest
import sys
sys.path.append("./")
from Library.GlobalAdapter import *
import Method.CommonMethod as CommonMethod
from Method.CommonMethod import*
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
import configparser
import Library.TestCaseHelper as TestCaseHelper

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class Order_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/purchase.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "SOP Purchase Flow"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.CommonVar.ShopHomeUrl = self.setting_config['Portal_Setting']['home_url']
        GlobalAdapter.CommonVar.TopUpUrl = self.setting_config['Api_Url']['top_up']
        GlobalAdapter.CommonVar.CreditCardUrl = self.setting_config['Api_Url']['credit_card']
        GlobalAdapter.CommonVar.StripeTokensUrl = self.setting_config['Api_Url']['stripe_tokens']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.AuthVar.ShopAuth = GetShopPortalAuth(self.setting_config, 'ShopControl_Setting_%s' % GlobalAdapter.FrameworkVar.Environment)
        self.PromotionStatusCode, self.PromotionCode,self.PromotionStatus, self.PromotionId = PromotionKeyCreate(4,self.config['PromotionTypeValue']['name'],self.config['PromotionTypeValue']['value'],self.config['PromotionTypeValue']['category'])
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        CleanTrips(320)
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        removePromotionKey(self.PromotionId)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_CheckSearchByGuest(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Open SOP homepage
            status_code, response, status = homepage(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 2 : Search SHOP by guest
            status_code, response, status = SopSearchGuest(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "781", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckSearchByLogin(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Get_auth_portal
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Open SOP Homepage
            status_code, response, status = homepage(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Search SHOP by Login
            status_code, response, status = SopSearchLogin(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "782", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderCreditCard(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"creditcard","",1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "783", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderWallet(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"wallet","",1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "784", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderAlipay(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"alipay","",1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "785", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderWechat(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"wechat","",1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "787", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderCreditCardPromotion(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"creditcard",self.PromotionCode[0],1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "788", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderWalletPromotion(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"wallet",self.PromotionCode[1],1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "789", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderAlipayPromotion(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"alipay",self.PromotionCode[2],1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "790", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_PurchaseOrderWechatPromotion(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Login and Get Authkey
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((AuthApiSpentTime.MerchantAuth, have_auth, check_result))
            #Step 2 : Check categories
            status_code, response, status = categories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 3 : Check SHOP - 1
            status_code, response, status = shop1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 4 : Check SHOP - 2
            status_code, response, status = shop2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 5 : Check SHOP - 3
            status_code, response, status = shop3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 6 : Check SHOP - 4
            status_code, response, status = shop4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 7 : Check Timeslot - 1
            status_code, response, status = timeslot1(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 8 : Check Timeslot - 2
            status_code, response, status = timeslot2(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Check Timeslot - 3
            status_code, response, status = timeslot3(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 10 : Check Timeslot - 4
            status_code, response, status = timeslot4(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 11 : Check Brower Store Namee
            status_code, response, status = BrowserStoreName(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 12 : Check Brower Store Inventories
            status_code, response, status = BrowserStoreInventories(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 13 : Check Brower Store Collection
            status_code, response, status = BrowserStoreCollection(totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 14 : Purchase Order by Credit Card
            status_code, response, status = PurchaseOrder(self.config,"wechat",self.PromotionCode[3],1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        #Step 15 : Update result to testrail
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "791", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_TrackOrder(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Purchase Order by Credit Card
            status_code, OrderNumber, status = PurchaseOrder(self.config,"creditcard","",1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderNumber))
            #Step 2 : Check Purchase Order Number
            status_code, TrackOrderNumber, status = TrackOrder(OrderNumber,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TrackOrderNumber))
            #Step 3 : Check Purchase order Detail
            status_code, response, status = TrackOrderDetail(TrackOrderNumber,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "792", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderStatusChanges(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Purchase Order by Credit Card
            status_code, OrderNumber, status = PurchaseOrder(self.config,"ChangeStatus","",4,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderNumber))
            #Step 2 : Went to Portal to Check Create SOP Order
            status_code, PurchaseList, status = PortalShopOrder(self.config,"PortalShopOrder",OrderNumber,4,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, PurchaseList))
            #Step 3 : Went to Portal to Change Purchase Order Status
            status_code, FulfilledOrderNumber, status = PortalOrderChangeStatus(self.config,"PortalOrderChangeStatus",PurchaseList,4,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, FulfilledOrderNumber))
            #Step 4 : Went to Admin to check Status was change to FULFILLED or not
            status_code, response, status = AdminPurchaseOrderStatus(FulfilledOrderNumber,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "810", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckPurchaseOrderInMPOrderList(self):
        totalstatus = True
        resultList = []
        try:
            #Step 1 : Purchase Order by Credit Card
            status_code, OrderNumber, status = PurchaseOrder(self.config,"creditcard","",1,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderNumber))
            #Step 1 : Check Purchase Order In Order List
            status_code, OrderInfo, status = GetMerchantPortalOrderList(1,OrderNumber,totalstatus)
            #resultList.extend((FrameworkVar.ApiSpentTime, status, OrderNumber))
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderInfo))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "936", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()  
