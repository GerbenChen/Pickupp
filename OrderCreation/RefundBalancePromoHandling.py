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
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class RefundBalancePromoHandling(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/RefundBalancePromoHandling.ini')
        self.international_config = Newconfigparser()
        self.admin_setting_config = configparser.ConfigParser()
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Refund Balance Promo Handling"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_RefundBalancePromoHandlingCreditPromo(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Check the total promo credit value on profile and choose one
            PromoList, status = MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
            PromoValue = random.choice(PromoList)
            resultList.extend((AuthApiSpentTime.MerchantAuth, status, PromoValue))
            # Step 2 : Choose the PromoID and Promo Credit to Create an Order
            self.config["condition_4HoursPromoCredit"]["Expiryid"]=PromoValue[0]
            with open('./Config/RefundBalancePromoHandling.ini', 'w') as configfile:    # save
                self.config.write(configfile)
            status_code, statusList, status = CreateOrder(self.config,'4HoursPromoCredit',totalstatus,"All",Single=False)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 3 : Check Credit Promo Value in list and Value correct or not 
            SencondTimePromoList, status = MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
            SubValuelist, status = GetSublistValueInList(self.config["condition_4HoursPromoCredit"]["Expiryid"],SencondTimePromoList)
            if status == True:
                UsingValue = int(self.config["condition_4HoursPromoCredit"]["ExpiryAmount"])
                print ("Using Value = %s"%UsingValue)
                print (SubValuelist)
                if (int(PromoValue[1]) - UsingValue) == int(SubValuelist[1]):
                    resultList.extend((FrameworkVar.ApiSpentTime, True, SubValuelist))
                else:
                    resultList.extend((FrameworkVar.ApiSpentTime, False, SubValuelist))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, PromoList))
            # Step 4 : Cancal Order
            response, status = MerchantPortal.CancelOrder(statusList[0],"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 5 : Check the promo credit have return or not
            PromoList, status = MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
            SubValuelist, status = GetSublistValueInList(self.config["condition_4HoursPromoCredit"]["Expiryid"],PromoList)
            if PromoValue == SubValuelist:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "%s = %s"%(PromoValue,SubValuelist)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "%s != %s"%(PromoValue,SubValuelist))) 
        except Exception as err:
            dumplogger.exception(err)
         # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12321", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_RefundBalancePromoHandlingWallet(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Check the total wallet value on profile 
            WalletValue, status = MerchantPortal.GetMerchantPaymentProfileWallet(self)
            resultList.extend((AuthApiSpentTime.MerchantAuth, status, WalletValue))
            # Step 2 : Create an Order
            status_code, statusList, status = CreateOrder(self.config,'4HoursWallet',totalstatus,"None",Single=False)
            resultList.extend((FrameworkVar.ApiSpentTime, status, statusList))
            # Step 3 : Check wallet Value and Value correct or not 
            WalletValueAfterCreateOrder, status = MerchantPortal.GetMerchantPaymentProfileWallet(self)
            UsingValue = int(self.config["condition_4HoursWallet"]["ExpiryAmount"])
            if float(WalletValue - UsingValue) == float(WalletValueAfterCreateOrder):
                    resultList.extend((FrameworkVar.ApiSpentTime, True, WalletValueAfterCreateOrder))
            else:
                    resultList.extend((FrameworkVar.ApiSpentTime, False, WalletValueAfterCreateOrder))
            # Step 4 : Cancal Order
            response, status = MerchantPortal.CancelOrder(statusList[0],"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 5 : Check the wallet return or not
            WalletValueAfterCancel, status = MerchantPortal.GetMerchantPaymentProfileWallet(self)
            if WalletValue == WalletValueAfterCancel:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "%s = %s"%(WalletValue,WalletValueAfterCancel)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "%s != %s"%(WalletValue,WalletValueAfterCancel))) 
        except Exception as err:
            dumplogger.exception(err)
         # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12321", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()