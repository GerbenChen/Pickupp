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

class Single_Order_Flow(unittest.TestCase):
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
            status_code, statusList, status = CreateOrder(self.config,'4Hours',totalstatus)
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
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "91", resultList, self.test_case_time_start)

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
            status_code, statusList, status = CreateOrder(self.config,'Exchange',totalstatus)
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
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "89", resultList, self.test_case_time_start)

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
            status_code, statusList, status = CreateOrder(self.config,'Express',totalstatus)
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
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "90", resultList, self.test_case_time_start)

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
            status_code, statusList, status = CreateOrder(self.config,'NextDay',totalstatus)
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
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "92", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderFlowSameDay(self):
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
            status_code, statusList, status = CreateOrder(self.config,'SameDay',totalstatus)
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
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "93", resultList, self.test_case_time_start)

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
            status_code, statusList, status = CreateOrder(self.config,'Collection',totalstatus)
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
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "88", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_OrderFlowSelfPickUppNextDay(self):
        totalstatus = True
        resultList = []
        try:
            #Conneted and SetUp Database uat = d360ecd2-5b6f-41c7-aec4-f2323a1ceba3 dev = bbf5acba-fe6a-4660-9091-08915b26b813
            connection = connect_postgresql(GlobalAdapter.FrameworkVar.Environment)
            #Step 1 : Modify Warehouse Created_at time
            command = """update alfred."Lockers" set created_at = '%s 08:00:12.519 +0800' where id ='%s'""" % (str(date.today()),self.config['SelfPickup_so_id'][GlobalAdapter.FrameworkVar.Environment])
            execute_postgresql(connection,command)
            command = """select created_at from alfred."Lockers" where id = '%s'""" % self.config['SelfPickup_so_id'][GlobalAdapter.FrameworkVar.Environment]
            response = execute_postgresql_fetchone(connection,command)
            if str(date.today()) in str(response[0]):
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,str(response[0])))
            #Step 2 : Modify Warehouse Updated_at time
            command = """update alfred."Lockers" set updated_at = '%s 23:00:12.519 +0800' where id ='%s'""" % (str(date.today()),self.config['SelfPickup_so_id'][GlobalAdapter.FrameworkVar.Environment])
            execute_postgresql(connection,command)
            command = """select updated_at from alfred."Lockers" where id = '%s'""" % self.config['SelfPickup_so_id'][GlobalAdapter.FrameworkVar.Environment]
            response = execute_postgresql_fetchone(connection,command)
            if str(date.today()) in str(response[0]):
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status,str(response[0])))
            # Step 3 : Get Merchant Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.MerchantPortalAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))
            # Step 4 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))
            # Step 5 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((FrameworkVar.ApiSpentTime, have_auth, check_result))
            # Step 6 : Create an order
            status_code, statusList, status = CreateOrder(self.config,'Self pick up via Next day',totalstatus,minimum=True)
            if statusList[1] == self.config["condition_Self pick up via Next day"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime, True, statusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime, False, statusList))
            # Step 7 : Check OrderStatus after Create Order
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 8 : Assign to DA
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status = AssignToDeliveryAgent(statusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
            # Step 9 : Check OrderStatus after Assign
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 10 : Enroute
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 11 : Check OrderStatus after Enroute
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 12 : Dropoff Process
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 13 : Dropoff
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 14 : Check OrderStatus after Dropoff
            OrderStatus = GetAdminOrderStatus(statusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "97", resultList, self.test_case_time_start)
    
    @TestCaseHelper.TestTimed
    def test_OrderFlowFirstLegAndLastLeg(self):
        totalstatus = True
        resultList = []
        try:
            # Check How Many days is Workday
            Getdays = CommonMethod.CheckHowManyDaysIsWorkday()
            # Step 1 : Create an order for FirstLeg
            status_code, FirstLegStatusList, status = ScheduleBulkCollection(self.config,'FirstLeg',totalstatus,Getdays)
            if FirstLegStatusList[1] == self.config["condition_FirstLeg"]["checkserviceofferingID"]:
                resultList.extend((FrameworkVar.ApiSpentTime,True, FirstLegStatusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime,False, FirstLegStatusList))
            # Step 2 : Check OrderStatus after Create Order FirstLeg
            OrderStatus = GetAdminOrderStatus(FirstLegStatusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime,status, OrderStatus))
            # Step 3 : Admin Create Order for LastLeg
            status_code, LastLegStatusList, status = AdminCreateOrder(self.config,'LastLeg',totalstatus)
            if LastLegStatusList[1] == self.config["LastLeg_so_id"][GlobalAdapter.FrameworkVar.Environment]:
                resultList.extend((FrameworkVar.ApiSpentTime,True, LastLegStatusList))
            else:
                resultList.extend((FrameworkVar.ApiSpentTime,False, LastLegStatusList))
            # Step 4 : Check OrderStatus after Create Order LastLeg
            OrderStatus = GetAdminOrderStatus(LastLegStatusList[0])
            status = CompareWithValue(OrderStatus,["PENDING","CONTACTING_AGENT"])
            resultList.extend((FrameworkVar.ApiSpentTime,status, OrderStatus))
            # Step 5 : Assign DA (FirstLeg)
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, tripid, status  = AssignToDeliveryAgent(FirstLegStatusList[0], da_id)
            resultList.extend((FrameworkVar.ApiSpentTime,status, status_code))
            # Step 6 : Check OrderStatus after Assign (FirstLeg)
            OrderStatus = GetAdminOrderStatus(FirstLegStatusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime, status, OrderStatus))
            # Step 7 : Enroute (FirstLeg)
            response, status = Enroute(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))
            # Step 8 : Check OrderStatus after Enroute (FirstLeg)
            OrderStatus = GetAdminOrderStatus(FirstLegStatusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime,status, OrderStatus))
            # Step 9 : Dropoff Process (FirstLeg)
            response, status = DropOffProcess(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime,status, response))
            # Step 10 : Dropoff (FirstLeg)
            response, status = DropOff(tripid)
            resultList.extend((FrameworkVar.ApiSpentTime,status, response))
            # Step 141 : Check OrderStatus after Dropoff (FirstLeg)
            OrderStatus = GetAdminOrderStatus(FirstLegStatusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime,status, OrderStatus))
            # Step 12 : Assign DA (LastLeg)
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_response, LastLegTripid, status = AssignToDeliveryAgent(LastLegStatusList[0],da_id)
            resultList.extend((FrameworkVar.ApiSpentTime,status, api_response))
            # Step 13 : Check OrderStatus after Assign (LastLeg)
            OrderStatus = GetAdminOrderStatus(LastLegStatusList[0])
            status = CompareWithValue(OrderStatus,"ACCEPTED")
            resultList.extend((FrameworkVar.ApiSpentTime,status, OrderStatus))
            # Step 14 : Enroute (LastLeg)
            response, status = Enroute(LastLegTripid)
            resultList.extend((FrameworkVar.ApiSpentTime,status, response))
            # Step 15 : Check OrderStatus after Enroute (LastLeg)
            OrderStatus = GetAdminOrderStatus(LastLegStatusList[0])
            status = CompareWithValue(OrderStatus,"ENROUTE")
            resultList.extend((FrameworkVar.ApiSpentTime,status, OrderStatus))
            # Step 16 : Dropoff Process (FirstLeg)
            response, status = DropOffProcess(LastLegTripid)
            resultList.extend((FrameworkVar.ApiSpentTime,status, response))
            # Step 17 : Dropoff (FirstLeg)
            response, status = DropOff(LastLegTripid)
            resultList.extend((FrameworkVar.ApiSpentTime,status, response))
            # Step 18 : Check OrderStatus after Dropoff (LastLeg)
            OrderStatus = GetAdminOrderStatus(LastLegStatusList[0])
            status = CompareWithValue(OrderStatus,"DROPPED_OFF")
            resultList.extend((FrameworkVar.ApiSpentTime,status, OrderStatus))

        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "12014", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()  
