#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import Final
import sys
sys.path.append("./")
import unittest
import configparser
import random
import Library.TestCaseHelper as TestCaseHelper
import Method.CommonMethod as CommonMethod

from Core.ApiQuery import *
from Library.Config import dumplogger
from Library.GlobalAdapter import *
from Method.OrderMethod import CompareWithValue
from Utility.testrail import *

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class Order_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/condition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Multi Parcel Order Flow"
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

    def randomWLH(self):
        '''
            Refer to https://hk.pickupp.io/en/faq SPEC
        '''
        total = 149
        weight = random.randrange(1, 20)
        width = random.randrange(1, total - 2)
        lengthtmp = total - width
        length = random.randrange(1, lengthtmp - 1)
        heighttmp = lengthtmp - length
        height = random.randrange(1, heighttmp)
        return width, length, height, weight

    @TestCaseHelper.TestTimed
    def test_OrderFlow4Hours(self):
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
            # Step 4 : Create an order
            width, length, height, weight = self.randomWLH()
            status_code, statusList, status = CreateOrder(self.config, '4Hours', totalstatus)
            if statusList[1] == self.config["condition_4Hours"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime, True, statusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, statusList))
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

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5685", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderFlowExchange(self):
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
            # Step 4 : Create an order
            width, length, height, weight = self.randomWLH()
            status_code, statusList, status = CreateOrder(self.config, 'Exchange', totalstatus)
            if statusList[1] == self.config["condition_Exchange"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime, True, statusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, statusList))
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
            OrderStatus = GetAdminOrderStatus(statusList[0],True)
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5683", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderFlowExpress(self):
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
            # Step 4 : Create an order
            width, length, height, weight = self.randomWLH()
            status_code, statusList, status = CreateOrder(self.config, 'Express', totalstatus)
            if statusList[1] == self.config["condition_Express"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime, True, statusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, statusList))
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

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5684", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderFlowNextDay(self):
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
            # Step 4 : Create an order
            width, length, height, weight = self.randomWLH()
            status_code, statusList, status = CreateOrder(self.config, 'NextDay', totalstatus)
            if statusList[1] == self.config["condition_NextDay"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime, True, statusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, statusList))
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

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5686", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderFlowSameDay(self):
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
            width, length, height, weight = self.randomWLH()
            status_code, statusList, status = CreateOrder(self.config, 'SameDay', totalstatus)
            if statusList[1] == self.config["condition_SameDay"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime, True, statusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, statusList))
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

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5687", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderFlowCollection(self):
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
            width, length, height, weight = self.randomWLH()
            status_code, statusList, status = CreateOrder(self.config, 'Collection', totalstatus)
            if statusList[1] == self.config["condition_Collection"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime, True, statusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, statusList))
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

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5682", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
