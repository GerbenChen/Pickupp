#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

sys.path.append("./")
import unittest
import configparser
import Method.CommonMethod as CommonMethod
import Method.OrderMethod as OrderMethod
import Library.GlobalAdapter as GlobalAdapter
import Library.TestCaseHelper as TestCaseHelper

from Core.ApiQuery import *
from Utility.testrail import *
from Library.Config import dumplogger
from Library.GlobalAdapter import *

class Newconfigparser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class Job_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/ServiceOfferingConfig.ini')
        self.admin_setting_config = configparser.ConfigParser()
        self.admin_setting_config.read('./Config/adminjobscondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/DAflow_account_setting.ini')
        self.TestSuiteName = "Job Flow"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.CommonVar.DeliveryAgentID = self.setting_config['DA_Setting']['email']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        self.test_case_time_start = time.time()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId, self.TestSuiteName)
        CommonMethod.CleanTrips(GlobalAdapter.CommonVar.DeliveryAgentID)
        CommonMethod.DeInitialAPIVar()

    @TestCaseHelper.TestTimed
    def test_JobAddOrderInTime(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Get auth admin
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))


            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Add an order
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 6 : Check Order status in Job
            release_time, status = OrderMethod.CheckOrderReleaseTime(order_response, order_number, True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, release_time))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
        except Exception as err:
            dumplogger.exception(err)
            JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5680", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_JobAddOrderOutOfTime(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))


            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Add an order
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 6 : Check Order status in Job
            release_time, status = OrderMethod.CheckOrderReleaseTime(order_response, order_number, True)
            resultList.extend((FrameworkVar.ApiSpentTime, status, release_time))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "5681", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_AddSOOrderToJob(self):
        resultList = []
        merchant_id = ""
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

            # Step 3 : Get merchant id
            merchant_id = AdminMerchantAPI.GetMerchantId(self.setting_config, "Merchant_SO_Setting")
            resultList.extend((FrameworkVar.ApiSpentTime, bool(merchant_id), merchant_id))

            # Step 4 : Create an order
            api_response, order_id, status = OrderAPI.CreateOrder(self.config, 'four_hours', "CreditCard")
            order_number = GetOrderNumber(order_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 5 : Add an order to Job
            api_response, order_response, status = JobAPI.AddOrderToJobs(self.setting_config, job_id, order_number, self.admin_setting_config['Order_condition']['assign_price'])
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 6 : Check Order Status "ACCEPTED"
            order_response, status = MerchantPortal.GetAndCheckOrderStatus("ACCEPTED", order_number)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_response))

            # Step 7 : Check Order form Job
            status_code, order_response, status = GetDAMyJob(job_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, order_response))

            JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")

        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")
        finally:
            if merchant_id:
                # back to normal
                merchants_setting = CommonMethod.GetJsonData("./Config/merchants_default_setting", "Default")
                AdminMerchantAPI.UpdateMerchantSetting(self.setting_config, merchant_id, merchants_setting)

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9538", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_ErrorNotAbleToFinishJob(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Finish Job and check response error_message will be 028002
            response, status = JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
            check_result, status = OrderMethod.GetAndCheckJobReturnMessage(response, status, "028002")
            resultList.extend((FrameworkVar.ApiSpentTime, status, check_result))
        except TypeError as err:
            dumplogger.exception(err)
        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9586", resultList, self.test_case_time_start)

    @TestCaseHelper.TestTimed
    def test_ErrorNotAbleToCancelJob(self):
        resultList = []
        job_id = ""

        timedict = CommonMethod.GetJobSettingTime()

        try:
            # Step 1 : Get Admin Auth Key
            have_auth, check_result = CommonMethod.Auth.CheckAuthSuccessfully(GlobalAdapter.AuthVar.AdminAuth)
            resultList.extend((AuthApiSpentTime.AdminAuth, have_auth, check_result))

            # Step 2 : Create a Job
            ServiceTypeList = list(self.admin_setting_config['condition']['service_types'].split(","))
            api_response, job_id, status = JobAPI.CreateJobs(self.admin_setting_config, timedict, ServiceTypeList)
            resultList.extend((FrameworkVar.ApiSpentTime, status, api_response))

            # Step 3 : Assign DA to Job
            da_id = GetDAId(self.setting_config, "DA_Setting")
            assign_response, status = JobAPI.AssignDaToJobs(self.setting_config, job_id, da_id)
            resultList.extend((FrameworkVar.ApiSpentTime, status, assign_response))

            # Step 4 : Cancel Job and check response error_message will be 028003
            response, status = JobAPI.ChangeJobStatus(self.setting_config, job_id, "finish")
            response, status = JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")
            check_result, status = OrderMethod.GetAndCheckJobReturnMessage(response, status, "028003")
            resultList.extend((FrameworkVar.ApiSpentTime, status, check_result))
        except TypeError as err:
            dumplogger.exception(err)
        except Exception as err:
            dumplogger.exception(err)
            if job_id:
                JobAPI.ChangeJobStatus(self.setting_config, job_id, "cancel")

        # Final : Update result to testrail
        CommonMethod.UpdateResultToTestrail(self.runId, self.testIds, "9588", resultList, self.test_case_time_start)



if __name__ == '__main__':
    unittest.main()
