from typing import OrderedDict
import sys
sys.path.append("./")
import numpy as np
import os
import Method.CommonMethod as CommonMethod
import json

from Core.ApiQuery import *
from Library.Config import dumplogger

class SearchMethod:

    def SearchOrder(condition, limit, reasonable = None):
        '''
            Search order by condition
        '''
        check_status = False
        data_description = ""
        try:
            status_code, api_data = DeliveryAgentAPI.GetDAMyOrderList(limit)
            if status_code == 200 and condition:
                if condition == "Full":
                    data_description = "The DA MyOrder have orders : %s " % str(len(api_data['data']))
                    check_status = True
                else:
                    if condition in json.dumps(api_data['data']):
                        data_description = "Find this key word(%s) in DA MyOrder have orders : %s " % (condition,str(len(api_data['data'])))
                        check_status = True
                    else:
                        data_description = "Can't find this key word(%s) in Order List " % condition
                        if reasonable:
                            check_status = True
                        else:
                            check_status = False
            else:
                data_description = api_data
                check_status = False

        except TypeError as e:
            data_description = "Script have exception, please check logger"
            dumplogger.exception(e)
        except Exception as e:
            data_description = "Script have exception, please check logger"
            dumplogger.exception(e.message)

        return check_status, data_description
