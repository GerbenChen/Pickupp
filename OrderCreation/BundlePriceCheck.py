#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
from typing import Final
import unittest
import configparser
import Method.CommonMethod as CommonMethod
import Library.GlobalAdapter as GlobalAdapter
import Library.TestCaseHelper as TestCaseHelper

from Method.CommonMethod import*
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
from Library.Config import dumplogger
from Library.GlobalAdapter import *

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class Bundle_Price_Check(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/BundlePriceCheckConfig.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Bundle Price Check"
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
    def test_BundlePriceSameDay(self):
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
            #avoid cronjob trigger time
            if 55 >= int(datetime.now().second) > 50 or 25 >=int(datetime.now().second) > 20:
                pass
            else:
                TimeCul = abs(30-int(datetime.now().second))
                if 20 - TimeCul > 0:
                    NeedToWaitTime = 20 - TimeCul
                    time.sleep(NeedToWaitTime)
                else:
                    NeedToWaitTime = 50 - TimeCul
                    time.sleep(NeedToWaitTime)
            #Step 4 : Create Order and Get OrderID
            OrderIDList = []
            OrderNumberList = []
            for i in range(2):
                status_code, OrderStatus, status = CreateOrder(self.config,'SameDay',totalstatus,Single=False)
                OrderIDList.append(OrderStatus[0])
                OrderNumberList.append(OrderStatus[1])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderIDList))
            #Step 5: Check Total Order Price before cronjob
            #Get Price From merchant
            MPTotalOrderPrice=0
            for OrderNumberInList in OrderNumberList:
                Price = GetMerchantOrderPrice(OrderNumberInList)
                MPTotalOrderPrice += int(float(Price))
            #Get Price From Admin
            APTotalOrderPrice=0
            for OrderIDInList in OrderIDList:
                Price = GetTripsPriceInOrder(OrderIDInList)
                APTotalOrderPrice += int(float(Price))
            if MPTotalOrderPrice == APTotalOrderPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "Check MPTotalPrice : %s equal to APTotalPrice : %s" % (MPTotalOrderPrice,APTotalOrderPrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "Check MPTotalPrice : %s not equal to APTotalPrice : %s" % (MPTotalOrderPrice,APTotalOrderPrice)))
            #Wait for Cronjob 60s
            time.sleep(60)
            #Step 6: Get Bundle ID
            BundleID,status = GetBundleIDInOrder(OrderStatus[0])
            resultList.extend((FrameworkVar.ApiSpentTime, status, BundleID))
            #Step 7 : Get Bundle Total Price
            da_id = GetDAId(self.setting_config, "DA_Setting")
            TotalBundlePrice,status = GetBundleOrderTotalPrice(BundleID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TotalBundlePrice))
            #Step 8 : Assign Bundle Order to DA
            TripList = []
            for OrderIDInList in OrderIDList:
                tripid = GetAdminOrderTripsID(OrderIDInList)
                TripList.append(tripid)
            response, status = AssignBundleToDeliveryAgent(BundleID, da_id, TripList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Get Total Price from DA
            status_code, TotalDAPrice, status = GetDAReceiveStatus(BundleID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TotalDAPrice))
            #Step 10 : Check Merchant Price Was Changed or not
            if TotalBundlePrice != MPTotalOrderPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The Merchant Price Was Changed After Cronjob"))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The Merchant Price Was Not Changed After Cronjob"))
            #Step 11 : Check Bundle Price need to equal to DA
            if TotalBundlePrice == TotalDAPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The Bundle Price  : %s equal to DA Price : %s" % (TotalBundlePrice,TotalDAPrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The Bundle Price : %s was not equal to DA Price : %s" % (TotalBundlePrice,TotalDAPrice)))
            #Step 12 : Check DA Price was not to equal to Merchant
            if MPTotalOrderPrice != TotalDAPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The DA Price Was Changed After Cronjob"))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The DAPrice Was Not Changed After Cronjob"))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9182", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_BundlePriceNextDay(self):
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
            #avoid cronjob trigger time
            if 55 >= int(datetime.now().second) > 50 or 25 >=int(datetime.now().second) > 20:
                pass
            else:
                TimeCul = abs(30-int(datetime.now().second))
                if 20 - TimeCul > 0:
                    NeedToWaitTime = 20 - TimeCul
                    time.sleep(NeedToWaitTime)
                else:
                    NeedToWaitTime = 50 - TimeCul
                    time.sleep(NeedToWaitTime)
            #Step 4 : Create Order and Get OrderID
            OrderIDList = []
            OrderNumberList = []
            for i in range(2):
                status_code, OrderStatus, status = CreateOrder(self.config,'NextDay',totalstatus,Single=False)
                OrderIDList.append(OrderStatus[0])
                OrderNumberList.append(OrderStatus[1])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderIDList))
            #Step 5: Check Total Order Price before cronjob
            #Get Price From merchant
            MPTotalOrderPrice=0
            for OrderNumberInList in OrderNumberList:
                Price = GetMerchantOrderPrice(OrderNumberInList)
                MPTotalOrderPrice += int(float(Price))
            #Get Price From Admin
            APTotalOrderPrice=0
            for OrderIDInList in OrderIDList:
                Price = GetTripsPriceInOrder(OrderIDInList)
                APTotalOrderPrice += int(float(Price))
            if MPTotalOrderPrice == APTotalOrderPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "Check MPTotalPrice : %s equal to APTotalPrice : %s" % (MPTotalOrderPrice,APTotalOrderPrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "Check MPTotalPrice : %s not equal to APTotalPrice : %s" % (MPTotalOrderPrice,APTotalOrderPrice)))
            #Inbound and Edit Pickup time
            for i in range(len(OrderNumberList)):
                Orderstatus, status= AdminWareHousesAPI.Inbound(self.config["warehouses_id"][GlobalAdapter.FrameworkVar.Environment],OrderNumberList[i])
            #Wait for Cronjob 60s
            time.sleep(60)
            #Step 6: Get Bundle ID
            BundleID, status = GetBundleIDInOrder(OrderStatus[0])
            resultList.extend((FrameworkVar.ApiSpentTime, status, BundleID))
            for i in range(len(OrderNumberList)):
                TripId, status = GetDAMyTrips(OrderIDList[i])
                status_code, status = EditAdminTripTimeStatus(self.config,"NextDay",TripId)
            #Step 7 : Get Bundle Total Price
            da_id = GetDAId(self.setting_config, "DA_Setting")
            TotalBundlePrice,status = GetBundleOrderTotalPrice(BundleID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TotalBundlePrice))
            #Step 8 : Assign Bundle Order to DA
            TripList = []
            for OrderIDInList in OrderIDList:
                tripid = GetAdminOrderTripsID(OrderIDInList)
                TripList.append(tripid)
            response, status = AssignBundleToDeliveryAgent(BundleID, da_id, TripList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Get Total Price from DA
            status_code, TotalDAPrice, status = GetDAReceiveStatus(BundleID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TotalDAPrice))
            #Step 10 : Check Merchant Price Was Changed or not
            if TotalBundlePrice != MPTotalOrderPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The Merchant Price Was Changed After Cronjob"))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The Merchant Price Was Not Changed After Cronjob"))
            #Step 11 : Check Bundle Price need to equal to DA
            if TotalBundlePrice == TotalDAPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The Bundle Price  : %s equal to DA Price : %s" % (TotalBundlePrice,TotalDAPrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The Bundle Price : %s was not equal to DA Price : %s" % (TotalBundlePrice,TotalDAPrice)))
            #Step 12 : Check DA Price was not to equal to Merchant
            if MPTotalOrderPrice != TotalDAPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The DA Price Was Changed After Cronjob"))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The DAPrice Was Not Changed After Cronjob"))
        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9183", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_BundlePriceCollection(self):
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
            #avoid cronjob trigger time
            if 55 >= int(datetime.now().second) > 50 or 25 >=int(datetime.now().second) > 20:
                pass
            else:
                TimeCul = abs(30-int(datetime.now().second))
                if 20 - TimeCul > 0:
                    NeedToWaitTime = 20 - TimeCul
                    time.sleep(NeedToWaitTime)
                else:
                    NeedToWaitTime = 50 - TimeCul
                    time.sleep(NeedToWaitTime)
            #Step 4 : Create Order and Get OrderID
            OrderIDList = []
            OrderNumberList = []
            for i in range(2):
                status_code, OrderStatus, status = CreateOrder(self.config,'Collection',totalstatus,Single=False)
                OrderIDList.append(OrderStatus[0])
                OrderNumberList.append(OrderStatus[1])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderIDList))
            #Step 5: Check Total Order Price before cronjob
            #Get Price From merchant
            MPTotalOrderPrice=0
            for OrderNumberInList in OrderNumberList:
                Price = GetMerchantOrderPrice(OrderNumberInList)
                MPTotalOrderPrice += int(float(Price))
            #Get Price From Admin
            APTotalOrderPrice=0
            for OrderIDInList in OrderIDList:
                Price = GetTripsPriceInOrder(OrderIDInList)
                APTotalOrderPrice += int(float(Price))
            if MPTotalOrderPrice == APTotalOrderPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "Check MPTotalPrice : %s equal to APTotalPrice : %s" % (MPTotalOrderPrice,APTotalOrderPrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "Check MPTotalPrice : %s not equal to APTotalPrice : %s" % (MPTotalOrderPrice,APTotalOrderPrice)))
            #Wait for Cronjob 60s
            time.sleep(60)
            #Step 6: Get Bundle ID
            BundleID,status = GetBundleIDInOrder(OrderStatus[0])
            resultList.extend((FrameworkVar.ApiSpentTime, status, BundleID))
            #Step 7 : Get Bundle Total Price
            da_id = GetDAId(self.setting_config, "DA_Setting")
            TotalBundlePrice,status = GetBundleOrderTotalPrice(BundleID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TotalBundlePrice))
            #Step 8 : Assign Bundle Order to DA
            TripList = []
            for OrderIDInList in OrderIDList:
                tripid = GetAdminOrderTripsID(OrderIDInList)
                TripList.append(tripid)
            response, status = AssignBundleToDeliveryAgent(BundleID, da_id, TripList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            #Step 9 : Get Total Price from DA
            status_code, TotalDAPrice, status = GetDAReceiveStatus(BundleID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TotalDAPrice))
            #Step 10 : Check Merchant Price Was Changed or not
            if TotalBundlePrice != MPTotalOrderPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The Merchant Price Was Changed After Cronjob"))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The Merchant Price Was Not Changed After Cronjob"))
            #Step 11 : Check Bundle Price need to equal to DA
            if TotalBundlePrice == TotalDAPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The Bundle Price  : %s equal to DA Price : %s" % (TotalBundlePrice,TotalDAPrice)))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The Bundle Price : %s was not equal to DA Price : %s" % (TotalBundlePrice,TotalDAPrice)))
            #Step 12 : Check DA Price was not to equal to Merchant
            if MPTotalOrderPrice != TotalDAPrice:
                resultList.extend((FrameworkVar.ApiSpentTime, True, "The DA Price Was Changed After Cronjob"))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, "The DAPrice Was Not Changed After Cronjob"))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9184", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()  