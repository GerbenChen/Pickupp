import sys
from urllib import response
sys.path.append("./")
import requests
import json
import configparser
import random
import Library.DecoratorHelper as DecoratorHelper
from Library.HttpApiHelper import APIController

'''
    Load all data from ShopifySetting.ini before Runig
'''
setting_config = configparser.ConfigParser()
setting_config.read('./Config/ShopifySetting.ini')
apikey = setting_config['Setting']['apikey']
accesstoken = setting_config['Setting']['accesstoken']
shopurl = setting_config['Setting']['shopurl']
apiversion = setting_config['Setting']['apiversion']
variant_id = setting_config['Setting']['variant_id']

@DecoratorHelper.FuncRecorder
def ShopifyCreateOrder(Totalstatus):
    path = "https://%s:%s@%s/admin/api/%s/orders.json" % (apikey,accesstoken,shopurl,apiversion)
    payload = json.dumps({
      "order": {
        "line_items": [
          {
            "variant_id": variant_id,
            "quantity": random.randrange(1,3)
          }
        ]
      }
    })
    headers = {
      'Content-Type': 'application/json',
    }
    # r = requests.post(path, headers=headers, data=payload)
    status_code, response = APIController.SendAPIPacket("post", path,headers,payload)
    if status_code == 201:
        OrderName = response['order']['name']
        OrderStatusUrl = response['order']['order_status_url']
        TotalPrice = response['order']['total_line_items_price']
        SinglePrice = response['order']['line_items'][0]['price']
        ShopifyOrderID = response['order']['id']
        return status_code, [OrderName,OrderStatusUrl,TotalPrice,SinglePrice,ShopifyOrderID] ,Totalstatus
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def GetShopifyOrderStatus(OrderID,TotalStatus):
    path = "https://%s:%s@%s/admin/api/%s/orders/%s.json" % (apikey,accesstoken,shopurl,apiversion,OrderID)
    status_code, response = APIController.SendAPIPacket("get", path)
    if status_code == 200:
        OrderStatus = response['order']['fulfillment_status']
        TotalPrice = response['order']['total_price']
        PaymanyStatus = response['order']['financial_status']
        return status_code, [OrderStatus,PaymanyStatus,TotalPrice],TotalStatus
    else:
        return status_code, response, False

