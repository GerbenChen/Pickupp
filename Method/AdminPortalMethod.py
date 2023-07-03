from typing import OrderedDict
import sys
sys.path.append("./")
import numpy as np
import os
from Core.ApiQuery import*
from Library.Config import dumplogger
import Method.CommonMethod as CommonMethod

class AdminMerchantPage:

    def GetAndCheckWallerHistory(order_id, merchant_id, target_status, payment_method):
        '''
            Call .npy file and using Service type to get OrderID
        '''
        check_status = False
        data_description = ""
        try:
            status_code, wallet_data = AdminMerchantAPI.GetWalletHistory(merchant_id)
            if status_code == 200:
                for raw in range(len(wallet_data["data"])):
                    if order_id == wallet_data["data"][raw]["order_id"]:
                        if target_status == wallet_data["data"][raw]["status"] and payment_method == wallet_data["data"][raw]["payment_gateway"]:
                            check_status = True
                            data_description = wallet_data["data"][raw]["description"]
                        else:
                            check_status = False
                            data_description = "Can't find currently status or payment method in wallet history list"
            else:
                check_status = False
                data_description = CommonMethod.ResponseHandler(status_code, wallet_data)

        except TypeError as e:
            data_description = "Script have exception, please check logger"
            dumplogger.exception(e)

        except Exception as e:
            data_description = "Script have exception, please check logger"
            dumplogger.exception(e.message)

        return check_status, data_description

    def PUDOSettingCompair(dropoff_response, merchant_response):
        '''
            Check Compair PU/DO Setting
        '''
        compar_status = False
        message = ""
        try:
            pu_compar_status = CommonMethod.CompairTwoDict(dropoff_response['data']['pickup_options'], merchant_response['data']['pickup_options'][dropoff_response['data']['service_type']])
            do_compar_status = CommonMethod.CompairTwoDict(dropoff_response['data']['dropoff_options'], merchant_response['data']['dropoff_options'][dropoff_response['data']['service_type']])
            if pu_compar_status == do_compar_status:
                compar_status = True
                message = "service type setting as same as dropoff process return"
            else:
                compar_status = False
                message = "service type setting not match dropoff process return"
        except KeyError as e:
            message = "No data can compair, please check api response"
            dumplogger.exception(e)
        except TypeError as e:
            message = "Script have exception, please check logger"
            dumplogger.exception(e)
        except Exception as err:
            message = "Script have exception, please check logger"
            dumplogger.exception(err)

        return compar_status, message

