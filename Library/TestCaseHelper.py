# -*- coding: utf-8 -*-
from __future__ import print_function
from functools import wraps
from pprint import pprint
import time
from Library.Config import dumplogger

def TestTimed(function):
    """
        Functions so decorated will print the time they took to execute.
    """
    @wraps(function)
    def TestCaseRecord(*args, **kwargs):
        dumplogger.info("=================== Test %s Started ===================" % function.__name__)
        time_start = time.time()
        out = function(*args, **kwargs)
        time_end = time.time()
        dt = str((time_end - time_start) * 1.00)
        test_case_spent_time = dt[:(dt.find(".") + 4)]

        if out is not None:
            print('RESULTS:')
            pprint(out, indent=4)

        dumplogger.info("=================== Test %s finished in %s seconds ===================" % (function.__name__, test_case_spent_time))

        return out

    return TestCaseRecord
