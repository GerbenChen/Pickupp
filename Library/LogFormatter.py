import logging
import os
import datetime
import pytz

class CustomFormatter(logging.Formatter):


    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            time_string = dt.strftime(datefmt)
        else:
            try:
                time_string = dt.isoformat(timespec='milliseconds')
            except TypeError:
                time_string = dt.isoformat()
        return time_string

    def format(self, record):
        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        return super(CustomFormatter, self).format(record)

    def converter(self, timestamp):
        # Create datetime in UTC
        dt = datetime.datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        # Change datetime's timezone
        return dt.astimezone(pytz.timezone('Asia/Taipei'))


def GetLogger(log_file_name, log_sub_dir=""):
    """ Creates a Log File and returns Logger object """

    ## if you need print logger into file, please remark it.
    # root_path = os.getcwd()
    # windows_log_dir = root_path + '\\LogsDir\\'
    # linux_log_dir = root_path + '/LogsDir/'
    #
    # log_dir = windows_log_dir if os.name == 'nt' else linux_log_dir
    # log_dir = os.path.join(log_dir, log_sub_dir)
    #
    # if not os.path.exists(log_dir):
    #     os.makedirs(log_dir)
    # logPath = log_file_name if os.path.exists(log_file_name) else os.path.join(log_dir, (str(log_file_name) + '.log'))

    logger = logging.Logger(log_file_name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter('%(asctime)s - [%(levelname)s]|[%(filename)s:%(lineno)d] - %(funcName)s - %(message)s','%Y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)

    return logger
