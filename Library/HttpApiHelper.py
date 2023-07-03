#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 HttpApiHelper.py: The def of this file called by other function.
'''
import time

from Library.Config import dumplogger
from Library.GlobalAdapter import FrameworkVar
import requests
import inspect

##For Send HTTP packets to API interface
class APIController():

    def SendAPIPacket(http_method, url, headers=None, payload=None, url_param=None):
        ''' SendAPIPacket : Send API Packet
                Input argu :
                    http_method - get, delete, post, put
                    url - url for http request
                    payload - payload for http request
                    headers - headers for http request
                Return code :
                    http response - session / status / text
                    0 - fail
        '''

        dumplogger.info("Enter APIController SendAPIPacket")
        http_method = str(http_method).lower()
        response = ""
        status_code = ""
        ##Start time
        time_first = time.time()

        dumplogger.info("Send to api url: %s" % (url))
        dumplogger.info("Send header to api: %s" % str(headers))
        dumplogger.info("Send payload to api: %s" % str(payload))

        ##HTTP Get
        if http_method == "get":
            # time.sleep(5)
            ##Send get request directly
            dumplogger.info("Send get request directly")
            response = requests.get(url, headers=headers, data=payload, params=url_param)
        ##HTTP Delete
        elif http_method == "delete":
            ##Send delete request directly
            dumplogger.info("Send delete request directly")
            response = requests.delete(url, headers=headers)
        #HTTP POST
        elif http_method == "post":
            # time.sleep(5)
            ##Send Post request directly
            dumplogger.info("Send Post request directly")
            response = requests.post(url, headers=headers, data=payload, params=url_param)
        #HTTP PUT
        elif http_method == "put":
            # time.sleep(5)
            ##Send Put request directly
            dumplogger.info("Send Put request directly")
            response = requests.put(url=url, headers=headers, data=payload)
        else:
            dumplogger.error("!!!!Please check your http_method!!!!")


        try:
            status_code = response.status_code
            response_data = response.json()
            dumplogger.info("%s -> Response status code : %d" % (http_method, response.status_code))
            # dumplogger.info(response_data)
        except :
            if response.status_code:
                dumplogger.info("Error - %s -> Response status code : %d" % (http_method, response.status_code))
                dumplogger.info("Error from server: %s " % str(response.text))
                status_code = response.status_code
                response_data = response.text

        ##End time
        time_second = time.time()

        #Record API Spent time
        FrameworkVar.ApiSpentTime = time_second - time_first

        dumplogger.info("End APIController SendAPIPacket")
        return status_code, response_data


