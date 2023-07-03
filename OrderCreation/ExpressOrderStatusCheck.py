#!/usr/bin/python
# -*- coding: UTF-8 -*-
from typing import Final
import sys
sys.path.append("./")
import unittest
import configparser
import Method.CommonMethod as CommonMethod
import Library.TestCaseHelper as TestCaseHelper

from Library.GlobalAdapter import *
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Library.Config import dumplogger

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr

class ExpressOrderStatusCheck(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ExpressOrders.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Express Order Status Check"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Standard_Order_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId, self.TestSuiteName)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_Express_SingleOrder(self):
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

            #Step 4 : Create an order
            status_code, order_id, status = OrderAPI.CreateExpressOrder(self.config, "Single")
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_id))

            #Step 5 : Check Order Status after Create Order
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("PENDING_SCHEDULE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id,da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 7 : Check OrderStatus after Assign
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("ACCEPTED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 8 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            #Step 9 : Check OrderStatus after Enroute
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("ENROUTE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 10 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 11 : Check OrderStatus after Dropoff
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("DROPPED_OFF", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11825", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_Express_CancelOrder(self):
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

            #Step 4 : Create an order
            status_code, order_id, status = OrderAPI.CreateExpressOrder(self.config, "Single")
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_id))

            #Step 5 : Check Order Status after Create Order
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("PENDING_SCHEDULE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id,da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 7 : Cancel Order
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Portal_Setting")
            response = AdminOrderAPI.CancelOrder(merchant_id, order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, bool(response), response))

            #Step 8 : Check Order Status Changed in AP
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("MERCHANT_CANCELLED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11826", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_Express_BackToWareHouse(self):
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

            #Step 4 : Create an order
            status_code, order_id, status = OrderAPI.CreateExpressOrder(self.config, "Single")
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_id))

            #Step 5 : Check Order Status after Create Order
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("PENDING_SCHEDULE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id,da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 7 : Check OrderStatus after Assign
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("ACCEPTED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 8 : Enroute
            response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            #Step 9 : Check OrderStatus after Enroute
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("ENROUTE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 10 : Back to Warehouse
            status_code, status = AdminPortal.BackToWareHouse(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))

            # Step 11 : Check order status after Back to Warehouse
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("UNABLE_TO_DELIVER", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            # Step 12 : Check trip status after UTD
            trip_status, status = AdminOrderAPI.GetAndCheckTripStatus("ENROUTE", trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, trip_status))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11827", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_Express_UnableToPickup(self):
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

            #Step 4 : Create an order
            status_code, order_id, status = OrderAPI.CreateExpressOrder(self.config, "Single")
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_id))

            #Step 5 : Check Order Status after Create Order
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("PENDING_SCHEDULE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id,da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 7 : Check OrderStatus after Assign
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("ACCEPTED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 8 : Unable To Pickup
            api_response, status = AdminPortal.UnableToPickup(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 9 : Check order status after Back to Warehouse
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("UNABLE_TO_PICKUP", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11828", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_Express_ItemNotReceived(self):
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

            #Step 4 : Create an order
            status_code, order_id, status = OrderAPI.CreateExpressOrder(self.config, "Single")
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_id))

            #Step 5 : Check Order Status after Create Order
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("PENDING_SCHEDULE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 6 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, trip_id, status = AssignToDeliveryAgent(order_id,da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 7 : Check OrderStatus after Assign
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("ACCEPTED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 8 : Item Not Received
            api_response, status = AdminOrderAPI.ItemNotReceived(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 9 : Check order status after Item Not Received
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("ITEM_NOT_RECEIVED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11829", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_Express_InboundOrder(self):
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

            #Step 4 : Create an order
            status_code, order_id, status = OrderAPI.CreateExpressOrder(self.config, "Single")
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_id))

            #Step 5 : Check Order Status after Create Order
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("CONTACTING_AGENT", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 6 : Inbound Order
            order_number = GetOrderNumber(order_id)
            warehouses_id = AdminWareHousesAPI.GetWareHousesID(self.setting_config['WareHouses']['name'])
            order_status, status = AdminWareHousesAPI.Inbound(warehouses_id, order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            #Step 7 : Check Order Status after Inbound
            order_status, status = AdminOrderAPI.GetAndCheckOrderStatus("PENDING_SCHEDULE", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "11834", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
