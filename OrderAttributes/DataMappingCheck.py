#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
import unittest
import configparser
import Method.DataBaseMethod as DataBaseMethod
import Library.TestCaseHelper as TestCaseHelper

from typing import Final
from Library.Config import dumplogger
from Utility.testrail import*
from Core.ApiQuery import*
from Library.GlobalAdapter import *

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class DataMappingCheck(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Order Attributes - Data Sync Check"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.CommonVar.DAUrl = self.setting_config['DA_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_CheckBBOrderSyncTOOldOrder(self):
        resultList = []
        check_status = False
        try:
            # Step 1 : Check OldOrder data have sync with Orders and order
            # OldOrders table willsync
            # when:
            # 1. order created
            # 2. timeline updated
            sql_command = """select newo.id,o.status,newo.status,newo.trip_status,newo.parcel_status from "backbone"."OldOrders" o
                                join "backbone"."Orders" newo on newo.id = o.id
                                join "backbone"."OrderAttributes" oa on oa.order_id = o.id
                                join "backbone"."OrderProperties" op on op.order_id = o.id
                                join "backbone"."Waypoints" w on w.order_id = o.id
                                where newo.created_at BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()
                                group by newo.id,o.status ,newo.status,newo.trip_status,newo.parcel_status"""
            order_dict = DataBaseMethod.GetBackBoneOrderData(sql_command)
            if len(order_dict) > 1:
                check_status = True
                data_check_result = "Have order sync between backbone.Orders and backbone.OldOrders in 24 HOURS"
            elif len(order_dict) == 1:
                check_status = "Retest"
                data_check_result = "Question!! only one order sync between backbone.Orders and backbone.OldOrders in 24 HOURS"
            else:
                check_status = False
                data_check_result = "NO!!!!!! order sync between backbone.Orders and backbone.OldOrders in 24 HOURS"
            resultList.extend(("0.0", check_status, data_check_result))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13176", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckBBOrderStatusSync_OrderCreated(self):
        resultList = []

        try:
            # Step 1 : Check OldOrder data have sync with Orders and order
            # OldOrders table willsync
            # when:
            # 1. order created
            # 2. timeline updated

            # Step 1 : Create order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config,'four_hours',"CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Check OldOrder data have sync with Orders and order
            sql_command = """select newo.id,o.status,newo.status,newo.trip_status,newo.parcel_status from "backbone"."OldOrders" o
                                join "backbone"."Orders" newo on newo.id = o.id
                                join "backbone"."OrderAttributes" oa on oa.order_id = o.id
                                join "backbone"."OrderProperties" op on op.order_id = o.id
                                join "backbone"."Waypoints" w on w.order_id = o.id
                                where newo.created_at BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()
                                and newo.id = '%s'
                                group by newo.id,o.status ,newo.status,newo.trip_status,newo.parcel_status""" % str(order_id)
            order_dict = DataBaseMethod.GetBackBoneOrderData(sql_command)
            if order_dict:
                check_status = True
                data_check_result = "Check result : %s" % str(order_dict)
            else:
                check_status = False
                data_check_result = "NO!!!!!! order sync between backbone.Orders and backbone.OldOrders by order_id : %s" % str(order_id)
            resultList.extend(("0.0", check_status, data_check_result))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13177", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckBBOrderStatusSync_TimelineUpdated(self):
        resultList = []

        try:
            # Step 1 : Check OldOrder data have sync with Orders and order
            # OldOrders table willsync
            # when:
            # 1. order created
            # 2. timeline updated

            # Step 1 : Create order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config,'four_hours',"CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Get BackBone Order Data with order_id
            sql_command = """select newo.id,o.status,newo.status,newo.trip_status,newo.parcel_status from "backbone"."OldOrders" o
                                join "backbone"."Orders" newo on newo.id = o.id 
                                join "backbone"."OrderAttributes" oa on oa.order_id = o.id 
                                join "backbone"."OrderProperties" op on op.order_id = o.id 
                                join "backbone"."Waypoints" w on w.order_id = o.id 
                                where newo.created_at BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()
                                and newo.id = '%s'
                                group by newo.id,o.status ,newo.status,newo.trip_status,newo.parcel_status""" % str(order_id)
            first_order_dict = DataBaseMethod.GetBackBoneOrderData(sql_command)
            if first_order_dict:
                check_status = True
                data_check_result = "Check result : %s" % str(first_order_dict)
            else:
                check_status = False
                data_check_result = "NO!!!!!! order sync between backbone.Orders and backbone.OldOrders by order_id : %s" % str(order_id)
            resultList.extend(("0.0", check_status, data_check_result))

            # Step 3 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(order_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 4 : Get BackBone Order Data with order_id after timeline updated
            sql_command = """select newo.id,o.status,newo.status,newo.trip_status,newo.parcel_status from "backbone"."OldOrders" o
                                join "backbone"."Orders" newo on newo.id = o.id 
                                join "backbone"."OrderAttributes" oa on oa.order_id = o.id 
                                join "backbone"."OrderProperties" op on op.order_id = o.id 
                                join "backbone"."Waypoints" w on w.order_id = o.id 
                                where newo.created_at BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()
                                and newo.id = '%s'
                                group by newo.id,o.status ,newo.status,newo.trip_status,newo.parcel_status""" % str(order_id)
            second_order_dict = DataBaseMethod.GetBackBoneOrderData(sql_command)
            if second_order_dict:
                check_status = True
                data_check_result = "Check result : %s" % str(second_order_dict)
            else:
                check_status = False
                data_check_result = "NO!!!!!! order sync between backbone.Orders and backbone.OldOrders by order_id : %s" % str(order_id)
            resultList.extend(("0.0", check_status, data_check_result))

            # Step 5 : Check order status change after timeline updated
            check_result = CommonMethod.CompairTwoDict(first_order_dict,second_order_dict)
            if type(check_result) == bool:
                check_status = False
                message = "Order status not changed after timeline updated"
            else:
                check_status = True
                message = "Order status changed after timeline updated"
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, message))

            # Step 6 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 7 : Check order status change after timeline updated - Enroute
            sql_command = """select newo.id,o.status,newo.status,newo.trip_status,newo.parcel_status from "backbone"."OldOrders" o
                                join "backbone"."Orders" newo on newo.id = o.id 
                                join "backbone"."OrderAttributes" oa on oa.order_id = o.id 
                                join "backbone"."OrderProperties" op on op.order_id = o.id 
                                join "backbone"."Waypoints" w on w.order_id = o.id 
                                where newo.created_at BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()
                                and newo.id = '%s'
                                group by newo.id,o.status ,newo.status,newo.trip_status,newo.parcel_status""" % str(order_id)
            third_order_dict = DataBaseMethod.GetBackBoneOrderData(sql_command)
            check_result = CommonMethod.CompairTwoDict(second_order_dict,third_order_dict)
            if type(check_result) == bool:
                check_status = False
                message = "Order status not changed after timeline updated"
            else:
                check_status = True
                message = "Order status changed after timeline updated"
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, message))

            # Step 8 : Dropoff Process
            response, status = DropOffProcess(tripid)
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 9 : Check order status change after timeline updated - Dropoff Process
            sql_command = """select newo.id,o.status,newo.status,newo.trip_status,newo.parcel_status from "backbone"."OldOrders" o
                                join "backbone"."Orders" newo on newo.id = o.id 
                                join "backbone"."OrderAttributes" oa on oa.order_id = o.id 
                                join "backbone"."OrderProperties" op on op.order_id = o.id 
                                join "backbone"."Waypoints" w on w.order_id = o.id 
                                where newo.created_at BETWEEN NOW() - INTERVAL '24 HOURS' AND NOW()
                                and newo.id = '%s'
                                group by newo.id,o.status ,newo.status,newo.trip_status,newo.parcel_status""" % str(order_id)
            fourth_order_dict = DataBaseMethod.GetBackBoneOrderData(sql_command)
            check_result = CommonMethod.CompairTwoDict(third_order_dict,fourth_order_dict)
            if type(check_result) == bool:
                check_status = False
                message = "Order status not changed after timeline updated"
            else:
                check_status = True
                message = "Order status changed after timeline updated"
            resultList.extend((FrameworkVar.ApiSpentTime, check_status, message))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "13178", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()
