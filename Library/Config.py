#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 Config.py: The def of this file called
'''


import Library.LogFormatter as LogFormatter
from datetime import date
today_time = str(date.today())
log_file_name = "AutomationDumpLog"
dumplogger = LogFormatter.GetLogger(log_file_name=log_file_name, log_sub_dir=today_time)