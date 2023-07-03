#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from Library.Config import dumplogger


def Click(driver, waiting_period, xpath):
    '''
    Click : Click any content in Web
    '''
    try:
        WebDriverWait(driver, waiting_period).until(EC.element_to_be_clickable((By.XPATH, (xpath)))).click()
    except TimeoutException:
        message = "Cannot find element in %s seconds. Element xpath => %s" % (waiting_period, xpath)
        dumplogger.exception(message)


def CheckElementExist(driver, waiting_period, xpath):
    '''
    CheckElementExist : Check the element exist or not
    '''
    try:
        WebDriverWait(driver, waiting_period).until(EC.presence_of_element_located((By.XPATH, (xpath))))
    except TimeoutException:
        message = "Cannot find element in %s seconds. Element xpath => %s" % (waiting_period, xpath)
        dumplogger.exception(message)
        return False
    except:
        message = "Encounter unknown exception."
        dumplogger.exception(message)
    return True


def CheckButtonClickable(driver, waiting_period, xpath):
    '''
    CheckButtonClickable : Check the button state clickable or not
    '''
    ##Check element is clickable or not
    try:
        ele_clickable = WebDriverWait(driver, waiting_period).until(EC.presence_of_element_located((By.XPATH, (xpath)))).is_enabled()
        ##Check element clickable result is expected or not
        if ele_clickable:
            dumplogger.info("Button is Enable")
            WebDriverWait(driver, waiting_period).until(EC.element_to_be_clickable((By.XPATH, (xpath)))).click()
        else:
            dumplogger.info("Button is Disable")

    except TimeoutException:
        message = "Cannot find element in %s seconds. Element xpath => %s" % (waiting_period, xpath)
        dumplogger.exception(message)
    except:
        message = "Encounter unknown exception."
        dumplogger.exception(message)
