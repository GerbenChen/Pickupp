#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
# import os
# root_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
import time
import unittest
import Method.CommonMethod as CommonMethod
import configparser
import Library.TestCaseHelper as TestCaseHelper

from typing import Final
from Core.ApiQuery import *
from Library.DBConnector import *
from Utility.testrail import *
from datetime import date
from Library.GlobalAdapter import *
from Library.Config import dumplogger
from Method.DeliveryAgentMethod import SearchMethod

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class DA_flow(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "DA Flow"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        GlobalAdapter.CommonVar.DeliveryAgentID = GetDAId(self.setting_config, "DA_Setting")
        self.test_case_time_start = time.time()


    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_DACheckJobAvailable(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Check Job Available
            status_code, job_response, status = GetAvailableJob(job_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, job_response))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5688", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckOrderAutoAccepted(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 3 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 4 : Add an order to Job
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Check Order Status "Contacting agent"
            order_response, status = MerchantPortal.GetAndCheckOrderStatus("ACCEPTED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_response))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5689", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckAvailableOrder(self):
        resultList = []

        # Step 1 : Check all available order in pool
        status_code, response, status = GetAllOrder()
        resultList.extend((FrameworkVar.ApiSpentTime, status, response))

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5690", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckOrderStatusChanged(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # #Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Add an order
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Get DA My Trips
            trip_id, status = GetDAMyTrips(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, trip_id))

            # Step 6 : Enroute
            enroute_response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, enroute_response))

            # Step 7 : Check Order Status Changed in DA
            status_code, response, status = GetDAMyOrderStatusByNumber("ENROUTE", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Check Order Status Changed in MP
            order_status, status = MerchantPortal.GetAndCheckOrderStatus("ENROUTE", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5691", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckMyOrderList(self):
        resultList = []

        # Step 1 : Check all order in My order page
        status, api_response = SearchMethod.SearchOrder("Full",1000)
        resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5692", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckMyJob(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Check my job
            status_code, response, status = GetDAMyJob(job_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5693", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DADropOrderOfJob(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Add an order
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Get DA My Trips
            trip_id, status = GetDAMyTrips(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, trip_id))

            # Step 6 : Enroute Order
            enroute_response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, enroute_response))

            # Step 7 : Drop off order
            response, status = DropOffProcess(trip_id)
            response, status = DropOff(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Check Order Status Change to "DELIVERED" in MP
            order_status, status = MerchantPortal.GetAndCheckOrderStatus("DELIVERED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5695", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DAOrderListAfterDrop(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Add an order to Job
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Get DA My Trips
            trip_id, status = GetDAMyTrips(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, trip_id))

            # Step 6 : Enroute order
            enroute_response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, enroute_response))

            # Step 7 : Drop off order
            response, status = DropOffProcess(trip_id)
            response, status = DropOff(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Check Order Status Changed to DELIVERED in DA
            status_code, order_status, status = DeliveryAgentAPI.GetAndCheckDAOrderStatus("DELIVERED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            # Step 9 : Check Finished Order Changed in DA Order List
            order_status, status = GetAndCheckDAFinishedOrder("DELIVERED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5696", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DAOrderDetailAfterDrop(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Add an order to Job
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Get DA My Trips
            trip_id, status = GetDAMyTrips(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, trip_id))

            # Step 6 : Enroute order
            enroute_response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, enroute_response))

            # Step 7 : Drop off order
            response, status = DropOffProcess(trip_id)
            response, status = DropOff(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Check Order Detail Status Changed in DA
            status_code, order_status, status = DeliveryAgentAPI.GetAndCheckDAOrderStatus("DELIVERED", order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5698", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckMiniPayOut(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Add an order
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Get DA My Trips
            trip_id, status = GetDAMyTrips(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, trip_id))

            # Step 6 : Enroute order
            enroute_response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, enroute_response))

            # Step 7 : Drop off order
            response, status = DropOffProcess(trip_id)
            response, status = DropOff(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Change Job status to finished
            job_number, status = JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
            resultList.extend((FrameworkVar.ApiSpentTime, status, job_number))

            # Step 9 : Check mini pay out after job finished
            da_id = GetDAId(self.setting_config, "DA_Setting")
            status_code, order_status, status = GetAndCheckMiniPayOut(da_id, job_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_status))

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5699", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckAPOrderDetail(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Add an order
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Get DA My Trips
            trip_id, status = GetDAMyTrips(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, trip_id))

            # Step 6 : Enroute
            response, status = Enroute(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 7 : Drop off order
            response, status = DropOffProcess(trip_id)
            response, status = DropOff(trip_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, response))

            # Step 8 : Change Job status to finished
            job_status, status = JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
            resultList.extend((FrameworkVar.ApiSpentTime, status, job_status))

            # Step 9 : Check order detail in admin portal after job finished
            status_code, order_response, status = JobAPI.GetAndCheckAPOrderDetail(job_id, order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_response))

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5700", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_DACheckJobHistory(self):
        resultList = []

        # Step 1 : Check Finished Job in History
        api_response, status = GetDAFinishedJob()
        resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5694", resultList, self.test_case_time_start)


if __name__ == '__main__':
    unittest.main()
