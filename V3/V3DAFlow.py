#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
import unittest
import configparser
import Method.CommonMethod as CommonMethod
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


class V3_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "V3 Project"
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
    def test_CheckPHBannerSetting(self):
        resultList = []

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            #Step 3 : Check PH Banner Setting
            api_res, status = V3API.GetAndCheckPHBanners(self)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_res))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9918", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckPHAppMessageSetting(self):
        resultList = []

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            #Step 3 : Check PH App Message Setting
            api_res,status = V3API.CheckPHAPPMessageSetting(self)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_res))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9919", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckAvailableOrder(self):
        totalstatus = ""
        resultList = []

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            #Step 3 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 4 : Check Order Available in P2P page
            order_number = GetOrderNumber(order_id)
            api_res, status = V3API.GetAndCheckNewAvailableOrder(order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_res))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9920", resultList, self.test_case_time_start)

    # @TestCaseHelper.TestTimed
    # def test_CheckMyLastLegTripPage(self):
    #     totalstatus = ""
    #     resultList = []
    #
    #     try:
    #         # Step 1 : Get Admin Auth Key
    #         have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
    #         resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))
    #
    #         # Step 2 : Get DA Auth Key
    #         have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
    #         resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))
    #
    #         #Step 3 : Create an order
    #         api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
    #         order_number = GetOrderNumber(order_id)
    #         resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))
    #
    #         #Step 4 : Check Order in My LastLeg Trip Page
    #         api_res, status = V3API.GetAndCheckMyLastLegTripPage(order_number)
    #         resultList.extend((FrameworkVar.ApiSpentTime, status, api_res))
    #
    #     except Exception as err:
    #         dumplogger.exception(err)
    #
    #
    #     #Final : Update result to testrail
    #     CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9921", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckMyLastLegJob(self):
        totalstatus = ""
        resultList = []
        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            #Step 3 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            #Step 4 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            #Step 5 : Check Order in My LastLeg Trip Page
            api_res, status = V3API.GetAndCheckMyLastLegJob(job_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_res))


            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
        except Exception as err:
            dumplogger.exception(err)
            JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9922", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckDARegions(self):
        totalstatus = ""
        resultList = []

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            #Step 4 : Check DA Regions
            da_id = GetDAId(self.setting_config, "DA_Setting")
            api_res, status = V3API.GetAndCheckDARegions(da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_res))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9923", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_CheckMyLastLegHistories(self):
        totalstatus = ""
        resultList = []

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Get DA Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.DAAuth)
            resultList.extend((AuthApiSpentTime.DAAuth, have_auth, check_result))

            #Step 4 : Get And Check My LastLeg Histories
            api_res, status = V3API.GetAndCheckMyLastLegHistories(self)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_res))

        except Exception as err:
            dumplogger.exception(err)

        #Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9924", resultList, self.test_case_time_start)

if __name__ == '__main__':
    unittest.main()
