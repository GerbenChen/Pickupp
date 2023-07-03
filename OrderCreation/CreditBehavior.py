#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
from Method.OrderMethod import *
from typing import Final
import unittest
import configparser
import Method.CommonMethod as CommonMethod
import Library.TestCaseHelper as TestCaseHelper

from Library.GlobalAdapter import *
from Method.CommonMethod import *
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
from Library.Config import dumplogger

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class CreditBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/CreditBehaviorConfig.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "CreditBehavior"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.TopUpAmount = self.setting_config['PromoCredits']['amount']
        GlobalAdapter.CommonVar.TopUpUrl = self.setting_config['Api_Url']['top_up']
        TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        self.test_case_time_start = time.time()
        self.PromotionStatusCode, self.PromotionCode,self.PromotionStatus, self.PromotionId = PromotionKeyCreate(3,self.config['PromotionTypeValue']['name'],self.config['PromotionTypeValue']['value'],self.config['PromotionTypeValue']['category'])
        

    @classmethod
    def tearDownClass(self):
        CleanTrips(320)
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        removePromotionKey(self.PromotionId)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_CreditBehavior4HoursExpiryPayALL(self):
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
            # Step 4 : Create an order, ServiceType = 4Hours, Payment = Promo Credit
            status_code, statusList, status = CreateOrder(self.config,'4HoursAll',totalstatus,"All",minimum=True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 5 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 7 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 11 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 12 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 13 : Check Order Payment Status
            PaymentList, status= GetMerchantOrderPaymentStatus(statusList[2])
            resultList.extend((FrameworkVar.ApiSpentTime,status, PaymentList))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10602", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_CreditBehavior4HoursExpiryPaySection(self):
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
            PromoList, status = MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
            PromoValue = random.choice(PromoList)
            CommonMethod.WriteDataInConfigFlie(self.config,'./Config/CreditBehaviorConfig.ini',"condition_4HoursSection","Expiryid",PromoValue[0])
            status_code, statusList, status = CreateOrder(self.config,'4HoursSection',totalstatus,"Section",minimum=True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 5 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 7 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 11 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 12 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 13 : Check Order Payment Status
            PaymentList, status= GetMerchantOrderPaymentStatus(statusList[2])
            resultList.extend((FrameworkVar.ApiSpentTime,status, PaymentList))

        except Exception as err:
            dumplogger.exception(err)
        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10603", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CreditBehavior4HoursCreditPayALL(self):
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
            status_code, statusList, status = CreateOrder(self.config,'4HoursNone',totalstatus,"None",minimum=True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 5 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 7 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 11 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 12 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 13 : Check Order Payment Status
            PaymentList, status= GetMerchantOrderPaymentStatus(statusList[2])
            resultList.extend((FrameworkVar.ApiSpentTime,status, PaymentList))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10604", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CreditBehavior4HoursExpiryPayAndPromotionALL(self):
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
            # Step 4 : Choose the PromoID and Promo Credit to Create an order, ServiceType = 4Hours, Payment = Promo Credit
            PromoList, status = MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
            PromoValue = random.choice(PromoList)
            CommonMethod.WriteDataInConfigFlie(self.config,'./Config/CreditBehaviorConfig.ini',"condition_Promo4HoursAll","Expiryid",PromoValue[0])
            status_code, statusList, status = CreateOrder(self.config,'Promo4HoursAll',totalstatus,"All",promocode=self.PromotionCode[0],promoid=self.PromotionId,minimum=True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 5 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 7 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 11 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 12 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 13 : Check Order Payment Status
            PaymentList, status= GetMerchantOrderPaymentStatus(statusList[2])
            resultList.extend((FrameworkVar.ApiSpentTime,status, PaymentList))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10736", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CreditBehavior4HoursExpiryPayAndPromotionSection(self):
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
            PromoList, status = MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
            PromoValue = random.choice(PromoList)
            CommonMethod.WriteDataInConfigFlie(self.config,'./Config/CreditBehaviorConfig.ini',"condition_Promo4HoursSection","Expiryid",PromoValue[0])
            status_code, statusList, status = CreateOrder(self.config,'Promo4HoursSection',totalstatus,"Section",promocode=self.PromotionCode[1],promoid=self.PromotionId,minimum=True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 5 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 7 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 11 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 12 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 13 : Check Order Payment Status
            PaymentList, status = GetMerchantOrderPaymentStatus(statusList[2])
            resultList.extend((FrameworkVar.ApiSpentTime,status, PaymentList))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10737", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CreditBehavior4HoursCreditPayAndPromotionALL(self):
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
            PromoList, status = MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
            PromoValue = random.choice(PromoList)
            CommonMethod.WriteDataInConfigFlie(self.config,'./Config/CreditBehaviorConfig.ini',"condition_Promo4HoursAll","Expiryid",PromoValue[0])
            status_code, statusList, status = CreateOrder(self.config,'Promo4HoursNone',totalstatus,"None",promocode=self.PromotionCode[2],promoid=self.PromotionId,minimum=True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 5 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 7 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 11 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 12 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 13 : Check Order Payment Status
            PaymentStatusList, status= GetMerchantOrderPaymentStatus(statusList[2])
            resultList.extend((FrameworkVar.ApiSpentTime,status, PaymentStatusList))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "10738", resultList, self.test_case_time_start)

'''
    @TestCaseHelper.TestTimed
    def test_CreditBehaviorCouponCodeNotExpired(self):
        totalstatus = True
        resultList = []
        # Step 1 : Get Merchant Auth Key
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
        # Step 2 : Get Admin Auth key
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
        # Step 3 : Get DA Auth key
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
        # Step 4 : Setup Coupon Code
        status_code, status = Discounts(self.config,"couponnotexpired")
        resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
        # Step 5 : Create an order, ServiceType = 4Hours, type = coupon
        status_code, statusList, status = CreateOrder(self.config,'CouponCodeNotExpired',totalstatus,"All",Single=False)
        resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
        # Step 6 : Check OrderStatus after Create Order
        OrderStatus = GetAdminOrderStatus(statusList[0])
        status = CompareWithValue(OrderStatus,"PENDING")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        # Step 7 : Assign to DA
        da_id = GetDAId(self.setting_config, "DA_Setting")
        api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
        resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
        # Step 8 : Check OrderStatus after Assign
        OrderStatus = GetAdminOrderStatus(statusList[0])
        status = CompareWithValue(OrderStatus,"ACCEPTED")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        # Step 9 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        # Step 10 : Check OrderStatus after Enroute
        OrderStatus = GetAdminOrderStatus(statusList[0])
        status = CompareWithValue(OrderStatus,"ENROUTE")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        # Step 11 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        # Step 12 : Dropoff
        response, status = DropOff(tripid)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        # Step 13 : Check OrderStatus after Dropoff
        OrderStatus = GetAdminOrderStatus(statusList[0])
        status = CompareWithValue(OrderStatus,"DROPPED_OFF")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11577", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CreditBehaviorCouponCodeExpired(self):
        totalstatus = True
        resultList = []
        # Step 1 : Get Merchant Auth Key
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
        # Step 2 : Get Admin Auth key
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
        # Step 3 : Get DA Auth key
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
        # Step 4 : Setup Coupon Code
        status_code, status = Discounts(self.config,"couponexpired")
        resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
        # Step 5 : Create an order, ServiceType = 4Hours, type = coupon
        status_code, statusList, status = CreateOrder(self.config,'CouponCodeNotExpired',totalstatus,"All",Single=False)
        resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11578", resultList, self.test_case_time_start)

'''
if __name__ == '__main__':
    unittest.main()