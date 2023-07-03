import sys
sys.path.append("./")
from Library.GlobalAdapter import *
from Core.ApiQuery import*
import numpy as np
import configparser
import unittest


class Newconfigparser(configparser.ConfigParser):
    def __init__(self,defaults=None):
        configparser.ConfigParser.__init__(self,defaults=None)
    def optionxform(self, optionstr):
        return optionstr

class CreateAllOrder(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.config = Newconfigparser()
        self.config.read('./Config/condition.ini')
        self.setting_config = configparser.ConfigParser()
        self.setting_config.read('./Config/common_setting.ini')

    def test_CreateAllOrder(self):
        '''
        Create Order for All service types
        '''
        status = True
        servicetypelist = ["4Hours","Exchange","Express","NextDay","Collection","SameDay"]
        Orderdict = CreateOrderListAllServiceType(self.config,status,servicetypelist)
        np.save('OrderDict.npy', Orderdict)


if __name__ == '__main__':
    unittest.main() 