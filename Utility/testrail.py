#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import time
from testrail_api import TestRailAPI
import configparser
import Utility.WebhookTestRailToSlack as WebhookTestRailToSlack
from Library.Config import dumplogger
testrail_config = configparser.ConfigParser()
testrail_config.read('./Config/testrail.ini')
api = TestRailAPI(testrail_config['UserSetting']['url'], testrail_config['UserSetting']['account'], testrail_config['UserSetting']['password'])
#list(testrail_config[TestSuiteName]['case_ids'])
def AddTestRunAndTest(TestSuiteName):
    runId = api.runs.add_run(project_id=2,suite_id=testrail_config[TestSuiteName]['suite_id'],name=TestSuiteName,include_all=False,case_ids=testrail_config[TestSuiteName]['case_ids'].split(','))
    testIds = api.tests.get_tests(run_id=runId["id"])
    return runId["id"],testIds

def GetTestCaseInfoWithCaseID(test_ids,case_id):
    test_id = 0
    case_step_counts = 0
    try:
        for case_raw in range(len(test_ids['tests'])):
            if str(case_id) == str(test_ids['tests'][case_raw]['case_id']):
                test_id = test_ids['tests'][case_raw]['id']
                case_step_counts = len(test_ids['tests'][case_raw]['custom_steps_separated'])
    except IndexError as err:
        dumplogger.error("Unknown Exception : %s" % str(err))
    except :
        dumplogger.error("Can't Get Test Case (%s) Info by case_id (%s)" % (str(test_ids), str(case_id)))
    return test_id, case_step_counts

def AppendTestContentForResult(test_id, result_list, case_step_counts):
    '''
        AppendTestContentForResult : append test content for result
        input:
            test_id,
            result_list - api_spent_time, step_status, response_content
            case_step_counts
        return :
            result list
    '''
    result = []
    try:
        for i in range(case_step_counts):
            body = {
                    "status_id":"%s" % result_list[((i*3)+1)],
                    "actual":"%s" % result_list[((i*3)+2)],
                    "content":"Step %s  -  Api Time taken : %.2f sec" % (i + 1, result_list[(i * 3)]),
                }
            result.append(body)
    except IndexError as err:
        dumplogger.error("Append Test Content For Result Fail, Please Check %s Test Case Step : %s" % (str(test_id),str(err)))
    except Exception as err:
        dumplogger.error("Append Test Content For Result Fail, Exception : %s" % str(err))
    return result

def AddResultByStep(test_status, test_case_spent_time, test_run_id, test_id, case_step_counts, result_list):
    #print (testId)
    result = AppendTestContentForResult(test_id, result_list, case_step_counts)
    try:
        api.results.add_results(
                    run_id = test_run_id,
                    results = [
                        {
                            "test_id": test_id,
                            "status_id": test_status,
                            "custom_step_results": result,
                            "elapsed":test_case_spent_time
                        }]
                    )
        dumplogger.info("Add Result By Step Success, Test Case Id : %s" % str(test_id))
    except IndexError as err:
        dumplogger.error("Add Result By Step Fail, Please Check %s Test Case Step : %s" % (str(test_id),str(err)))
    except Exception as err:
        dumplogger.error("Add Result By Step Fail, Exception : %s" % str(err))
        if "maintenance" in str(err):
            ReAddResultByStep(test_run_id, test_id, test_status, result, test_case_spent_time)


def ReAddResultByStep(test_run_id, test_id, test_status, result, test_case_spent_time):
    #print (testId)
    time.sleep(5)
    try:
        api.results.add_results(
                    run_id = test_run_id,
                    results = [
                        {
                            "test_id": test_id,
                            "status_id": test_status,
                            "custom_step_results": result,
                            "elapsed":test_case_spent_time
                        }]
                    )
        dumplogger.info("Re-Add Result By Step Success, Test Case Id : %s" % str(test_id))
    except IndexError as err:
        dumplogger.error("Re-Add Result By Step Fail, Please Check %s Test Case Step : %s" % (str(test_id),str(err)))
    except Exception as err:
        dumplogger.error("Re-Add Result By Step Fail, Exception : %s" % str(err))

def CheckResultStepAmount(result_list, case_step_counts):
    try:
        result_step_amount = int(len(result_list) / 3)
        dumplogger.info("Automation Script Step Count : %s, Test Rails Step Count : %s" % (str(result_step_amount), str(case_step_counts)))
        if result_step_amount != case_step_counts and result_step_amount < case_step_counts:
            for index in range(case_step_counts-result_step_amount):
                result_list.extend((0.1, False, "Fail, Not run this step"))
    except Exception as err:
        dumplogger.error("Compair Result Step Amount Fail, Exception : %s" % str(err))
    return result_list

def IntegrationFailCaseQuote(ErrorCaseNameList,CaseStatusTestIdList):
    try:
        FailCase = "*FailCaseLink:* "
        if len(ErrorCaseNameList) == 0:
            FailCase = "None"
        else:
            for index in range(len(ErrorCaseNameList)):
                FailCase = FailCase + "<%s|%s>." % (testrail_config['UserSetting']['caseurl']+str(CaseStatusTestIdList[index]),str(ErrorCaseNameList[index]))
    except Exception as err:
        dumplogger.info("Unknown Exception : %s" % str(err))
    return FailCase

def CulResultStatus(CaseStatusList):
    TotalResult = []
    TotalResult.append(CaseStatusList.count(1))
    TotalResult.append(CaseStatusList.count(5))
    return TotalResult

def GetRunResultAndCheckStatusThenSendToSlack(RunId,TestSuiteName):
    CaseStatusList = []
    ErrorCaseNameList = []
    CaseStatusTestIdList = []
    try:
        result = api.results.get_results_for_run(RunId)
        for index in range(len(result["results"])):
            CaseStatus = result["results"][index]["status_id"]
            CaseStatusList.append(int(CaseStatus))
            if int(CaseStatus) == 5:
                CaseStatusTestId = api.tests.get_test(result["results"][index]["test_id"])
                CaseStatusTestIdList.append(CaseStatusTestId['id'])
                CaseNameTmp = api.cases.get_case(CaseStatusTestId['case_id'])
                CaseName = CaseNameTmp['title']
                ErrorCaseNameList.append(CaseName)
        TotalResult = CulResultStatus(CaseStatusList)
        TestResultLink = testrail_config['UserSetting']['resulturl']+ str(RunId)
        FailCase = IntegrationFailCaseQuote(ErrorCaseNameList,CaseStatusTestIdList)
        WebhookTestRailToSlack.WebHookSendResult(TestSuiteName,TotalResult,FailCase,TestResultLink)
    except Exception as err:
        dumplogger.info("Unknown Exception : %s" % str(err))
