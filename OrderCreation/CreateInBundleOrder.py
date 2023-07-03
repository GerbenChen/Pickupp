import sys
sys.path.append("./")
from Core.ApiQuery import *
import configparser
totalstatus = True
Initconfig = configparser.ConfigParser()
Initconfig.read('./Config/condition.ini')

Bundleconfig = configparser.ConfigParser()
Bundleconfig.read('./Config/CreateInbundleOrder.ini')

def Inbundle(Servicetype):
    status_code, FirstOrderID, status = CreateOrder(Initconfig,Servicetype,totalstatus)
    status_code, SecondOrderID, status = CreateOrder(Bundleconfig,Servicetype,totalstatus)
    return [FirstOrderID, SecondOrderID]



