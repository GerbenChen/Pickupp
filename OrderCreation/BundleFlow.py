#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unittest
import sys
sys.path.append("./")
import configparser
import Method.CommonMethod as CommonMethod
import Library.TestCaseHelper as TestCaseHelper

from OrderCreation.CreateInBundleOrder import Inbundle
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
from Library.GlobalAdapter import *
from Library.Config import dumplogger

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class BundleFlow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/condition.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Bundle Flow"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
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
    def test_ErrorBundleNotValidReleaseTime(self):
        resultList = []

        try:
            #Step 1 : Get auth admin
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            #Step 2 : Create Bundle order
            order_list = Inbundle('4Hours')
            resultList.extend((FrameworkVar.ApiSpentTime, bool(order_list),order_list))

            #Step 3 : Get Bundle Information
            time.sleep(15)
            bundle_id, status = AdminPortal.GetBundleIdByOrder(self.setting_config, order_list[0])
            resultList.extend((FrameworkVar.ApiSpentTime, bool(bundle_id), bundle_id))

            #Step 4 : DA Accepted Bundle
            bundle_dict = BundleAPI.GetBundleInformation(self.setting_config, bundle_id)
            bundle_response, status = DeliveryAgentAPI.AcceptedBundleOrder(self.setting_config, bundle_id, bundle_dict)
            if bundle_response['error_type'] == '026023':
                status = True
            resultList.extend((FrameworkVar.ApiSpentTime, status, bundle_id))
        except Exception as err:
            dumplogger.exception(err)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9603", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_ErrorWrongBundleStatus(self):
        resultList = []

        try:
            #Step 1 : Get auth admin
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            #Step 2 : Create Bundle order
            order_list = Inbundle('4Hours')
            resultList.extend((FrameworkVar.ApiSpentTime, bool(order_list),order_list))

            #Step 3 : Get Bundle Information
            time.sleep(15)
            bundle_id, status = AdminPortal.GetBundleIdByOrder(self.setting_config, order_list[0])
            resultList.extend((FrameworkVar.ApiSpentTime, bool(bundle_id), bundle_id))

            #Step 4 : DA Accepted Bundle
            bundle_dict = BundleAPI.GetBundleInformation(self.setting_config, bundle_id)
            bundle_response, status = DeliveryAgentAPI.AcceptedBundleOrder(self.setting_config, bundle_id, bundle_dict)
            if bundle_response['error_type'] == '026022':
                status = True
            resultList.extend((FrameworkVar.ApiSpentTime, status, bundle_id))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9604", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_ErrorBundleChanged(self):
        resultList = []

        try:
            #Step 1 : Get auth admin
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            #Step 2 : Create Bundle order
            order_list = Inbundle('4Hours')
            resultList.extend((FrameworkVar.ApiSpentTime, bool(order_list),order_list))

            #Step 3 : Get Bundle Information
            time.sleep(15)
            bundle_id, status = AdminPortal.GetBundleIdByOrder(self.setting_config, order_list[0])
            resultList.extend((FrameworkVar.ApiSpentTime, bool(bundle_id), bundle_id))

            # Step 4 : Change Bundle Status
            bundle_dict = BundleAPI.GetBundleInformation(self.setting_config, bundle_id)
            if bundle_dict['status'] != "READY" or bundle_dict['status'] != "CONTACTING_AGENT":
                bundle_dict = BundleAPI.ChangeBundleStatus(self.setting_config, bundle_id, bundle_dict)
            resultList.extend((FrameworkVar.ApiSpentTime, bool(bundle_dict), bundle_id))

            #Step 5 : DA Accepted Bundle
            bundle_response, status = DeliveryAgentAPI.AcceptedBundleOrder(self.setting_config, bundle_id,bundle_dict)
            if bundle_response['error_type'] == '026024':
                status = True
            resultList.extend((FrameworkVar.ApiSpentTime, status, bundle_id))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9605", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_JobAddBundleOrder(self):
        resultList = []

        timedict = CommonMethod.GetJobSettingTime()

        try:
            #Step 1 : Get auth admin
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            #Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            #Step 4 : Create Bundle order
            order_list = Inbundle('4Hours')
            resultList.extend((FrameworkVar.ApiSpentTime, bool(order_list),order_list))

            #Step 5 : Add Bundle order to Job
            order_number = GetOrderNumber(order_list[0])
            order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_response))

            #Step 6 : Check order status should not InBundle
            bundle_id, status = AdminPortal.GetBundleIdByOrder(self.setting_config, order_list[0])
            if bundle_id:
                status = False
            else:
                status = True
            resultList.extend((FrameworkVar.ApiSpentTime, status, bundle_id))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "6455", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_AddJobOrderToBundle(self):
        totalstatus = True
        resultList = []

        timedict = CommonMethod.GetJobSettingTime()

        try:
            #Step 1 : Get auth admin
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            #Step 2 : Create Bundle order
            order_list = Inbundle('4Hours')
            resultList.extend((FrameworkVar.ApiSpentTime, bool(order_list),order_list))

            #Step 3 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 4 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            #Step 5 : create single order
            api_response, order_id, status = CreateOrder(self.config,'4Hours',totalstatus)
            single_order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 6 : Add single order to Job
            order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, single_order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_response))

            #Step 7 : Add Job order to bundle, but cannot bundle it
            #is need time to wait order into bundle
            time.sleep(15)
            bundle_id, status = AdminPortal.GetBundleIdByOrder(self.setting_config, order_list[0])
            status_code, bundle_response, status = BundleAPI.AddOrderToBundle(self.setting_config,bundle_id,single_order_number)
            if status_code == 400:
                status = True
            else:
                status = False
            resultList.extend((FrameworkVar.ApiSpentTime, status, bundle_response))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "6456", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()  
