import sys, os, functools
sys.path.append("./")

import time
import Library.LogFormatter as LogFormatter
from inspect import getframeinfo, stack
from Library.Config import today_time,log_file_name
from datetime import date

def FuncRecorder(_func=None):
    def FuncDecoratorInfo(func):
        @functools.wraps(func)
        def FuncRecordWrapper(self, *args, **kwargs):

            today = today_time
            file_name = log_file_name
            logger_obj = LogFormatter.GetLogger(log_file_name=file_name, log_sub_dir=today)
            args_passed_in_function = [repr(a) for a in args]
            kwargs_passed_in_function = [f"{k}={v!r}" for k, v in kwargs.items()]
            formatted_arguments = ", ".join(args_passed_in_function + kwargs_passed_in_function)

            py_file_caller = getframeinfo(stack()[1][0])
            extra_args = { 'func_name_override': func.__name__,
                           'file_name_override': os.path.basename(py_file_caller.filename) }

            logger_obj.info(f"Begin function - Arguments: {formatted_arguments}", extra=extra_args)
            # print(f"Arguments: {formatted_arguments} - Begin function {func.__name__}")
            try:
                time.sleep(3)
                ##Start time
                time_first = time.time()
                value = func(self, *args, **kwargs)
                ##End time
                time_second = time.time()
                logger_obj.info(f"End function - Returned: {value!r}", extra=extra_args)
                logger_obj.info("End function %s at %.2f sec" % (func.__name__, time_second - time_first), extra=extra_args)
                # print("Leave %s at %.2f sec" % (func.__name__, time_second - time_first))
                # print(f"Returned: - End function : %s" % func.__name__)
            except:
                logger_obj.error(f"Exception: {str(sys.exc_info()[1])}", extra=extra_args)
                # print(f"Exception: {str(sys.exc_info()[1])}")
                raise

            return value
        return FuncRecordWrapper
    if _func is None:
        return FuncDecoratorInfo
    else:
        return FuncDecoratorInfo(_func)