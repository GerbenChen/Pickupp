from typing import OrderedDict
import sys
sys.path.append("./")
import numpy as np
import os
from Core.ApiQuery import*
from Library.Config import dumplogger
import Method.CommonMethod as CommonMethod

class PaymentProfilePage:

    def GetAndCheckTransactionHistory(order_id, amount):
        '''
            Get And Check Transaction History
        '''
        check_status = False
        data_description = ""
        try:
            status_code, transaction_data = MerchantPortal.GetTransactionHistory(order_id)
            if status_code == 200:
                for data in transaction_data["data"]:
                    if order_id == data["order_id"]:
                        if amount == data["amount"]:
                            check_status = True
                            data_description = "Transaction : " + data["description"]
                        else:
                            check_status = False
                            data_description = "Can't find currently refund amount in transaction list"
            else:
                check_status = False
                data_description = CommonMethod.ResponseHandler(status_code, transaction_data)
        except TypeError as e:
            data_description = "Script have exception, please check logger"
            dumplogger.exception(e)
        except Exception as e:
            data_description = "Script have exception, please check logger"
            dumplogger.exception(e.message)

        return check_status, data_description
