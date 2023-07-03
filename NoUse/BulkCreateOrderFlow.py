#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
sys.path.append("./")
import unittest
import shutil
from Core.ApiQuery import*
from Utility.testrail import*
import configparser
import openpyxl
import string
import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
import os
import re
import Core.BaseUICore as BaseUICore
from Library.Config import dumplogger

class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class Order_flow(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/bulkordercondition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')
        self.TestSuiteName = "Bulk Create Order"
        GlobalAdapter.CommonVar.AdminUrl = self.setting_config['Admin_Setting']['url']
        GlobalAdapter.CommonVar.PortalUrl = self.setting_config['Portal_Setting']['url']
        GlobalAdapter.CommonVar.TopUpUrl = self.setting_config['Api_Url']['top_up']
        GlobalAdapter.CommonVar.CreditCardUrl = self.setting_config['Api_Url']['credit_card']
        GlobalAdapter.CommonVar.StripeTokensUrl = self.setting_config['Api_Url']['stripe_tokens']
        GlobalAdapter.AuthVar.AdminAuth = GetAdminAuth(self.setting_config, 'Admin_Setting')
        GlobalAdapter.AuthVar.MerchantPortalAuth = GetMerchantAuth(self.setting_config, 'Portal_Setting')
        GlobalAdapter.AuthVar.DAAuth = GetDAAuth(self.setting_config, 'DA_Setting')
        self.runId, self.testIds = AddTestRunAndTest(self.TestSuiteName)

    def setUp(self):
        opts = Options()
        opts.add_argument('--no-sandbox')
        opts.add_argument('--headless')
        opts.add_argument('--disable-gpu')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument("--window-size=1440,900")
        opts.binary_location = "/usr/bin/google-chrome"
        self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),chrome_options=opts)

    def tearDown(self):
        self.driver.delete_all_cookies()
        sleep(5)
        self.driver.quit()

    @classmethod
    def tearDownClass(self):
        GetRunResultAndCheckStatusThenSendToSlack(self.runId,self.TestSuiteName)
        sleep(10)

    #Different Region need to different format
    def TimeCul(self):
        dumplogger.info(datetime.datetime.today())
        GetDate = datetime.datetime.today()+datetime.timedelta(days=1)
        year = GetDate.year
        month = GetDate.month
        day = GetDate.day
        hour = GetDate.hour
        minute = GetDate.minute
        self.PickUpTime = "%02d/%02d/%s %s:%s" % (day,month,year,10,minute)
        self.DropOffTime = "%02d/%02d/%s %s:%s" % (day,month,year,10,minute)
        return self.PickUpTime, self.DropOffTime

    def WriteDataToExcel(self,numbers):
        FileName = os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath']
        try:
            WorkBook = openpyxl.load_workbook(FileName)
            WorkBook.active = 0
            WorkSheet = WorkBook.active
            for i in range(int(numbers)):
                low = i+16
                WorkSheet['%s%s' % (string.ascii_uppercase[0],low)] = self.config['common']['PickUppName']
                WorkSheet['%s%s' % (string.ascii_uppercase[1],low)] = self.config['common']['PickUppPhoneNumber']
                WorkSheet['%s%s' % (string.ascii_uppercase[2],low)] = self.config['common']['PickUppAddress']
                WorkSheet['%s%s' % (string.ascii_uppercase[3],low)] = self.config['common']['DropOffName']
                WorkSheet['%s%s' % (string.ascii_uppercase[4],low)] = self.config['common']['DropOffPhoneNumber']
                WorkSheet['%s%s' % (string.ascii_uppercase[5],low)] = self.config['common']['DropOffAddress']
                WorkSheet['%s%s' % (string.ascii_uppercase[6],low)] = self.config['common']['PartnerStoreNumber']
                WorkSheet['%s%s' % (string.ascii_uppercase[7],low)] = self.config['common']['ItemName']
                WorkSheet['%s%s' % (string.ascii_uppercase[8],low)] = self.config['common']['Length']
                WorkSheet['%s%s' % (string.ascii_uppercase[9],low)] = self.config['common']['Width']
                WorkSheet['%s%s' % (string.ascii_uppercase[10],low)] = self.config['common']['Height']
                WorkSheet['%s%s' % (string.ascii_uppercase[11],low)] = self.config['common']['Weight']
                WorkSheet['%s%s' % (string.ascii_uppercase[12],low)] = self.config['common']['NumberofPackages']
                WorkSheet['%s%s' % (string.ascii_uppercase[13],low)] = self.config['common']['ReferenceNumberperPackage']
                PickupTime, DropOffTime = self.TimeCul()
                WorkSheet['%s%s' % (string.ascii_uppercase[14],low)] = PickupTime
                WorkSheet['%s%s' % (string.ascii_uppercase[15],low)] = DropOffTime
            WorkBook.save(FileName)
            return "Write Data Success"

        except Exception as e:
            return e.args

    def ReadDataFromExcel(self,numbers):
        FileName = os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath']
        WorkBook = openpyxl.load_workbook(FileName)
        WorkBook.active = 0
        WorkSheet = WorkBook.active
        TotalList = []
        BulkOrderDataList = []
        for i in range(int(numbers)):
            low = i+16
            for j in range(16):
                BulkOrderDataList.append(WorkSheet['%s%s' % (string.ascii_uppercase[j],low)])
            TotalList.append(BulkOrderDataList)
        return "Read Data Success"

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

    def FindElementXpathWaitTime(self,path):
        self.driver.find_element(By.XPATH,path).click()
        sleep(3)

    def FindElementXpathWaitLongTime(self,path):
        self.driver.find_element(By.XPATH,path).click()
        sleep(10)

    def FindElementXpathSendKeyWaitTime(self,Xpath,Sendkey):
        self.driver.find_element(By.XPATH,Xpath).send_keys(Sendkey)
        sleep(3)

    def FindElementXpathWaitAndRetry(self,Xpath):
        for i in range(5):
            sleep(20)
            try:
                self.driver.find_element(By.XPATH,Xpath).click()
                break
            except WebDriverException as e:
                dumplogger.exception(e.args)

    def WaitFor30sAndFindElementXpath(self,Xpath):
        for i in range(3):
            try:
                self.driver.find_element(By.XPATH,Xpath).click()
                break
            except WebDriverException as e:
                dumplogger.exception(e.args)
                sleep(30)

    def FindElementXpathWaitAndRetryNotBreak(self,Xpath):
        for i in range(3):
            sleep(10)
            try:
                self.driver.find_element(By.XPATH,Xpath).click()
            except WebDriverException as e:
                dumplogger.exception(e.args)

    def FindElementXpathWaitAndRetryThenButtonEnable(self,Xpath):
        for i in range(3):
            try:
                element = self.driver.find_element(By.XPATH,Xpath)
                if element.is_enabled():
                    dumplogger.info("Button is Enable")
                    element.click()
                    break
                else:
                    dumplogger.info("Button is Disable")
                    sleep(10)
            except WebDriverException as e:
                dumplogger.exception(e.args)
                sleep(10)

    def FindElementXpathGetAttributeAndRetry(self,Xpath):
        OrderNumberList = []
        links = self.driver.find_elements(By.XPATH,Xpath)
        for link in links:
            linktext = link.get_attribute("href")
            dumplogger.info(linktext)
            if linktext != None:
                try:
                    match = re.search(r'.*/orders/(PU.*)',linktext)
                    ordernumber = match.group(1)
                    OrderNumberList.append(str(ordernumber))
                except:
                    pass
        return OrderNumberList

    def CheckOutFlow(self):
        self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
        self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
        if BaseUICore.CheckElementExist(self.driver, self.setting_config['Common_Var']['waiting_period'], self.config['seleniumPath']['paynow']):
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
        else:
            topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
            if topup_status_code == 201:
                BaseUICore.CheckButtonClickable(self.driver, self.setting_config['Common_Var']['waiting_period'], self.config['seleniumPath']['back_and_edit'])
                self.CheckOutFlow()
            else:
                return topup_status_code, topup_response, False

    def test_BulkCreateByExpress(self):
        totalstatus = True
        resultList = []
        #Step 1 : Write Data In to excel
        status = self.WriteDataToExcel(3)
        resultList.extend((totalstatus, status))
        #Step 2 : Read Data from excel
        TotalList = self.ReadDataFromExcel(self.config['common']['DataCount'])
        resultList.extend((totalstatus, TotalList))
        #Step 3 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['ServiceTypeExpress']).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateByExpress",resultList,self.runId)

    def test_BulkCreateBy4Hours(self):
        totalstatus = True
        resultList = []
        #Step 1 : Write Data In to excel
        status = self.WriteDataToExcel(3)
        resultList.extend((totalstatus, status))
        #Step 2 : Read Data from excel and trigger BuilOrder
        TotalList = self.ReadDataFromExcel(self.config['common']['DataCount'])
        resultList.extend((totalstatus, TotalList))
        #Step 3 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['ServiceType4Hours']).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateBy4Hours",resultList,self.runId)

    def test_BulkCreateByFirstLeg(self):
        totalstatus = True
        resultList = []
        #Step 1 : Write Data In to excel
        status = self.WriteDataToExcel(3)
        resultList.extend((totalstatus, status))
        #Step 2 : Read Data from excel and trigger BuilOrder
        TotalList = self.ReadDataFromExcel(self.config['common']['DataCount'])
        resultList.extend((totalstatus, TotalList))
        #Step 3 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['ServiceTypeFirstLag']).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateByFirstLeg",resultList,self.runId)

    def test_BulkCreateByCollection(self):
        totalstatus = True
        resultList = []
        #Step 1 : Write Data In to excel
        status = self.WriteDataToExcel(3)
        resultList.extend((totalstatus, status))
        #Step 2 : Read Data from excel and trigger BuilOrder
        TotalList = self.ReadDataFromExcel(self.config['common']['DataCount'])
        resultList.extend((totalstatus, TotalList))
        #Step 3 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['ServiceTypeCollection']).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateByCollection",resultList,self.runId)

    def test_BulkCreateByExchange(self):
        totalstatus = True
        resultList = []
        #Step 1 : Write Data In to excel
        status = self.WriteDataToExcel(3)
        resultList.extend((totalstatus, status))
        #Step 2 : Read Data from excel and trigger BuilOrder
        TotalList = self.ReadDataFromExcel(self.config['common']['DataCount'])
        resultList.extend((totalstatus, TotalList))
        #Step 3 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['ServiceTypeExchange']).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateByExchange",resultList,self.runId)

    def test_BulkCreateBySameDay(self):
        totalstatus = True
        resultList = []
        #Step 1 : Write Data In to excel
        status = self.WriteDataToExcel(3)
        resultList.extend((totalstatus, status))
        #Step 2 : Read Data from excel and trigger BuilOrder
        TotalList = self.ReadDataFromExcel(self.config['common']['DataCount'])
        resultList.extend((totalstatus, TotalList))
        #Step 3 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['ServiceTypeSameDay']).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['Okaybutton'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateBySameDay",resultList,self.runId)

    def test_BulkCreateByNextDay(self):
        totalstatus = True
        resultList = []
        #Step 1 : Write Data In to excel
        status = self.WriteDataToExcel(3)
        resultList.extend((totalstatus, status))
        #Step 2 : Read Data from excel and trigger BuilOrder
        TotalList = self.ReadDataFromExcel(self.config['common']['DataCount'])
        resultList.extend((totalstatus, TotalList))
        #Step 3 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['ServiceTypeNextDay']).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['Okaybutton'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateByNextDay",resultList,self.runId)

    def test_BulkCreateByOptional(self):
        totalstatus = True
        resultList = []
        #Step 1 : Need to manual upload to bitbucket BulkOrderFile/ServiceTypeXXXX.xlsx
        path = (os.path.abspath(os.getcwd())+self.config['seleniumPath']['OptionalFilepath'])
        shutil.copy(os.path.abspath(os.getcwd())+self.config['seleniumPath']['filepath'], path+'ServiceType4Hours.xlsx')
        for filename in os.listdir(path):
            if filename.endswith('.xlsx'):
                ServiceTypeFile = filename
                ServiceType = filename.split('.')[0]
        NameRuleList = self.config['common']['namerulelist']
        if ServiceType in NameRuleList:
            status = True
        else:
            status = False
        resultList.extend((status, ServiceTypeFile))
        #Step 2 : Using Selenium to upload file and Pay
        try:
            self.driver.get(self.config['seleniumPath']['loginpage'])
            self.driver.implicitly_wait(10)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['email']).send_keys(self.config['common']['email'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).click()
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['password']).send_keys(self.config['common']['password'])
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['termscheck']).click()
            self.FindElementXpathWaitTime(self.config['seleniumPath']['login'])
            self.driver.get(self.config['seleniumPath']['bulkpage'])
            self.driver.implicitly_wait(10)
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipclose'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            self.FindElementXpathWaitTime(self.config['seleniumPath']['tipgotit'])
            dumplogger.info("Start to Upload File")
            self.FindElementXpathSendKeyWaitTime(self.config['seleniumPath']['file'],os.path.abspath(os.getcwd())+self.config['seleniumPath']['OptionalFilepath']+ServiceTypeFile)
            self.driver.find_element(By.XPATH,self.config['seleniumPath']['%s' % ServiceType]).click()
            self.FindElementXpathWaitLongTime(self.config['seleniumPath']['confirm'])
            # self.WaitFor30sAndFindElementXpath(self.config['seleniumPath']['ready'])
            # sleep(30)
            # self.FindElementXpathWaitAndRetryThenButtonEnable(self.config['seleniumPath']['checkout'])
            # self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['paynow'])
            self.CheckOutFlow()
            self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['GotItAfterPay'])
            if ServiceType in self.config['common']['schedulelaterList']:
                self.FindElementXpathWaitAndRetry(self.config['seleniumPath']['schedulelater'])
            self.FindElementXpathWaitAndRetryNotBreak(self.config['seleniumPath']['complete'])
            resultList.extend((True, "Finish Selenium"))
        except WebDriverException as e:
            resultList.extend((False, [e.args]))
        self.driver.implicitly_wait(10)
        OrderNumberList = self.FindElementXpathGetAttributeAndRetry(self.config['seleniumPath']['hrefpath'])
        #Check The Order Complete or not
        if len(OrderNumberList) == int(self.config['common']['DataCount']):
            resultList.extend((totalstatus, OrderNumberList))
        else:
            resultList.extend((False, OrderNumberList))
        #Compare OrderList equal Complete or not
        status_code, response, status = GetMerchantPortalOrderListTotally(totalstatus)
        if set(OrderNumberList) == set():
            resultList.extend((totalstatus, "Order Numbers is Empty"))
        else:
            if set(OrderNumberList) < set(response):
                resultList.extend((totalstatus, "Order Numbers All in OrdersList"))
            else:
                resultList.extend((False, "OrdersList Not Found"))
        totalstatus = self.CheckTotalStatus(resultList)
        resultList = self.TranslateForStatus(resultList)
        AddResultByStep(totalstatus,self.testIds,"BulkCreateByOptional",resultList,self.runId)

if __name__ == '__main__':
    unittest.main()
