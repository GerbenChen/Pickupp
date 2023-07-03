#!/usr/bin/python
# -*- coding: UTF-8 -*-
import unittest
import sys
sys.path.append("./")
from Library.GlobalAdapter import *
from Method.CommonMethod import*
from Core.ApiQuery import*
from Library.DBConnector import*
from Utility.testrail import*
from datetime import date
import configparser
class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr
class STWithSOCheck(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('STWithSOCheck.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('common_setting.ini')
        self.TestSuiteName = "ST With SO Check"
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Dev_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Dev_Setting']['url']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Dev_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Dev_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Dev_Setting')
    @classmethod
    def tearDownClass(self):
        CleanTrips(745)
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        CommonMethod.DeInitialAPIVar()
    def CheckTotalStatus(self,resultList):
        for index in resultList:
            if index == False:
                return 5
        return 1  
 
    def TranslateForStatus(self,resultList):
        FinalResult = []
        for index in resultList:
            if index == True:
                FinalResult.append(1)
            elif index == False:
                FinalResult.append(5)
            else:
                FinalResult.append(index)
        return FinalResult
    
    def test_STWithSOCheck_4Hours(self):
        totalstatus = True
        resultList = []
        #Step 1 : Get_auth_portal
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.MerchantPortalAuth))
        #Step 2 : Get_auth_admin
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.AdminAuth))
        #Step 3 : Get_auth_da
        resultList.extend((totalstatus, GlobalAdapter.AuthVar.DAAuth))
        #Step 4 : Create an order without SO id in payload
        status_code, Statuslist, status = STWithSOCreateOrder(self.config,'4Hours',totalstatus)
        resultList.extend((status, Statuslist))
        #Step 5 : Check Response had Include Service offering ID
        if Statuslist[1] == self.config['condition_4Hours']['checksoid']:
            resultList.extend((True, Statuslist[1]))
        else:
            resultList.extend((False, "Service Offfering ID was not equal"))
        #Step 6 : Create an order Include SO id
        status_code, Response, status = STWithSOCreateOrder(self.config,'4HoursSOID',totalstatus)
        if status_code == 400:
            status = True
        resultList.extend((status, Response))
        #Step 7 : Check BackBone Order exist or not
        BackBoneOrderID = GetBackBoneOrderStatus(Statuslist[0])
        if BackBoneOrderID == Statuslist[0]:
            resultList.extend((True, "The BackBone Order exist"))
        else:
            resultList.extend((False, "The BackBone Order was not exist"))
        #Step 8 : Check BackBone Order on DB
        connection = connect_postgresql(dbname="dev")
        command = """select service_offering_id  from backbone."Orders" where id = '%s'""" % Statuslist[0]
        response = execute_postgresql_fetchone(connection, command)
        if response[0] == self.config['condition_4Hours']['checksoid']:
            resultList.extend((True, "The BackBone Order was on DB"))
        else:
            resultList.extend((False, "The BackBone Order was not on DB"))            
        #Step 9 : Assign Order to DA
        da_id = GetDAId(self.setting_config, "DA_Dev_Setting")
        api_response, tripid, status = AssignToDeliveryAgent(Statuslist[0],da_id)
        resultList.extend((status, api_response))
        #Step 10 : Enroute
        response, status = Enroute(tripid)
        resultList.extend((status, response))
        #Step 10 : Dropoff Process
        response, status = DropOffProcess(tripid)
        resultList.extend((status, response))
        #Step 11 : Dropoff
        response, status = DropOff(tripid)
        resultList.extend((status, response))
        #Step 12 : Payrolls
        status = 3
        response = ""
        resultList.extend((status, response))
        #Step 13 : Updata Order Detail and check
        status_code, Statuslist, status = STWithSOCreateOrder(self.config,'4Hours',totalstatus)
        status_code, response, status = SetupOrderDetail(Statuslist[0])
        if len(set(response)) == 1:
            resultList.extend((status, "Check Set order detail success"))
        else:
            resultList.extend((False, "Check Set order detail fail"))
        #Final : Update result to testrail
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"STWithSOCheck_4Hours",resultList,self.runId)
if __name__ == '__main__':
    unittest.main()  