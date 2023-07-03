#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
from Method.OrderMethod import *
from typing import Final
import unittest
from Library.GlobalAdapter import *
from Method.CommonMethod import *
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
import configparser
from Library.Config import dumplogger
import Library.TestCaseHelper as TestCaseHelper
import Method.CommonMethod as CommonMethod

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class OrderStatusCheck(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/condition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Single Order Flow"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        CleanTrips(320)
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_SameDayPendingScheduleStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDayHomeDelivery')
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Enroute
            status_code, response, status = Enroute(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 7 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Dropoff Process
            status_code, response, status = DropOffProcess(TripID,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Dropoff
            status_code, response, status = DropOff(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 10 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SameDayMerchantCancelStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 4 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDayHomeDelivery')
            # Step 5 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 7 : MP Cancel Order
            response, status = MerchantPortal.CancelOrder(OrderID,"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 8 : Check OrderStatus after MP Cancel Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"MERCHANT_CANCELLED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SameDayUnableToPickupStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDayHomeDelivery')
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Unable To Pickup
            status_code, status = UnableToPickup(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 7 : Check OrderStatus after UTP
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_PICKUP")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SameDayBackToWarehouseStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 4 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDayHomeDelivery')
            # Step 5 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 6 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 7 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 8 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 9 : Enroute
            status_code, response, status = Enroute(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 10 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 11 : Back to Warehouse
            status_code, status =BackToWH(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 12 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_DELIVER")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 13 : Check trip status after UTD 
            status_code, status = PoolTripStatus(TripID)
            status = CompareWithValue(OrderStatus,"BACK_TO_WAREHOUSE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_NextDayPendingScheduleStandard(self):
        totalstatus = True
        resultList = []
        # Step 1 : Get_auth_portal
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
        # Step 2 : Get_auth_admin
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
        # Step 3 : Get_auth
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
        # Step 4 : Create an order
        status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDayHomeDelivery')
        # Step 5 : PUT Order To Warehouse
        response, status = PUTOrderToWH(OrderID)
        # Step 6 : Check OrderStatus after Create Order
        OrderStatus = GetAdminOrderStatus(OrderID)
        status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        # Step 7 : Assign to DA
        da_id = GetDAId(self.setting_config, "DA_Setting")
        status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
        # Step 8 : Check OrderStatus after Assign
        OrderStatus = GetAdminOrderStatus(OrderID)
        status = CompareWithValue(OrderStatus,"ACCEPTED")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        # Step 9 : Enroute
        status_code, response, status = Enroute(TripID, OrderID, totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        # Step 10 : Check OrderStatus after Enroute
        OrderStatus = GetAdminOrderStatus(OrderID)
        status = CompareWithValue(OrderStatus,"ENROUTE")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        # Step 11 : Dropoff Process
        status_code, response, status = DropOffProcess(TripID,totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        # Step 12 : Dropoff
        status_code, response, status = DropOff(TripID, OrderID, totalstatus)
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))
        # Step 13 : Check OrderStatus after Dropoff
        OrderStatus = GetAdminOrderStatus(OrderID)
        status = CompareWithValue(OrderStatus,"DROPPED_OFF")
        resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_NextDayMerchantCancelStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDayHomeDelivery')
            # Step 2 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 3 : MP Cancel Order
            response, status = MerchantPortal.CancelOrder(OrderID,"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 4 : Check OrderStatus after MP Cancel Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"MERCHANT_CANCELLED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_NextDayUnableToPickupStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDayHomeDelivery')
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Unable To Pickup
            status_code, status = UnableToPickup(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 7 : Check OrderStatus after UTP
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_PICKUP")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_NextDayBackToWarehouseStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDayHomeDelivery')
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Enroute
            status_code, response, status = Enroute(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 7 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Back to Warehouse
            status_code, status =BackToWH(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 9 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_DELIVER")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Check trip status after UTD 
            status_code, status = PoolTripStatus(TripID)
            status = CompareWithValue(OrderStatus,"BACK_TO_WAREHOUSE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfSameDayPendingScheduleStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 4 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDaySelfPickup',"SelfPickUp")
            # Step 5 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 6 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 7 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 8 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 9 : Enroute
            status_code, response, status = Enroute(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 10 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 11 : Dropoff Process
            status_code, response, status = DropOffProcess(TripID,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 12 : Dropoff
            status_code, response, status = DropOff(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 13 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfSameDayMerchantCancelStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDaySelfPickup',"SelfPickUp")
            # Step 2 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 3 : MP Cancel Order
            response, status = MerchantPortal.CancelOrder(OrderID,"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 4 : Check OrderStatus after MP Cancel Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"MERCHANT_CANCELLED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfSameDayUnableToPickupStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDaySelfPickup',"SelfPickUp")
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Unable To Pickup
            status_code, status = UnableToPickup(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 7 : Check OrderStatus after UTP
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_PICKUP")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfSameDayBackToWarehouseStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'SameDaySelfPickup',"SelfPickUp")
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Enroute
            status_code, response, status = Enroute(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 7 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Back to Warehouse
            status_code, status =BackToWH(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 9 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_DELIVER")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Check trip status after UTD 
            status_code, status = PoolTripStatus(TripID)
            status = CompareWithValue(OrderStatus,"BACK_TO_WAREHOUSE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfNextDayPendingScheduleStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDaySelfPickup',"SelfPickUp")
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Enroute
            status_code, response, status = Enroute(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 7 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Dropoff Process
            status_code, response, status = DropOffProcess(TripID,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 9 : Dropoff
            status_code, response, status = DropOff(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 10 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfNextDayMerchantCancelStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDaySelfPickup',"SelfPickUp")
            # Step 2 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 3 : MP Cancel Order
            response, status = MerchantPortal.CancelOrder(OrderID,"CREATED_BY_MISTAKE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 4 : Check OrderStatus after MP Cancel Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"MERCHANT_CANCELLED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfNextDayUnableToPickupStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDaySelfPickup',"SelfPickUp")
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 4 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 5 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 6 : Unable To Pickup
            status_code, status = UnableToPickup(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 7 : Check OrderStatus after UTP
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_PICKUP")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


    @TestCaseHelper.TestTimed
    def test_SelfNextDayBackToWarehouseStandard(self):
        totalstatus = True
        resultList = []
        try:
            # Step 1 : Create an order
            status_code, OrderID, status = MerchantPortal.CreateStandardOrder(self.config,'NextDaySelfPickup',"SelfPickUp")
            # Step 2 : PUT Order To Warehouse
            response, status = PUTOrderToWH(OrderID)
            # Step 3 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"PENDING_SCHEDULE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 5 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, TripID, status = AssignToDeliveryAgent(OrderID,da_id,totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, TripID))
            # Step 6 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 7 : Enroute
            status_code, response, status = Enroute(TripID, OrderID, totalstatus)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 8 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 9 : Back to Warehouse
            status_code, status =BackToWH(TripID)
            resultList.extend((FrameworkVar.ApiSpentTime, status, status_code))
            # Step 10 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(OrderID)
            status = CompareWithValue(OrderStatus,"UNABLE_TO_DELIVER")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 11 : Check trip status after UTD 
            status_code, status = PoolTripStatus(TripID)
            status = CompareWithValue(OrderStatus,"BACK_TO_WAREHOUSE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
        except Exception as err:
            dumplogger.exception(err)
        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()  