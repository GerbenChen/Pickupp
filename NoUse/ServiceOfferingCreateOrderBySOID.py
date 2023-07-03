import sys
sys.path.append("./")
from Library.GlobalAdapter import *
import Core.ApiQuery as api_query
import json
import uuid
from itertools import combinations
import requests

def FlowTag(randomuuid,add):
    payload = json.dumps({
    "order_flow_id": randomuuid,
    "adds": add
    })
    status_code, OrderFlowId, status = api_query.ServiceOffering_OrderFlowTag(payload,True)

def OrderFlowModel(randomuuid,number):
    payload = json.dumps({
        "id": randomuuid,
        "name": "QAOrderFlow_%s" % number
    })
    status_code, OrderFlowId, status=api_query.ServiceOffering_OrderFlow_NewAll(payload,True)

FlowTagList = ["fulfillment","warehouse","outsource","self_pickup","cross_border"]
'''
for time in range(1,6):
    print (time)
    one_temp = combinations(FlowTagList, time)
    number = 0
    for i in list(one_temp):
        randomuuid = str(uuid.uuid4())
        choose_naming = "%sTags_%s" % (time,number)
        FlowTag(randomuuid,list(i))
        OrderFlowModel(randomuuid,choose_naming)
        number+=1
'''
OrderFlowLIst = []
for i in range(0,40,10):
    OrderFlowId = api_query.GetOrderFlowList(i)
    test = OrderFlowId['data']['order_flows']
    for attr in test:
        OrderFlowLIst.append(attr['id'])

#for i in range(len(OrderFlowLIst)):
#    print (OrderFlowLIst[i])
#    api_query.ServiceOfferingUpdate(OrderFlowLIst[i],"158fb289-d53c-41a5-9f68-ed664606ec54")

def delete(id):
    url = "https://admin-dev.hk.pickupp.io/?%s" % id

    payload={}
    headers = {}

    response = requests.request("DELETE", url, headers=headers, data=payload)


ServiceOfferingList = []
for i in range(20,50,10):
    OrderFlowId = api_query.GetServiceOfferingList(i)
    test = OrderFlowId['data']['services']
    for j in range(len(test)):
        ServiceOfferingList.append(test[j]['id'])
#print (ServiceOfferingList)
#print (len(ServiceOfferingList))
for ServiceOfferingID in ServiceOfferingList:
    #delete(ServiceOfferingID)
    api_query.AddServiceOfferingToMerchant(ServiceOfferingID,"2007")

