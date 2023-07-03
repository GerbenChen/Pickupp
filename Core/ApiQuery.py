import base64
import time
import random
import json
import uuid
import Method.CommonMethod as CommonMethod
import Library.GlobalAdapter as GlobalAdapter
import Library.DecoratorHelper as DecoratorHelper

from urllib import response
from datetime import date, datetime, timedelta
from Library.Config import dumplogger
from Library.HttpApiHelper import APIController

@DecoratorHelper.FuncRecorder
def GetMerchantAuth(setting_config, config_name):
    status_code, response = APIController.SendAPIPacket("post",GlobalAdapter.CommonVar.PortalUrl + "v2/merchant/sessions/login", None,{"email":setting_config[config_name]['email'], "password":setting_config[config_name]['password']})
    authorization = ""
    try:
        token_string = "%s:" % setting_config[config_name]['email'] + response['data']['token']
        token_string_bytes = token_string.encode("UTF-8")
        auth_byte = base64.b64encode(token_string_bytes)
        auth_string = auth_byte.decode("UTF-8")
        authorization = "Basic " + auth_string
        GlobalAdapter.AuthApiSpentTime.MerchantAuth = GlobalAdapter.FrameworkVar.ApiSpentTime
    except Exception as err:
        dumplogger.exception(err)
    if status_code == 201:
        return authorization
    else:
        return ""


@DecoratorHelper.FuncRecorder
def GetShopPortalAuth(setting_config, config_name):
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + "v2/merchant/sessions/login", None, {"email":setting_config[config_name]['email'], "password":setting_config[config_name]['password']})
    authorization = ""
    try:
        token_string = "%s:" % setting_config[config_name]['email'] + response['data']['token']
        token_string_bytes = token_string.encode("UTF-8")
        auth_byte = base64.b64encode(token_string_bytes)
        auth_string = auth_byte.decode("UTF-8")
        authorization = "Basic " + auth_string
        GlobalAdapter.AuthApiSpentTime.ShopPortalAuth = GlobalAdapter.FrameworkVar.ApiSpentTime
    except Exception as err:
        dumplogger.exception(err)
    if status_code == 201:
        return authorization
    else:
        return ""

@DecoratorHelper.FuncRecorder
def GetAdminAuth(setting_config, config_name):
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + "v2/admin/sessions/login", None, {"email":setting_config[config_name]['email'], "password":setting_config[config_name]['password']})
    authorization = ""
    try:
        token_string = "%s:" % setting_config[config_name]['email'] + response['data']['token']
        token_string_bytes = token_string.encode("UTF-8")
        auth_byte = base64.b64encode(token_string_bytes)
        auth_string = auth_byte.decode("UTF-8")
        authorization = "Basic " + auth_string
        GlobalAdapter.AuthApiSpentTime.AdminAuth = GlobalAdapter.FrameworkVar.ApiSpentTime
    except Exception as err:
        dumplogger.exception(err)
    if status_code == 201:
        return authorization
    else:
        return ""

@DecoratorHelper.FuncRecorder
def GetDAAuth(setting_config, config_name):
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + "v2/agent/login", None, {"email":setting_config[config_name]['email'], "password":setting_config[config_name]['password']})
    authorization = ""
    try:
        token_string = "%s:" % setting_config[config_name]['email'] + response['data']['token']
        token_string_bytes = token_string.encode("UTF-8")
        auth_byte = base64.b64encode(token_string_bytes)
        auth_string = auth_byte.decode("UTF-8")
        authorization = "Basic " + auth_string
        GlobalAdapter.AuthApiSpentTime.DAAuth = GlobalAdapter.FrameworkVar.ApiSpentTime
    except Exception as err:
        dumplogger.exception(err)
    if status_code == 201:
        return authorization
    else:
        return ""


def get_auth_portal_dev(devsetting_config):
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + "v2/merchant/sessions/login", None, {"email":devsetting_config['Portal_Setting']['email'], "password":devsetting_config['Portal_Setting']['password']})
    token_string = "%s:" % devsetting_config['Portal_Setting']['email'] + response['data']['token']
    token_string_bytes = token_string.encode("UTF-8")
    auth_byte = base64.b64encode(token_string_bytes)
    auth_string = auth_byte.decode("UTF-8")
    authorization = "Basic " + auth_string
    if status_code == 201:
        return authorization, True
    else:
        return authorization, False


def get_auth_portal_Shop_dev(devsetting_config):
    status_code, response = APIController.SendAPIPacket("post", devsetting_config['ShopControl_Setting']['url'] + "v2/merchant/sessions/login", None, {"email":devsetting_config['Portal_Setting']['email'], "password":devsetting_config['Portal_Setting']['password']})
    token_string = "%s:" % devsetting_config['ShopControl_Setting']['email'] + response['data']['token']
    token_string_bytes = token_string.encode("UTF-8")
    auth_byte = base64.b64encode(token_string_bytes)
    auth_string = auth_byte.decode("UTF-8")
    authorization = "Basic " + auth_string
    if status_code == 201:
        return authorization, True
    else:
        return authorization, False


def get_auth_admin_dev(devsetting_config):
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + "v2/merchant/sessions/login", None, {"email":devsetting_config['Portal_Setting']['email'], "password":devsetting_config['Portal_Setting']['password']})
    token_string = "%s:" % devsetting_config['Admin_Setting']['email'] + response['data']['token']
    token_string_bytes = token_string.encode("UTF-8")
    auth_byte = base64.b64encode(token_string_bytes)
    auth_string = auth_byte.decode("UTF-8")
    authorization = "Basic " + auth_string
    if status_code == 201:
        return authorization, True
    else:
        return authorization, False


def get_auth_dev(devsetting_config):
    status_code, response = APIController.SendAPIPacket("post", devsetting_config['DA_Setting']['url'] + "v2/agent/login", None, {"email":devsetting_config['Portal_Setting']['email'], "password":devsetting_config['Portal_Setting']['password']})
    token_string = "%s:" % devsetting_config['DA_Setting']['email'] + response['data']['token']
    token_string_bytes = token_string.encode("UTF-8")
    auth_byte = base64.b64encode(token_string_bytes)
    auth_string = auth_byte.decode("UTF-8")
    authorization = "Basic " + auth_string
    if status_code == 201:
        return authorization, True
    else:
        return authorization, False


##  Create Order
@DecoratorHelper.FuncRecorder
def CreateOrder(config, type, status, PaymentPayload=None, Single=True, promocode="",promoid="",minimum=False):
    if minimum == True:
        width, length, height, weight = 1, 1, 1, 1
    else:
        width, length, height, weight = CommonMethod.GetParcelRandomWLH()
    conditionchoose = "condition_" + type
    path = "v2/merchant/orders/single?include_transactions=true"
    if PaymentPayload != None:
            if config[conditionchoose]['value'] == "All":
                PaymentPayload = [{
                    "payment_profile_id": config[conditionchoose]['Expiryid'],
                    "payment_type": config[conditionchoose]['VerifyExpiryPaymentGateway'],
                    "amount": int(config[conditionchoose]['ExpiryAmount'])
                }]
            elif config[conditionchoose]['value']  == "Section":
                PaymentPayload = [{
                    "payment_profile_id": config[conditionchoose]['Expiryid'],
                    "payment_type": config[conditionchoose]['VerifyExpiryPaymentGateway'],
                    "amount": int(config[conditionchoose]['ExpiryAmount'])
                    },
                    {
                    "payment_profile_id": config[conditionchoose]['Creditid'],
                    "payment_type": config[conditionchoose]['VerifyCreditPaymentGateway'],
                    "amount": int(config[conditionchoose]['CreditAmount'])
                }]
            elif config[conditionchoose]['value']  == "None":
                PaymentPayload = [{
                    "payment_profile_id": config[conditionchoose]['Creditid'],
                    "payment_type": config[conditionchoose]['VerifyCreditPaymentGateway'],
                    "amount": int(config[conditionchoose]['CreditAmount'])
                }]
    if config[conditionchoose]['discount_ids'] == "" :
        DiscountList = []
    else:
        DiscountList = config[conditionchoose]['discount_ids']

    payload = json.dumps({
        "id":"",
        "pickup_contact_person":config[conditionchoose]['pickup_contact_person'],
        "pickup_address_line_1":config[conditionchoose]['pickup_address_line_1'],
        "pickup_address_line_2":config[conditionchoose]['pickup_address_line_2'],
        "pickup_contact_phone":config[conditionchoose]['pickup_contact_phone'],
        "pickup_latitude":config[conditionchoose]['pickupp_lat'],
        "pickup_longitude":config[conditionchoose]['pickupp_lng'],
        "pickup_zip_code":"",
        "pickup_city":"",
        "dropoff_contact_person":config[conditionchoose]['dropoff_contact_person'],
        "dropoff_address_line_1":config[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2":config[conditionchoose]['dropoff_address_line_2'],
        "dropoff_contact_phone":config[conditionchoose]['dropoff_contact_phone'],
        "dropoff_latitude":config[conditionchoose]['dropoff_lat'],
        "dropoff_longitude":config[conditionchoose]['dropoff_lng'],
        "dropoff_zip_code":"",
        "dropoff_city":"",
        "width":width,
        "length":length,
        "height":height,
        "weight":weight,
        "item_name":"Autobag",
        "total_parcel": 1,
        "parcel_client_reference_numbers": [],
        "pickup_time":"",
        "is_fragile":False,
        "cash_on_delivery":False,
        "cash_on_delivery_amount":"0",
        "dropoff_notes":"",
        "client_reference_number":CommonMethod.GenClientReferenceNumber(),
        "pickup_sms":False,
        "reliable":False,
        "has_delivery_note":False,
        "origin":"portal",
        "single_or_bulk":"single",
        "enforce_validation":True,
        "outsource_partner":config[conditionchoose]['outsource_partner'],
        "outsource_id":config[conditionchoose]['outsource_id'],
        "convenience_store_parcel_price":config[conditionchoose]['convenience_store_parcel_price'],
        "service_type":config[conditionchoose]['service_type'],
        "service_time":-1,
        "service_offering_id":config[conditionchoose]['service_offering_id'],
        "duty_type":"",
        "promo_code": promocode,
        "promotion_id": promoid,
        "items":[],
        "is_pickupp_care":False,
        "agent_type_id": "",
        "location_id": None,
        "dropoff_country_code": "HK",
        "dropoff_settlement": "",
        "dropoff_country": "HK",
        "payments": PaymentPayload,
        "discount_ids": DiscountList,
        "discount_code_id": config[conditionchoose]['discount_code_id'],
        "contacts":[],
    })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201 and Single==True :
        OrderID = response['data']["transactions"][0]['order_id']
        ServiceOfferingID = config[conditionchoose]['checkserviceofferingID']
        OrderNumber = response["data"]['order_number']
        return status_code, [OrderID,ServiceOfferingID,OrderNumber], True

    elif status_code == 201 and Single==False:
        OrderID = response["data"]["transactions"][0]['order_id']
        OrderNumber = response["data"]['order_number']
        return status_code, [OrderID,OrderNumber], True

    if status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return CreateOrder(config, type, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def STWithSOCreateOrder(config, type, status, width=1, length=1, height=1, weight=1):
    conditionchoose = "condition_" + type
    path = "v2/merchant/orders/single?include_transactions=true"
    payload = json.dumps({
        "id":"",
        "pickup_contact_person":config[conditionchoose]['pickup_contact_person'],
        "pickup_address_line_1":config[conditionchoose]['pickup_address_line_1'],
        "pickup_address_line_2":config[conditionchoose]['pickup_address_line_2'],
        "pickup_contact_phone":config[conditionchoose]['pickup_contact_phone'],
        "pickup_latitude":{
            "lat":config[conditionchoose]['pickupp_lat'],
            "lng":config[conditionchoose]['pickupp_lng']
        },
        "pickup_longitude":{
            "lat":config[conditionchoose]['pickupp_lat'],
            "lng":config[conditionchoose]['pickupp_lng']
        },
        "pickup_zip_code":"",
        "pickup_city":"",
        "dropoff_contact_person":config[conditionchoose]['dropoff_contact_person'],
        "dropoff_address_line_1":config[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2":config[conditionchoose]['dropoff_address_line_2'],
        "dropoff_contact_phone":config[conditionchoose]['dropoff_contact_phone'],
        "dropoff_latitude":{
            "lat":config[conditionchoose]['dropoff_lat'],
            "lng":config[conditionchoose]['dropoff_lng']
        },
        "dropoff_longitude":{
            "lat":config[conditionchoose]['dropoff_lat'],
            "lng":config[conditionchoose]['dropoff_lng']
        },
        "dropoff_zip_code":"",
        "dropoff_city":"",
        "width":width,
        "length":length,
        "height":height,
        "weight":weight,
        "item_name":"Autobag",
        "pickup_time":"",
        "is_fragile":False,
        "cash_on_delivery":False,
        "cash_on_delivery_amount":"0",
        "dropoff_notes":"",
        "client_reference_number":CommonMethod.GenClientReferenceNumber(),
        "pickup_sms":False,
        "reliable":False,
        "has_delivery_note":False,
        "origin":"portal",
        "single_or_bulk":"single",
        "enforce_validation":True,
        "outsource_partner":config[conditionchoose]['outsource_partner'],
        "outsource_id":config[conditionchoose]['outsource_id'],
        "convenience_store_parcel_price":config[conditionchoose]['convenience_store_parcel_price'],
        "service_type":config[conditionchoose]['service_type'],
        "service_time":0,
        "service_offering_id":config[conditionchoose]['service_offering_id'],
        "duty_type":"",
        "promo_code":"",
        "items":[],
        "is_pickupp_care":False,
        "contacts":[]
    })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response['data']["transactions"][0]['order_id']
        ServiceOfferingID = response["data"]["service_offering_id"]
        return status_code, [OrderID,ServiceOfferingID], True
    if status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return CreateOrder(config, type, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def ScheduleBulkCollection(config, type, status, dayvalue=0):
    width, length, height, weight = CommonMethod.GetParcelRandomWLH()
    conditionchoose = "condition_" + type
    path = "v2/merchant/orders/single?include_transactions=true"
    file_data = {
        "id": "",
        "pickup_contact_person": config[conditionchoose]['pickup_contact_person'],
        "pickup_address_line_1": config[conditionchoose]['pickup_address_line_1'],
        "pickup_address_line_2": config[conditionchoose]['pickup_address_line_2'],
        "pickup_contact_phone": config[conditionchoose]['pickup_contact_phone'],
        "pickup_latitude": config[conditionchoose]['pickup_address_line_2'],
        "pickup_longitude": config[conditionchoose]['pickup_address_line_2'],
        "pickup_zip_code": "",
        "pickup_city": "",
        "dropoff_contact_person": config[conditionchoose]['dropoff_contact_person'],
        "dropoff_address_line_1": config[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2": config[conditionchoose]['dropoff_address_line_2'],
        "dropoff_contact_phone": config[conditionchoose]['dropoff_contact_phone'],
        "dropoff_latitude": config[conditionchoose]['dropoff_latitude'],
        "dropoff_longitude": config[conditionchoose]['dropoff_longitude'],
        "dropoff_zip_code": "",
        "dropoff_city": "",
        "width": width,
        "length": length,
        "height": height,
        "weight": weight,
        "item_name": config[conditionchoose]['item_name'],
        "total_parcel": config[conditionchoose]['total_parcel'],
        "parcel_client_reference_numbers": [],
        "pickup_time": str(date.today() + timedelta(days=dayvalue))+"T10:00:00+08:00",
        "is_fragile": False,
        "cash_on_delivery": False,
        "cash_on_delivery_amount": "0",
        "dropoff_notes": "Pick up timeslot: 10:00-13:00\n",
        "client_reference_number": CommonMethod.GenClientReferenceNumber(),
        "pickup_sms": False,
        "reliable": False,
        "has_delivery_note": False,
        "origin": "portal",
        "single_or_bulk": "single",
        "enforce_validation": True,
        "outsource_partner": "",
        "outsource_id": "",
        "convenience_store_parcel_price": "",
        "service_type": config[conditionchoose]['service_type'],
        "service_time": -1,
        "service_offering_id": "",
        "duty_type": "",
        "promo_code": "",
        "items": [],
        "is_pickupp_care": False,
        "agent_type_id": "",
        "location_id": None,
        "dropoff_country_code": config[conditionchoose]['dropoff_country_code'],
        "dropoff_settlement": "",
        "dropoff_country": config[conditionchoose]['dropoff_country'],
        "payments": [],
        "dropoff_time": str(date.today() + timedelta(days=dayvalue)) + "T22:00:00+08:00",
        "pickup_timeslot_id": config[conditionchoose]['pickup_timeslot_id'],
        "contacts": []
        }
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    if GlobalAdapter.FrameworkVar.Environment == "dev":
        file_data["pickup_timeslot_id"] = config["FirstLeg_timeslot_id"][GlobalAdapter.FrameworkVar.Environment]
    payload = json.dumps(file_data)
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response['data']["parcels"][0]['order_id']
        ServiceOfferingID = config[conditionchoose]['checkserviceofferingID']
        OrderNumber = response["data"]['order_number']
        return status_code, [OrderID,ServiceOfferingID,OrderNumber], True
    elif status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return ScheduleBulkCollection(config, type, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def AdminCreateOrder(config, type, status):
    width, length, height, weight = CommonMethod.GetParcelRandomWLH()
    conditionchoose = "condition_" + type
    path = "v2/admin/orders/single"
    file_data = {
            "pickup_address_line_1": config[conditionchoose]['pickup_address_line_1'],
            "pickup_address_line_2": config[conditionchoose]['pickup_address_line_2'],
            "pickup_latitude": config[conditionchoose]['pickup_latitude'],
            "pickup_longitude": config[conditionchoose]['pickup_longitude'],
            "pickup_contact_phone": config[conditionchoose]['pickup_contact_phone'],
            "pickup_time": str(date.today() + timedelta(days=1))+"T04:00:00.000Z",
            "dropoff_address_line_1":config[conditionchoose]['dropoff_address_line_1'],
            "dropoff_address_line_2": config[conditionchoose]['dropoff_address_line_2'],
            "dropoff_latitude": config[conditionchoose]['dropoff_latitude'],
            "dropoff_longitude": config[conditionchoose]['dropoff_longitude'],
            "dropoff_contact_phone": config[conditionchoose]['dropoff_contact_phone'],
            "dropoff_time": str(date.today() + timedelta(days=1))+"T10:00:00.000Z",
            "dropoff_notes": "",
            "pickupTimeslot": "",
            "pickup_contact_person": config[conditionchoose]['pickup_contact_person'],
            "dropoff_contact_person":config[conditionchoose]['pickup_contact_person'],
            "service_type": config[conditionchoose]['service_type'],
            "weight": weight,
            "height": height,
            "length": length,
            "width": width,
            "price": 1,
            "name": config[conditionchoose]['name'],
            "as_entity_id": config[conditionchoose]['as_entity_id'],
            "origin": "admin-portal",
            "enforce_validation": True,
            "single_or_bulk": "single",
            "client_reference_number": CommonMethod.GenClientReferenceNumber()
        }
    if GlobalAdapter.FrameworkVar.Environment == "dev":
        file_data["service_offering_id"] = config["LastLeg_so_id"][GlobalAdapter.FrameworkVar.Environment]
        file_data["service_time"] = -1
        file_data["as_entity_id"] = config["LastLeg_entity_id"][GlobalAdapter.FrameworkVar.Environment]
    payload = json.dumps(file_data)
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response['data']["parcels"][0]['order_id']
        ServiceOfferingID = config["LastLeg_so_id"][GlobalAdapter.FrameworkVar.Environment]
        OrderNumber = response["data"]['order_number']
        return status_code, [OrderID,ServiceOfferingID,OrderNumber], True
    elif status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return AdminCreateOrder(config, type, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code,response, False

##  Create Order List
def CreateOrderListAllServiceType(config, status, servicetype):
    OrderDict = {}
    for service in servicetype:
        status_code, OrderID, status = CreateOrder(config, service, status)
        OrderDict[service] = OrderID
    return OrderDict


def New_CreateOrder_international(config, mode, status):
    conditionchoose = "condition_internation"
    order_template_data = CommonMethod.GetJsonData("Order_Template", "Standard")
    order_template_data["pickup_contact_person"] = config[conditionchoose]['pickup_contact_person']
    order_template_data["pickup_address_line_1"] = config[conditionchoose]['pickup_address_line_1']
    order_template_data["pickup_contact_phone"] = config[conditionchoose]['pickup_contact_phone']
    order_template_data["pickup_latitude"] = config[conditionchoose]['pickupp_lat']
    order_template_data["pickup_longitude"] = config[conditionchoose]['pickupp_lng']
    order_template_data["dropoff_contact_person"] = config[conditionchoose]['dropoff_contact_person']
    order_template_data["dropoff_address_line_1"] = config[conditionchoose]['dropoff_address_line_1']
    order_template_data["dropoff_address_line_2"] = config[conditionchoose]['dropoff_address_line_2']
    order_template_data["dropoff_contact_phone"] = config[conditionchoose]['pickup_contact_phone']
    order_template_data["dropoff_latitude"] = config[conditionchoose]['dropoff_lat']
    order_template_data["dropoff_longitude"] = config[conditionchoose]['dropoff_lng']
    order_template_data["dropoff_zip_code"] = config[conditionchoose]['dropoff_zip_code']
    order_template_data["dropoff_city"] = config[conditionchoose]['dropoff_city']
    order_template_data["service_type"] = config[conditionchoose]['service_type']
    order_template_data["service_time"] = 0
    order_template_data["service_offering_id"] = config[conditionchoose]['service_offering_id']
    path = "v2/merchant/orders/single?include_transactions=true"
    payload = json.dumps(order_template_data)
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response["transactions"][0]['order_id']
        return status_code, OrderID, True
    if status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return CreateOrder(config, type, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code, response, False


def New_CreateOrder_express(config, type, mode, status):
    conditionchoose = "condition_express"
    order_template_data = CommonMethod.GetJsonData("Order_Template", "Standard")
    order_template_data["pickup_contact_person"] = config[conditionchoose]['pickup_contact_person']
    order_template_data["pickup_address_line_1"] = config[conditionchoose]['pickup_address_line_1']
    order_template_data["pickup_contact_phone"] = config[conditionchoose]['pickup_contact_phone']
    order_template_data["pickup_latitude"] = config[conditionchoose]['pickupp_lat']
    order_template_data["pickup_longitude"] = config[conditionchoose]['pickupp_lng']
    order_template_data["dropoff_contact_person"] = config[conditionchoose]['dropoff_contact_person']
    order_template_data["dropoff_address_line_1"] = config[conditionchoose]['dropoff_address_line_1']
    order_template_data["dropoff_address_line_2"] = config[conditionchoose]['dropoff_address_line_2']
    order_template_data["dropoff_contact_phone"] = config[conditionchoose]['pickup_contact_phone']
    order_template_data["dropoff_latitude"] = config[conditionchoose]['dropoff_lat']
    order_template_data["dropoff_longitude"] = config[conditionchoose]['dropoff_lng']
    order_template_data["dropoff_zip_code"] = config[conditionchoose]['dropoff_zip_code']
    order_template_data["dropoff_city"] = config[conditionchoose]['dropoff_city']
    order_template_data["service_type"] = config[conditionchoose]['service_type']
    order_template_data["service_time"] = 0
    order_template_data["service_offering_id"] = config[conditionchoose]['service_offering_id']
    path = "v2/merchant/orders/single?include_transactions=true"
    payload = json.dumps(order_template_data)
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response["transactions"][0]['order_id']
        return status_code, OrderID, True
    else:
        return status_code, response, False


def New_CreateOrder_standard(config, conditionchoose):
    order_template_data = CommonMethod.GetJsonData("Order_Template", "Standard")
    order_template_data["pickup_contact_person"] = config[conditionchoose]['pickup_contact_person']
    order_template_data["pickup_address_line_1"] = config[conditionchoose]['pickup_address_line_1']
    order_template_data["pickup_contact_phone"] = config[conditionchoose]['pickup_contact_phone']
    order_template_data["pickup_latitude"] = config[conditionchoose]['pickupp_lat']
    order_template_data["pickup_longitude"] = config[conditionchoose]['pickupp_lng']
    order_template_data["dropoff_contact_person"] = config[conditionchoose]['dropoff_contact_person']
    order_template_data["dropoff_address_line_1"] = config[conditionchoose]['dropoff_address_line_1']
    order_template_data["dropoff_address_line_2"] = config[conditionchoose]['dropoff_address_line_2']
    order_template_data["dropoff_contact_phone"] = config[conditionchoose]['pickup_contact_phone']
    order_template_data["dropoff_latitude"] = config[conditionchoose]['dropoff_lat']
    order_template_data["dropoff_longitude"] = config[conditionchoose]['dropoff_lng']
    order_template_data["dropoff_zip_code"] = config[conditionchoose]['dropoff_zip_code']
    order_template_data["dropoff_city"] = config[conditionchoose]['dropoff_city']
    order_template_data["service_type"] = config[conditionchoose]['service_type']
    order_template_data["service_time"] = 0
    order_template_data["service_offering_id"] = config[conditionchoose]['service_offering_id']
    path = "v2/merchant/orders/single?include_transactions=true"
    payload = json.dumps(order_template_data)
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response["transactions"][0]['order_id']
        return status_code, OrderID, True
    else:
        return status_code, response, False


@DecoratorHelper.FuncRecorder
def BulkCreateOrder(condition, quantity, OrderName, TotalStatus):
    path = "v2/merchant/orders/single?include_transactions=true?"
    payload = json.dumps({
        "pickup_contact_person": condition['ShopifyCondition']['pickup_contact_person'],
        "pickup_address_line_1": condition['ShopifyCondition']['pickup_address_line_1'],
        "pickup_address_line_2": condition['ShopifyCondition']['pickup_address_line_2'],
        "pickup_contact_phone": condition['ShopifyCondition']['pickup_contact_phone'],
        "pickup_latitude": condition['ShopifyCondition']['pickup_latitude'],
        "pickup_longitude": condition['ShopifyCondition']['pickup_longitude'],
        "dropoff_contact_person": condition['ShopifyCondition']['dropoff_contact_person'],
        "dropoff_address_line_1": condition['ShopifyCondition']['dropoff_address_line_1'],
        "dropoff_address_line_2": condition['ShopifyCondition']['dropoff_address_line_2'],
        "dropoff_contact_phone": condition['ShopifyCondition']['dropoff_contact_phone'],
        "dropoff_latitude": condition['ShopifyCondition']['dropoff_latitude'],
        "dropoff_longitude": condition['ShopifyCondition']['dropoff_longitude'],
        "width": int(condition['ShopifyCondition']['width']),
        "length": int(condition['ShopifyCondition']['length']),
        "height": int(condition['ShopifyCondition']['height']),
        "weight": int(condition['ShopifyCondition']['weight']),
        "item_name": "QAShopifyTest x %s - null" % quantity,
        "parcel_client_reference_numbers": [],
        "pickup_time": str(date.today() + timedelta(days=1)) + "T13:00:00+08:00",
        "cash_on_delivery": False,
        "cash_on_delivery_amount": 0,
        "dropoff_notes": None,
        "client_reference_number": OrderName,
        "distribution_id": "",
        "is_fragile": False,
        "pickup_sms": False,
        "reliable": False,
        "has_delivery_note": False,
        "origin": "shopify",
        "enforce_validation": True,
        "single_or_bulk": "bulk",
        "address_meta": {
            "pickup_address_confidence": condition['ShopifyCondition']['pickup_address_confidence'],
            "dropoff_address_confidence": condition['ShopifyCondition']['dropoff_address_confidence'],
            "pickup_recognized_address": condition['ShopifyCondition']['pickup_recognized_address'],
            "dropoff_recognized_address": condition['ShopifyCondition']['dropoff_recognized_address']
        },
        "pickup_zip_code": condition['ShopifyCondition']['pickup_zip_code'],
        "pickup_city":condition['ShopifyCondition']['pickup_city'],
        "dropoff_city": "",
        "metadata": {
            "shopify_id": condition['ShopifyCondition']['shopify_id'],
            "shopify_email": condition['ShopifyCondition']['shopify_email'],
            "shopify_domain":condition['ShopifyCondition']['shopify_domain'],
            "status": condition['ShopifyCondition']['status'],
            "errorCount": condition['ShopifyCondition']['errorCount'],
            "orderNumber": None,
            "quotes": [],
            "quoteErrors": [],
            "responseError": None
        },
        "service_type": condition['ShopifyCondition']['service_type'],
        "service_time": condition['ShopifyCondition']['service_time'],
        "service_offering_id": "",
        "items": None,
        "is_pickupp_care": False,
        "dropoff_settlement": None,
        "contacts": []
    })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response["data"]['id']
        return status_code, OrderID, True
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def OutBoundFulfillment(condition, quantity, OrderName, ShopifyOrderID,TotalStatus):
    path = "v2/merchant/fulfillment/outbound_request?language=en"
    payload = json.dumps({
        "quantity": int(condition['ShopifyFulfillmentCondition']['quantity']),
        "total_value": int(condition['ShopifyFulfillmentCondition']['total_value']),
        "dropoff_contact_person": condition['ShopifyFulfillmentCondition']['dropoff_contact_person'],
        "dropoff_contact_phone": condition['ShopifyFulfillmentCondition']['dropoff_contact_phone'],
        "dropoff_address_line_1": condition['ShopifyFulfillmentCondition']['dropoff_address_line_1'],
        "dropoff_address_line_2": condition['ShopifyFulfillmentCondition']['dropoff_address_line_2'],
        "dropoff_latitude": float(condition['ShopifyFulfillmentCondition']['dropoff_latitude']),
        "dropoff_longitude": float(condition['ShopifyFulfillmentCondition']['dropoff_longitude']),
        "outsource_id": condition['ShopifyFulfillmentCondition']['outsource_id'],
        "service_type": condition['ShopifyFulfillmentCondition']['service_type'],
        "service_time": condition['ShopifyFulfillmentCondition']['service_time'],
        "estimated_delivery_date": str(date.today() + timedelta(days=1)) + "T13:00:00+08:00",
        "client_reference_number": OrderName,
        "outbound_items": [
            {
            "upc": condition['ShopifyFulfillmentCondition']['outbound_items_upc'],
            "serial_number": condition['ShopifyFulfillmentCondition']['outbound_items_serial_number'],
            "batch_number": condition['ShopifyFulfillmentCondition']['outbound_items_batch_number'],
            "quantity": quantity
            }
        ],
        "origin": condition['ShopifyFulfillmentCondition']['origin'],
        "metadata": {
            "shopify_id": ShopifyOrderID,
            "shopify_email": condition['ShopifyFulfillmentCondition']['shopify_email'],
            "shopify_domain": condition['ShopifyFulfillmentCondition']['shopify_domain']
        }
        })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response["data"]['outbound_request']['order_id']
        return status_code, OrderID, True
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def SubOrders(OrderID):
    trip_id = ""
    path = "v2/admin/orders/%s/sub_orders" % (OrderID)
    payload = json.dumps({
        "master_order_id": OrderID,
        "order_ids": [
            OrderID
        ]
        })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        return status_code, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def AssignPoolToDeliveryAgent(PoolID, PoolTripID, da_id):
    path = "v2/admin/admin_operation/pools/%s/accept" % PoolID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps({
        "poolTripId": PoolTripID,
        "poolId": PoolID,
        "agentId": da_id,
        "latitude": "25.0526359",
        "longitude": "121.5487137",
        "poolTripPriceMap": {}
        })
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
    if status_code == 200:
        return status_code, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def AssignToDeliveryAgent(OrderID, da_id):
    trip_id = ""
    path = "v2/admin/agents/%s/trips/%s/accept" % (da_id, OrderID)
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    time.sleep(5)
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        trip_id = response["data"]["trips"][0]['id']
        return ResponseHandler(status_code, "Assign DA success, and trip id : " + trip_id), trip_id, True
    else:
        return ResponseHandler(status_code, response), trip_id, False


def DeliveryAgentReceive(OrderID, Accesskey, status):
    path = "v2/agents/trips/%s/accept" % (OrderID)
    headers = {
        'Authorization':Accesskey,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        trip_id = response["data"]["trips"][0]['id']
        return status_code, trip_id, True
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def PUTOrderToWH(OrderID):
    path = "v2/admin/warehouse_network/orders/%s/update_destination_warehouse" % OrderID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps({
        "warehouse_id": "d9c9b748-eb0d-408a-b671-90ffba9b8012"
        })
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
    if status_code == 200:
        return status_code, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def UnableToPickup(TripID):
    path = "v2/admin/admin_operation/agentTrips/%s/unable_to_pickup" % TripID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps({
        "id": TripID,
        "utpReasonType": "UNREACHABLE",
        "utpNote": ""
        })
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
    if status_code == 200:
        return status_code, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def BackToWH(TripID):
    path = "v2/admin/admin_operation/agentTrips/%s/backToWarehouse" % TripID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps({
        "id": TripID,
        "utdReasonType": "RECIPIENT_REFUSE",
        "utdReason": {
            "key": "Package was damaged"
            }
        })
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
    if status_code == 200:
        return status_code, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def PoolTripStatus(TripID):
    path = "v2/admin/admin_query/pool_trips/%s" % TripID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        status = response['data']['status']
        return status, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def GetPoolsTripID(OrderNumber):
    path = "v2/admin/last_leg/backbone_query/pool_trips?orderNumbers%5B0%5D=" + OrderNumber
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        status = response['data']['items'][0]['id']
        return status, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def GetPoolsID(TripID):
    path = "v2/admin/admin_query/pool_trips/%s" % TripID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        status = response['data']['poolId']
        return status, True
    else:
        return status_code, False

@DecoratorHelper.FuncRecorder
def GetWHParcelsID(OrderID):
    path = "v2/admin/warehouse_network/parcels?order_id=%s" % OrderID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        status = response['data'][0]['id']
        return status, True
    else:
        return status_code, False

def DeliveryAgentReceiveInBundle(OrderID, Accesskey, status):
    path = "v2/agents/bundles/%s/accept" % (OrderID)
    headers = {
        'Authorization':Accesskey,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        trip_id = response["data"]["trips"][0]['id']
        return status_code, trip_id, True
    else:
        return status_code, response, False


def GetAdminPoolOrders():
    path = "v2/admin/agents/320/trips/available"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    return response


def CheckAdminOrderTripsStatus(OrderID):
    path = "v2/admin/orders/%s" % OrderID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    TripStatus = response['data']['trips'][0]['status']
    return TripStatus


@DecoratorHelper.FuncRecorder
def Enroute(trip_id):
    path = "v2/agent/trips/%s/enroute" % trip_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return ResponseHandler(status_code, "Enroute Order success"), True
    else:
        return ResponseHandler(status_code, response), False

@DecoratorHelper.FuncRecorder
def PoolTripEnroute(PoolTripID):
    path = "v2/agent/trips/%s/enroute" % PoolTripID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return ResponseHandler(status_code, "Enroute Order success"), True
    else:
        return ResponseHandler(status_code, response), False

@DecoratorHelper.FuncRecorder
def DropOffProcess(trip_id):
    path = "v2/agent/trips/%s/dropoff_process" % trip_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps({
        "geolocation":False,
        "qr_or_passcode":False,
        "dropoff_photo":False,
        "contactless_or_unattended":True,
        "signature_photo":False,
        "cash_on_delivery":False,
        "delivery_note":False,
        "recipient_verify_code":False
    })
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
    if status_code == 200:
        return ResponseHandler(status_code, "Drop off process success"), True
    else:
        return ResponseHandler(status_code, response), False

@DecoratorHelper.FuncRecorder
def EditAdminTripTimeStatus(config,type,trip_id):
    conditionchoose = "condition_" + type
    path = "v2/admin/trips/%s" % trip_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps({
            "pickup_latitude": config[conditionchoose]['pickup_latitude'],
            "pickup_longitude": config[conditionchoose]['pickup_longitude'],
            "dropoff_latitude": config[conditionchoose]['dropoff_latitude'],
            "dropoff_longitude": config[conditionchoose]['dropoff_longitude'],
            "status": config[conditionchoose]['status'],
            "release_time": str(date.today()+ timedelta(days=-1))+"T16:00:00.000Z",
        })
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
    if status_code == 200:
        return ResponseHandler(status_code, "Change Trips Time Status Success"), True
    else:
        return ResponseHandler(status_code, response), False

@DecoratorHelper.FuncRecorder
def DropOff(trip_id):
    path = "v2/agent/trips/%s/dropoff" % trip_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return ResponseHandler(status_code, "Drop off order success"), True
    else:
        return ResponseHandler(status_code, response), False

@DecoratorHelper.FuncRecorder
def GetAdminOrderStatus(OrderID,ST=False):
    path = "v2/admin/orders/%s" % OrderID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200 and ST == False:
        return response['data']['trips'][0]['status']
    elif status_code == 200 and ST == True:
        return response['data']['trips'][1]['status']
    else:
        return response

@DecoratorHelper.FuncRecorder
def GetAdminPoolTripStatus(PoolTripID):
    path = "v2/admin/admin_query/pool_trips/%s" % PoolTripID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return response['data']['status']
    else:
        return response

@DecoratorHelper.FuncRecorder
def GetOrderNumber(order_id):
    path = "v2/admin/orders/%s" % order_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    return_value = ""
    if order_id:
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            if response['data']['order_number']:
                return_value = response['data']['order_number']

    return return_value

@DecoratorHelper.FuncRecorder
def GetAndCheckMiniPayOut(da_id, job_number):
    minipay_out = "Minimum payout of job %s" % job_number
    path = "v2/admin/agents/%s/payrolls" % da_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    params = {
        "id":da_id,
        "start_date":(datetime.utcnow() + timedelta(days=-2)).isoformat() + 'Z',
        "end_date":(datetime.utcnow() + timedelta(days=5)).isoformat() + 'Z'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, None, params)
    if status_code == 200:
        for list_raw in range(len(response['data'])):
            if response['data'][list_raw]['description'] == minipay_out:
                return status_code, response['data'][list_raw]['description'], True
        else:
            return status_code, "Can't find Mini Pay Out record", False
    else:
        return ResponseHandler(status_code,response), False


## Promotion
@DecoratorHelper.FuncRecorder
def PromotionKeyCreate(Times,PromoName,value,category):
    path = "v2/admin/promotion"
    timenow = datetime.now()
    if category == "percentage":
        payload = json.dumps({
            "days_valid":30,
            "percentage":"10",
            "name":PromoName,
            "description":"",
            "expire_at":str(date.today() + timedelta(days=1)) + " 00:00",
            "key":"Promo%s%s" % (timenow.month, timenow.day),
            "rules":[{
                "type":"origin",
                "value": value,
                "enabled":True,
                "id":1,
                "parent_id":0,
                "children":[]
            }]
        })
    elif category == "amount":
        payload = json.dumps({
            "days_valid":30,
            "amount":"15",
            "name":PromoName,
            "description":"",
            "expire_at":str(date.today() + timedelta(days=1)) + " 00:00",
            "key":"Promo%s%s" % (timenow.month, timenow.day),
            "rules":[{
                "type":"origin",
                "value": value,
                "enabled":True,
                "id":1,
                "parent_id":0,
                "children":[]
            }]
        })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        PromotionId = response['data']['id']
        StatusCode, PromotionCode, Status = PromotionCodeCreate(PromotionId, timenow.month, timenow.day, Times)
        return StatusCode, PromotionCode, Status, PromotionId
    else:
        return status_code, "", False, ""

def InboundParcel(OrderID,ParcelID):
    PromotionCodeList = []
    path = "v2/admin/warehouse_network/parcels/%s/inbound" % ParcelID
    payload = json.dumps({
            "order_id": OrderID,
            "warehouse_id": "d9c9b748-eb0d-408a-b671-90ffba9b8012"
        })
    headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        return [status_code, response], True
    else:
        return [status_code, response], False

def PromotionCodeCreate(PromotionId, timemonth, timeday, Times):
    PromotionCodeList = []
    for times in range(Times):
        path = "v2/admin/promotion/%s/codes" % PromotionId
        payload = json.dumps({
            "promotion_id":PromotionId,
            "code":"Promo%s%s%s" % (timemonth, timeday, times),
            "expired_at":str(date.today() + timedelta(days=1)) + "T00:00:00.00Z"
        })
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
        PromotionCode = response['data']['code']
        PromotionCodeList.append(PromotionCode)

    return status_code, PromotionCodeList, True

def Discounts(config, type):
    conditionchoose = "condition_" + type
    path = "v2/admin/discounts"
    payload = json.dumps({
            "id": config[conditionchoose]["id"],
            "name": config[conditionchoose]["name"],
            "title": {
                "en": config[conditionchoose]["title"],
                "zh": "",
                "ms": "",
                "vi": "",
                "th": ""
            },
            "description": {
                "en": config[conditionchoose]["description"],
                "zh": "",
                "ms": "",
                "vi": "",
                "th": ""
            },
            "from_date": str(date.today() + timedelta(days=config[conditionchoose]["startdays"]))+"T16:00:00.000Z",
            "to_date": str(date.today() + timedelta(days=config[conditionchoose]["enddays"]))+"T16:00:00.000Z",
            "type": config[conditionchoose]["type"],
            "origin": config[conditionchoose]["origin"],
            "options": {
                "apply_for_new_merchant": False
            },
            "offers": [],
            "created_at": "",
            "updated_at": "",
            "valid": False,
            "tableData": {
                "index": config[conditionchoose]["index"],
                "id": config[conditionchoose]["tableDataid"],
                "uuid": config[conditionchoose]["tableDatauuid"]
            }
        })
    headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        return status_code, True
    else:
        return status_code, False

def removePromotionKey(PromotionId):
    path = "v2/admin/promotion/%s" % PromotionId
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return response
    else:
        return response


## Service offering
def service_offering_price(PriceConfig, status):
    path = "v2/admin/service_offering/pricings"
    randomuuid = str(uuid.uuid4())
    payload = json.dumps({
        "id":randomuuid,
        "name":PriceConfig[0],
        "fix_price":PriceConfig[1],
        "discount_rate":PriceConfig[2],
        "pickup_surcharge":PriceConfig[3],
        "express_surcharge":PriceConfig[4],
        "dropoff_surcharge":PriceConfig[5],
        "wall_surcharge":PriceConfig[6],
        "distance_model":[
            {
                "distance":PriceConfig[7],
                "price":PriceConfig[8]
            }
        ],
        "dimension_weight_model":[
            {
                "dimension":PriceConfig[9],
                "weight":PriceConfig[10],
                "price":PriceConfig[11]
            }
        ]
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        price_id = response["data"]['id']
        return status_code, price_id, True
    else:
        return status_code, response, False


def service_offering_orderflow(OrderflowConfig, status):
    path = "v2/admin/service_offering/order_flows"
    randomuuid = str(uuid.uuid4())
    payload = json.dumps({
        "id":randomuuid,
        "name":OrderflowConfig
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        orderflow_id = response["data"]['id']
        return status_code, orderflow_id, True
    else:
        return status_code, response, False


def ServiceOffering_OrderFlowTag(OrderFlowTagPayload, status):
    path = "v2/admin/backbone/order_flow_tags"
    randomuuid = str(uuid.uuid4())
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, OrderFlowTagPayload)
    if status_code == 200:
        return status_code, response, True
    else:
        return status_code, response, False


def ServiceOffering_OrderFlow_NewAll(OrderFLowPayload, status):
    path = "v2/admin/backbone/order_flows"
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, OrderFLowPayload)
    if status_code == 200:
        return status_code, response, True
    else:
        return status_code, response, False


def GetOrderFlowList(page):
    path = "v2/admin/backbone/order_flows?name=&limit=10&offset=%s" % page
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return response
    else:
        return response


def GetServiceOfferingList(page):
    path = "v2/admin/service_offering/services?query=&limit=10&offset=%s" % page
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return response
    else:
        return response


def AddServiceOfferingToMerchant(ServiceOfferingId, entityId):
    path = "v2/admin/service_offering/entity_services"
    randomuuid = str(uuid.uuid4())
    payload = json.dumps({
        "id":randomuuid,
        "entity_id":entityId,
        "service_id":ServiceOfferingId,
        "priority":10
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        return status_code, response, True
    else:
        return status_code, response, False


def ServiceOfferingUpdate(ServiceOfferingOrderFLowId, OrderFlowID):
    path = "v2/admin/backbone/service_offering_order_flows"
    payload = json.dumps({
        "order_flow_id":ServiceOfferingOrderFLowId,
        "adds":[
            OrderFlowID
        ]
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        return status_code, response, True
    else:
        return status_code, response, False


def service_offering_timeslot(timeslotConfing, status):
    path = "v2/admin/service_offering/timeslots"
    randomuuid = str(uuid.uuid4())
    payload = json.dumps({
        "id":randomuuid,
        "name":timeslotConfing[0],
        "mode":timeslotConfing[1],
        "target_1":timeslotConfing[2],
        "target_2":timeslotConfing[3],
        "value":timeslotConfing[4],
        "custom":timeslotConfing[5]
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        timeslot_id = response["data"]['id']
        return status_code, timeslot_id, True
    else:
        return status_code, response, False


def service_offering_service(serviceConfig, status):
    path = "v2/admin/service_offering/services"
    randomuuid = str(uuid.uuid4())
    payload = json.dumps({
        "id":randomuuid,
        "name":serviceConfig[0],
        "service_type":serviceConfig[1],
        "service_time":serviceConfig[2],
        "is_default":serviceConfig[3],
        "enabled":serviceConfig[4],
        "earliest_pickup_id":serviceConfig[5],
        "latest_pickup_id":serviceConfig[6],
        "earliest_dropoff_id":serviceConfig[7],
        "latest_dropoff_id":serviceConfig[8],
        "pricing_id":serviceConfig[9],
        "order_flow_id":serviceConfig[10],
        "display_name":{
            "en":serviceConfig[11],
            "zh":serviceConfig[12],
            "ms":serviceConfig[13],
            "vi":serviceConfig[14],
            "th":serviceConfig[15]
        }
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)
    if status_code == 200:
        service_offering_id = response["data"]['id']
        return status_code, service_offering_id, True
    else:
        return status_code, response, False


def DeletePriceModel(price_id):
    path = "v2/admin/service_offering/pricings/%s" % price_id
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)


def DeleteOrderFlow(order_flow_id):
    path = "v2/admin/service_offering/order_flows/%s" % order_flow_id
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)


def DeleteTimeslot(timeslot_id):
    path = "v2/admin/service_offering/timeslots/%s" % timeslot_id
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)


def DeleteServiceOffering(service_offering_id):
    path = "v2/admin/service_offering/services/%s" % service_offering_id
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)

def LinkShopify(Config):
    path = "v2/merchant/portal/link"
    payload = json.dumps({
        "shop": Config['Merchant_Shopify']['shop'],
        "type": Config['Merchant_Shopify']['type']
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 200:
        dumplogger.info("link Shopify Success")
    else:
        dumplogger.info("link Shopify Failed, Error Code : %s" % status_code)

def UnlinkShopify(Config):
    ''' UnlinkShopify : Unlink Shopify by merchant
            Return code :
                if you get error_type 007015, please check it have any ine use in database:EntityPortals.
    '''
    path = "v2/merchant/portal/unlink"
    payload = json.dumps({
        "type": Config['Merchant_Shopify']['type'],
        "value": Config['Merchant_Shopify']['shop']
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 200:
        dumplogger.info("Unlink Shopify Success")
    elif response['meta']['error_type'] == "007015":
        dumplogger.warn("Unlink Shopify Failed, The link is not belong to current merchant, Please check you account")
    else:
        dumplogger.warn("Unlink Shopify Failed, Error Code : %s" % status_code)

##SOP Purchase Order

def homepage(status):
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.ShopHomeUrl)
    if status_code == 200:
        return status_code, response, True
    else:
        return status_code, response, False


def SopSearchGuest(status):
    path = "v2/public/shops?query=Fantastic%20Beast&offset=0&limit=4"
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path)
    if status_code == 200:
        shop_name = response['data']['shops'][0]['name']
        return status_code, shop_name, True
    else:
        return status_code, response, False


def SopSearchLogin(status):
    path = "v2/public/shops?query=Fantastic%20Beast&offset=0&limit=4"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        shop_name = response['data']['shops'][0]['name']
        return status_code, shop_name, status
    else:
        return status_code, response, False


def categories(status):
    path = "v2/public/categories"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        return status_code, "Catch Categories successfully", True
    else:
        return status_code, response, False


def shop1(status):
    path = "v2/public/shops?statuses%5B0%5D=active&limit=12&offset=0&tag_id=170&primary_only=false&lat=22.309558&lng=114.190845"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        shop = response['data']
        return status_code, "Catch SHOP - 1 successfully", True
    else:
        return status_code, response, False


def shop2(status):
    path = "v2/public/shops?statuses%5B0%5D=active&limit=12&offset=0&tag_id=15&primary_only=false&lat=22.309558&lng=114.190845"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        shop = response['data']
        return status_code, "Catch SHOP - 2 successfully", True
    else:
        return status_code, response, False


def shop3(status):
    path = "v2/public/shops?statuses%5B0%5D=active&limit=12&offset=0&tag_id=7&primary_only=false&lat=22.309558&lng=114.190845"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        shop = response['data']
        return status_code, "Catch SHOP - 3 successfully", True
    else:
        return status_code, response, False


def shop4(status):
    path = "v2/public/shops?statuses%5B0%5D=active&limit=12&offset=0&tag_id=14&primary_only=false&lat=22.309558&lng=114.190845"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        shop = response['data']
        return status_code, "Catch SHOP - 4 successfully", True
    else:
        return status_code, response, False


def timeslot1(status):
    path = "v2/public/timeslots?shop_ids%5B0%5D=143"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        timeslot = response['data']
        return status_code, "Check Timeslot - 1 successfully", True
    else:
        return status_code, response, False


def timeslot2(status):
    path = "v2/public/timeslots?shop_ids%5B0%5D=43&shop_ids%5B1%5D=36&shop_ids%5B2%5D=85"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        timeslot = response['data']
        return status_code, "Check Timeslot - 2 successfully", True
    else:
        return status_code, response, False


def timeslot3(status):
    path = "v2/public/timeslots?shop_ids%5B0%5D=37&shop_ids%5B1%5D=82&shop_ids%5B2%5D=3&shop_ids%5B3%5D=2&shop_ids%5B4%5D=1"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        timeslot = response['data']
        return status_code, "Check Timeslot - 3 successfully", True
    else:
        return status_code, response, False


def timeslot4(status):
    path = "v2/public/timeslots?shop_ids%5B0%5D=92&shop_ids%5B1%5D=93&shop_ids%5B2%5D=43&shop_ids%5B3%5D=42&shop_ids%5B4%5D=85&shop_ids%5B5%5D=37&shop_ids%5B6%5D=3&shop_ids%5B7%5D=1&shop_ids%5B8%5D=44&shop_ids%5B9%5D=98&shop_ids%5B10%5D=46&shop_ids%5B11%5D=45"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        timeslot = response['data']
        return status_code, "Check Timeslot - 4 successfully", True
    else:
        return status_code, response, False


def BrowserStoreName(status):
    path = "v2/public/shops/Fantastic-Beast"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        BSN = response['data']
        return status_code, "Catch Brower Store Name successfully", True
    else:
        return status_code, response, False


def BrowserStoreInventories(status):
    path = "v2/public/shops/37/inventories?limit=500"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        BSI = response['data']
        return status_code, "Catch Brower Store Inventories successfully", True
    else:
        return status_code, response, False


def BrowserStoreCollection(status):
    path = "v2/public/shops/43/collections?limit=100&inventory_statuses%5B0%5D=active&inventory_statuses%5B1%5D=sold_out"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        BSC = response['data']
        return status_code, "Catch Brower Store Collection successfully", True
    else:
        return status_code, response, False


def PurchaseOrder(PurchaseConfig, type, promotioncode, Days, status):
    conditionchoose = "condition_" + type
    path = "v2/merchant/purchase_orders"
    payload = json.dumps({
        "payment_method":PurchaseConfig[conditionchoose]['payment_method'],
        "payment_type":PurchaseConfig[conditionchoose]['payment_type'],
        "promotion_code":promotioncode,
        "shop_id":PurchaseConfig[conditionchoose]['shop_id'],
        "dropoff_address_line_1":PurchaseConfig[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2":PurchaseConfig[conditionchoose]['dropoff_address_line_2'],
        "dropoff_lat":PurchaseConfig[conditionchoose]['dropoff_lat'],
        "dropoff_lng":PurchaseConfig[conditionchoose]['dropoff_lng'],
        "dropoff_contact_person":PurchaseConfig[conditionchoose]['dropoff_contact_person'],
        "dropoff_contact_phone":PurchaseConfig[conditionchoose]['dropoff_contact_phone'],
        "dropoff_notes":"",
        "dropoff_date":str(date.today() + timedelta(days=Days)),
        "shop_timeslot_id":PurchaseConfig[conditionchoose]['shop_timeslot_id'],
        "origin":PurchaseConfig[conditionchoose]['origin'],
        "items":[
            {
                "product_id":PurchaseConfig[conditionchoose]['product_id'],
                "quantity":1,
                "notes":"",
                "notes_label":{
                    "en":"",
                    "zh":"",
                    "ms":"",
                    "vi":"",
                    "th":""
                },
                "packs":[]
            }
        ],
        "delivery_option":PurchaseConfig[conditionchoose]['delivery_option'],
        "total_price":PurchaseConfig[conditionchoose]['total_price']
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 200:
        PurchaseId = response["data"]['id']
        PurchaseNumber = response["data"]['reference_code']
        return status_code, [PurchaseNumber, PurchaseId], True
    if status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return PurchaseOrder(PurchaseConfig, type, promotioncode, Days, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def TrackOrder(OrderNumber, status):
    path = "v2/merchant/purchase_orders/%s" % OrderNumber[0]
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        return status_code, response['data']['order_number'], True
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def TrackOrderDetail(OrderNumber, status):
    path = "v2/public/backbone/order/?order_number=%s" % OrderNumber
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path)
    if status_code == 200:
        return status_code, response['data'], True
    else:
        return status_code, response, False


def PortalShopOrder(PurchaseConfig, type, OrderNumber, Days, status):
    conditionchoose = "condition_" + type
    path = "v2/merchant/orders/single?"
    payload = json.dumps({
        "pickup_contact_person":PurchaseConfig[conditionchoose]['pickup_contact_person'],
        "pickup_address_line_1":PurchaseConfig[conditionchoose]['pickup_address_line_1'],
        "pickup_address_line_2":PurchaseConfig[conditionchoose]['pickup_address_line_2'],
        "pickup_contact_phone":PurchaseConfig[conditionchoose]['pickup_contact_phone'],
        "pickup_latitude":PurchaseConfig[conditionchoose]['pickup_latitude'],
        "pickup_longitude":PurchaseConfig[conditionchoose]['pickup_longitude'],
        "dropoff_contact_person":PurchaseConfig[conditionchoose]['dropoff_contact_person'],
        "dropoff_address_line_1":PurchaseConfig[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2":PurchaseConfig[conditionchoose]['dropoff_address_line_2'],
        "dropoff_contact_phone":PurchaseConfig[conditionchoose]['dropoff_contact_phone'],
        "dropoff_latitude":PurchaseConfig[conditionchoose]['dropoff_latitude'],
        "dropoff_longitude":PurchaseConfig[conditionchoose]['dropoff_longitude'],
        "width":PurchaseConfig[conditionchoose]['width'],
        "length":PurchaseConfig[conditionchoose]['length'],
        "height":PurchaseConfig[conditionchoose]['height'],
        "weight":PurchaseConfig[conditionchoose]['weight'],
        "pickup_notes":PurchaseConfig[conditionchoose]['pickup_notes'],
        "pickup_time":str(date.today() + timedelta(days=Days)) + "T13:00:00+08:00",
        "dropoff_time":str(date.today() + timedelta(days=Days)) + "T18:00:00+08:00",
        "dropoff_notes":"Delivery time slot: %s, 08:00 - 12:00" % str(date.today() + timedelta(days=Days)),
        "client_reference_number":OrderNumber[0],
        "origin":PurchaseConfig[conditionchoose]['origin'],
        "enforce_validation":True,
        "single_or_bulk":PurchaseConfig[conditionchoose]['single_or_bulk'],
        "purchase_order_id":OrderNumber[1],
        "metadata":{
            "sop_delivery_option":PurchaseConfig[conditionchoose]['sop_delivery_option']
        }
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.ShopAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        PurchaseOrderID = response['data']['purchase_order_id']
        PurchaseNumber = response['data']['client_reference_number']
        PortalOrderNumber = response['data']['order_number']
        OrderID = response['data']['id']
        return status_code, [PurchaseOrderID, PurchaseNumber, PortalOrderNumber, OrderID], True
    else:
        return status_code, response, False


def PortalOrderChangeStatus(PurchaseConfig, type, PurchaseOrderID, Days, status):
    conditionchoose = "condition_" + type
    path = "v2/merchant/purchase_orders/%s" % PurchaseOrderID[0]
    payload = json.dumps({
        "items":[
            {
                "packs":[],
                "id":"",
                "buyer_id":PurchaseConfig[conditionchoose]['buyer_id'],
                "seller_id":PurchaseConfig[conditionchoose]['seller_id'],
                "purchase_order_id":PurchaseOrderID[0],
                "product_id":PurchaseConfig[conditionchoose]['product_id'],
                "quantity":PurchaseConfig[conditionchoose]['quantity'],
                "subtotal":PurchaseConfig[conditionchoose]['subtotal'],
                "discount":PurchaseConfig[conditionchoose]['discount'],
                "total":PurchaseConfig[conditionchoose]['total'],
                "created_at":"",
                "updated_at":"",
                "product":{
                    "tags":[],
                    "shops":[],
                    "collections":[],
                    "packs":[],
                    "id":"",
                    "name":PurchaseConfig[conditionchoose]['name'],
                    "long_description":None,
                    "price":PurchaseConfig[conditionchoose]['price'],
                    "width":PurchaseConfig[conditionchoose]['width'],
                    "height":PurchaseConfig[conditionchoose]['height'],
                    "length":PurchaseConfig[conditionchoose]['length'],
                    "weight":PurchaseConfig[conditionchoose]['weight'],
                    "image_url":PurchaseConfig[conditionchoose]['image_url'],
                    "created_at":"",
                    "updated_at":"",
                    "link":"",
                    "entity":None,
                    "additional_notes":None,
                    "dynamic_link":None,
                    "short_description":None,
                    "entity_id":PurchaseConfig[conditionchoose]['entity_id'],
                    "type":"",
                    "original_price":PurchaseConfig[conditionchoose]['original_price'],
                    "slug":""
                },
                "notes":"",
                "shop_timeslot_id":PurchaseConfig[conditionchoose]['shop_timeslot_id'],
                "dropoff_date":str(date.today() + timedelta(days=Days)),
                "notes_label":{
                    "en":"",
                    "zh":"",
                    "ms":"",
                    "vi":"",
                    "th":""
                },
                "group_id":"",
                "purchase_order":None
            }
        ],
        "buyer_id":PurchaseConfig[conditionchoose]['buyer_id'],
        "seller_id":PurchaseConfig[conditionchoose]['seller_id'],
        "shop_id":PurchaseConfig[conditionchoose]['shop_id'],
        "order_number":PurchaseOrderID[2],
        "reference_code":PurchaseOrderID[1],
        "dropoff_contact_person":PurchaseConfig[conditionchoose]['dropoff_contact_person'],
        "dropoff_contact_phone":PurchaseConfig[conditionchoose]['dropoff_contact_phone'],
        "dropoff_address_line_1":PurchaseConfig[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2":PurchaseConfig[conditionchoose]['dropoff_address_line_2'],
        "dropoff_lat":PurchaseConfig[conditionchoose]['dropoff_latitude'],
        "dropoff_lng":PurchaseConfig[conditionchoose]['dropoff_longitude'],
        "dropoff_notes":"Delivery time slot: %s, 08:00 - 12:00" % (date.today() + timedelta(days=Days)),
        "description":PurchaseConfig[conditionchoose]['description'],
        "width":PurchaseConfig[conditionchoose]['width'],
        "length":PurchaseConfig[conditionchoose]['length'],
        "height":PurchaseConfig[conditionchoose]['height'],
        "dimension":PurchaseConfig[conditionchoose]['dimension'],
        "weight":PurchaseConfig[conditionchoose]['weight'],
        "status":PurchaseConfig[conditionchoose]['status'],
        "subtotal":PurchaseConfig[conditionchoose]['subtotal'],
        "discount":PurchaseConfig[conditionchoose]['discount'],
        "tax":PurchaseConfig[conditionchoose]['tax'],
        "delivery_price":PurchaseConfig[conditionchoose]['delivery_price'],
        "total_price":PurchaseConfig[conditionchoose]['total_price'],
        "payment_method":PurchaseConfig[conditionchoose]['payment_method'],
        "payment_status":PurchaseConfig[conditionchoose]['payment_status'],
        "transaction_id":PurchaseConfig[conditionchoose]['transaction_id'],
        "created_at":str(date.today()) + "T09:56:25.178Z",
        "updated_at":str(date.today()) + "T09:56:26.513Z",
        "buyer":{
            "warehouse_whitelist":[],
            "custom_notification":[],
            "portals":[],
            "fulfillment_warehouses":[],
            "pickup_options":{},
            "dropoff_options":{},
            "id":PurchaseConfig[conditionchoose]['buyer_id'],
            "name":PurchaseConfig[conditionchoose]['company_name'],
            "website":"",
            "phone":PurchaseConfig[conditionchoose]['buyer_phone'],
            "contact_person_name":PurchaseConfig[conditionchoose]['buyer_contact_person_name'],
            "type":"",
            "status":"",
            "email_enabled":False,
            "pay_on_success":False,
            "webhook":"",
            "owner":"",
            "created_at":"",
            "updated_at":"",
            "master_code":"",
            "core":False,
            "fragile":False,
            "delivery_note":False,
            "cash_on_delivery":False,
            "bank_name":"",
            "bank_account":"",
            "bank_holder_name":"",
            "pick_up_sms_enabled":False,
            "reliable":False,
            "tier_id":"",
            "next_tier_id":"",
            "is_tier_subscribed":False,
            "business_registration":"",
            "is_credit_line":False,
            "tier_subscribed_at":"",
            "referral":"",
            "logo":"",
            "is_prematchable":False,
            "is_own_crew":False,
            "use_own_surge":False,
            "surge_cap":"",
            "surge_step":"",
            "surge_sd":"",
            "check_client_reference_number":False,
            "skip_google":False,
            "can_outsource":False,
            "dropoff_options_old":"",
            "can_exchange":False,
            "exchange_rate":"",
            "can_initial_bundle":False,
            "public_name":"",
            "rating_sms_enabled":False,
            "enroute_sms_enabled":False,
            "exchange_destination":"",
            "reschedule_sms_enabled":False,
            "mask_item_enabled":False,
            "allow_unable_to_pickup":"",
            "pickup_options_old":"",
            "project":None,
            "fixed_outsource_partner":"",
            "freight_collect":False,
            "shopify_email_enabled":False,
            "matching_options":None,
            "sop_options":None,
            "can_multi_parcel":False,
            "tw_invoice_options":None,
            "referral_codes":None
        },
        "seller":{
            "warehouse_whitelist":[],
            "custom_notification":[],
            "portals":[],
            "fulfillment_warehouses":[],
            "pickup_options":{},
            "dropoff_options":{},
            "id":PurchaseConfig[conditionchoose]['seller_id'],
            "name":PurchaseConfig[conditionchoose]['seller_name'],
            "website":"",
            "phone":PurchaseConfig[conditionchoose]['seller_phone'],
            "contact_person_name":PurchaseConfig[conditionchoose]['seller_id'],
            "type":"",
            "status":"",
            "email_enabled":False,
            "pay_on_success":False,
            "webhook":"",
            "owner":"",
            "created_at":"",
            "updated_at":"",
            "master_code":"",
            "core":False,
            "fragile":False,
            "delivery_note":False,
            "cash_on_delivery":False,
            "bank_name":"",
            "bank_account":"",
            "bank_holder_name":"",
            "pick_up_sms_enabled":False,
            "reliable":False,
            "tier_id":"",
            "next_tier_id":"",
            "is_tier_subscribed":False,
            "business_registration":"",
            "is_credit_line":False,
            "tier_subscribed_at":"",
            "referral":"",
            "logo":"",
            "is_prematchable":False,
            "is_own_crew":False,
            "use_own_surge":False,
            "surge_cap":"",
            "surge_step":"",
            "surge_sd":"",
            "check_client_reference_number":False,
            "skip_google":False,
            "can_outsource":False,
            "dropoff_options_old":"",
            "can_exchange":False,
            "exchange_rate":"",
            "can_initial_bundle":False,
            "public_name":"",
            "rating_sms_enabled":False,
            "enroute_sms_enabled":False,
            "exchange_destination":"",
            "reschedule_sms_enabled":False,
            "mask_item_enabled":False,
            "allow_unable_to_pickup":"",
            "pickup_options_old":"",
            "project":None,
            "fixed_outsource_partner":"",
            "freight_collect":False,
            "shopify_email_enabled":False,
            "matching_options":None,
            "sop_options":None,
            "can_multi_parcel":False,
            "tw_invoice_options":None,
            "referral_codes":None
        },
        "shop":{
            "timeslots":[],
            "excluded_week_days":[
                "SATURDAY",
                "SUNDAY"
            ],
            "tags":[],
            "districts":[],
            "categories":[],
            "timeslot_date_ranges":[],
            "delivery_options":[
                "delivery",
                "self_collect"
            ],
            "id":PurchaseConfig[conditionchoose]['shop_id'],
            "entity_id":PurchaseConfig[conditionchoose]['seller_id'],
            "name":PurchaseConfig[conditionchoose]['shop_name'],
            "address_line_1":PurchaseConfig[conditionchoose]['pickup_address_line_1'],
            "address_line_2":PurchaseConfig[conditionchoose]['pickup_address_line_2'],
            "latitude":PurchaseConfig[conditionchoose]['pickup_latitude'],
            "longitude":PurchaseConfig[conditionchoose]['pickup_longitude'],
            "created_at":"",
            "updated_at":"",
            "max_days_ahead":PurchaseConfig[conditionchoose]['max_days_ahead'],
            "entity":None,
            "link":PurchaseConfig[conditionchoose]['link'],
            "dynamic_link":{
                "title":PurchaseConfig[conditionchoose]['title'],
                "description":"",
                "image_url":PurchaseConfig[conditionchoose]['shop_image_url']
            },
            "banner_image_url":PurchaseConfig[conditionchoose]['banner_image_url'],
            "description":{
                "en":PurchaseConfig[conditionchoose]['en_description'],
                "zh":"",
                "ms":"",
                "vi":"",
                "th":""
            },
            "status":PurchaseConfig[conditionchoose]['shop_status'],
            "delivery_info":{
                "en":"",
                "zh":"",
                "ms":"",
                "vi":"",
                "th":""
            },
            "profile_image_url":PurchaseConfig[conditionchoose]['profile_image_url'],
            "delivery_fee":PurchaseConfig[conditionchoose]['delivery_fee'],
            "checkout_threshold":PurchaseConfig[conditionchoose]['checkout_threshold'],
            "free_delivery_threshold":PurchaseConfig[conditionchoose]['free_delivery_threshold'],
            "group_id":PurchaseConfig[conditionchoose]['shop_id'],
            "pickup_time_buffer":PurchaseConfig[conditionchoose]['pickup_time_buffer'],
            "project":None,
            "contact_person_name":"",
            "contact_person_phone":"",
            "search_keywords":PurchaseConfig[conditionchoose]['search_keywords'],
            "ignore_holidays":False,
            "faq":{
                "en":"",
                "zh":"",
                "ms":"",
                "vi":"",
                "th":""
            },
            "slug":PurchaseConfig[conditionchoose]['slug']
        },
        "order_id":PurchaseOrderID[3],
        "shop_timeslot_id":PurchaseConfig[conditionchoose]['shop_timeslot_id'],
        "dropoff_date":str(date.today() + timedelta(days=Days)),
        "timeslot":{
            "from":"08:00",
            "to":"12:00",
            "id":PurchaseConfig[conditionchoose]['shop_timeslot_id'],
            "shop_id":PurchaseConfig[conditionchoose]['shop_id'],
            "cutoff_days":PurchaseConfig[conditionchoose]['cutoff_days'],
            "cutoff_time":"11:30",
            "type":PurchaseConfig[conditionchoose]['type']
        },
        "origin":PurchaseConfig[conditionchoose]['origin'],
        "buyer_user_id":PurchaseConfig[conditionchoose]['buyer_user_id'],
        "delivery_option":PurchaseConfig[conditionchoose]['delivery_option'],
        "payment_token":"",
        "pickup_time":str(date.today() + timedelta(days=Days)) + "T13:00:00+08:00",
        "dropoff_time":str(date.today() + timedelta(days=Days)) + "T18:00:00+08:00",
        "metadata":{
            "sop_delivery_option":PurchaseConfig[conditionchoose]['sop_delivery_option']
        }
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.ShopAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 200:
        FulfilledOrderNumber = response['data']['reference_code']
        return status_code, FulfilledOrderNumber, True
    else:
        return status_code, response, False


def AdminPurchaseOrderStatus(FulfilledOrderNumber, status):
    path = "v2/admin/purchase_orders/%s" % FulfilledOrderNumber
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        PurchaseOrderStatus = response['data']['status']
        if PurchaseOrderStatus == "fulfilled":
            return status_code, PurchaseOrderStatus, True
        else:
            return status_code, PurchaseOrderStatus, False
    else:
        return status_code, response, False


def GetMerchantPortalOrderList(Days, PurchaseOrderInfo, status):
    starttime = str(date.today())
    endtime = str(date.today() + timedelta(days=Days))
    path = "v2/admin/purchase_orders?query=&limit=1&page=0&offset=0&status=&payment_status=&" + "start_time=%s" % starttime + "T16%3A00%3A00.000Z&" + "end_time=%s" % endtime + "T15%3A59%3A59.999Z&" + "dropoff_start_time=%s" % starttime + "T00%3A00%3A00.000%2B08%3A00&" + "dropoff_end_time=%s" % endtime + "T23%3A59%3A59.999%2B08%3A00"
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    OrderId = response['data']['list'][0]['id']
    ReferenceCode = response['data']['list'][0]['reference_code']
    OrderNumber = response['data']['list'][0]['order_number']
    OrderStatus = response['data']['list'][0]['status']
    if status_code == 200:
        if [ReferenceCode, OrderId] == PurchaseOrderInfo:
            return status_code, [OrderId, ReferenceCode, OrderNumber, OrderStatus], True
        return status_code, "The Order Not In list", False
    else:
        return status_code, response, False


def GetMerchantPortalOrderListTotally(status):
    path = "v2/merchant/orders?offset=0&limit=10&query=&sort_field=created_at&sort_order=DESC"
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        MerchantPortalList = []
        for i in range(len(response['data'])):
            MerchantPortalList.append(response['data'][i]['order_number'])
        return status_code, MerchantPortalList, status
    else:
        return status_code, response, False



## payment
def TopUpMoneyInToWallet(topup_amount):
    '''
        TopUpMoneyInToWallet : use this function to top up money into wallet when money not enough
                Notice: amount in payload must be a string
    '''
    path = GlobalAdapter.CommonVar.TopUpUrl
    payload = json.dumps({
        "amount":topup_amount
    })
    headers = {
        'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        return status_code, response
    if status_code == 400 and (response["meta"]["error_type"] == "013007" or response["meta"]["error_type"] == "005008"):
        card_status_code, card_response = PaymentAPI.AddCreditCard()
        if card_status_code == 201:
            return TopUpMoneyInToWallet(topup_amount)
        else:
            return card_status_code, card_response, False
    else:
        return status_code, response


def GetStripeTokens():
    '''
        GetStripeTokens : get one time tokens from stripe
                Notice: payload must be card[number]=1234&card[exp_month]=9 not json
    '''
    payload = {
        "card[number]":"4242424242424242",
        "card[exp_month]":"9",
        "card[exp_year]":"2023",
        "card[cvc]":"314",
        "card[name]":"archertest@testarcher.io",
    }
    headers = {
        'authorization':"Bearer pk_test_IOB6ApdrpFPrr4VN5hRf34tn",
        'content-type':'application/x-www-form-urlencoded'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.StripeTokensUrl, headers, payload)
    return status_code, response

##DA flow
@DecoratorHelper.FuncRecorder
def GetDAId(setting_config, da_info):
    ''' GetAccessKeyOfDA : Get da access key from database
            Input argu:
                setting_config - which env setting you use this time.
                condition_name - which condition name from setting_config, you want to use
            Return code:
                da_id - target account's da id you want to query
    '''
    da_email = setting_config[da_info]['email']

    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    param = {
        "query":da_email,
        "limit":10,
        "offset":0,
        "sort_by":"id DESC"
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + setting_config['Api_Url']['admin_agents'], headers, None, param)
    if status_code == 200:
        for raw in range(len(response)):
            if response['data'][raw]['email'] == da_email:
                return response['data'][raw]['id']
        else:
            return ""
    else:
        return ""


def GetDAMyJob():
    path = "v2/agent/jobs/me"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return status_code, response['data']['status_history'][len(response['data']['status_history']) - 1]['status'], True
    else:
        return status_code, response, False


def GetDAMyTrips(order_id):
    '''
    GetDAMyTrips : Get order trips by order_id
            Input argu:
                order_id - order id
            Return code:
                status_code,response, boolean
    '''
    path = "v2/admin/orders/%s" % order_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        if response['data']['id'] == order_id:
            return response['data']["trips"][0]['id'], True
        else:
            return "Order id: %s can't mapping response order_id: %s" % (response['data']['id'], order_id), False
    else:
        return response, False


@DecoratorHelper.FuncRecorder
def GetDAMyOrderStatusByNumber(statuses, order_number):
    '''
    GetDAMyOrderStatusByNumber : Get order status by order_number in my order page
            Input argu:
                statuses - which status you hope to see
                order_number - which order you want to check
            Return code:
                status_code,response, boolean
    '''
    status_dict = {"ACCEPTED":"0", "ARRIVED_AT_PICKUP":"1", "ENROUTE":"2", "ARRIVED_AT_DROPOFF":"3", "BACK_TO_WAREHOUSE":"4"}

    if statuses == "ALL":
        params = {
            "statuses[0]":"ACCEPTED",
            "statuses[1]":"ARRIVED_AT_PICKUP",
            "statuses[2]":"ENROUTE",
            "statuses[3]":"ARRIVED_AT_DROPOFF",
            "statuses[4]":"BACK_TO_WAREHOUSE",
            "offset":0,
            "limit":1000
        }
    else:
        params = {
            "statuses[" + status_dict[statuses] + "]":statuses,
            "offset":0,
            "limit":1000
        }

    path = "v2/agent/trips/me"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, None, params)
    if status_code == 200:
        if statuses == "ALL":
            if response['data']:
                return status_code, response['data'], True
            else:
                return status_code, response['data'], False
        else:
            for list_raw in range(len(response['data'])):
                if response['data'][list_raw]['order_number'] == order_number:
                    return status_code, ("%s:%s" % (order_number, statuses)), True
            else:
                return status_code, "Can't Find Job %s" % order_number, False
    else:
        return status_code, response, False

def GetAvailableJob(job_id):
    '''
    GetAvailableJob : Review all available Job in pool
    '''
    path = "v2/agent/jobs/available"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        for job in range(len(response['data'])):
            if response['data'][job]['id'] == job_id:
                return status_code, job_id, True
        else:
            return status_code, "Can't Find Job %s" % job_id, False
    else:
        return status_code, response, False


def GetAllOrder():
    '''
    GetAllOrder : Review all available Order in pool
    '''
    path = "v2/agent/trips/new/all?group=force_in_pool&select=compact.availableOrder"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return status_code, len(response['data']), True
    else:
        return status_code, response, False


@DecoratorHelper.FuncRecorder
def GetDAMyJob(job_id):
    '''
    GetDAMyJob : Review Accepted Job in My order page
    '''
    path = "v2/agent/jobs/me"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        try:
            for job in range(len(response['data'])):
                if response['data'][job]['id'] == job_id:
                    return status_code, job_id, True
            else:
                return status_code, "Can't Find Job %s" % job_id, False
        except IndexError as err:
            dumplogger.exception(err)
            return status_code, response, False
        except KeyError as err:
            dumplogger.exception(err)
            return status_code, response, False
        except Exception as err:
            dumplogger.exception(err)
            return status_code, response, False
    else:
        return status_code, response, False


def GetDAFinishedJob():
    '''
    GetDAFinishedJob : Review Job History in DA app
    '''
    job_lis = []
    path = "v2/agent/jobs/me/finished"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return ResponseHandler(status_code, "Have Job History"), True
    else:
        return ResponseHandler(status_code, response), False

@DecoratorHelper.FuncRecorder
def GetAndCheckDAFinishedOrder(order_status, order_number):
    '''
    GetAndCheckDAFinishedOrder : Review Order History in DA order history
    '''
    path = "v2/agent/trips/me"
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    param = {
        "statuses[0]":"DROPPED_OFF",
        "statuses[1]":"UNABLE_TO_DELIVER",
        "statuses[2]":"COMPLETED",
        "statuses[3]":"DELIVERY_AGENT_CANCELLED",
        "statuses[4]":"MERCHANT_CANCELLED",
        "statuses[5]":"ADMIN_CANCELLED",
        "offset":0,
        "limit":1000
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, None, param)
    if status_code == 200:
        for raw in range(len(response['data'])):
            if response['data'][raw]['order_number'] == order_number and response['data'][raw]['status'] == order_status:
                return order_number, True
        else:
            return "Can't find this order: %s in history" % order_number, False
    else:
        return response, False


class OrderAPI:

    @DecoratorHelper.FuncRecorder
    def CreateOrder(so_config, service_type, payment, full_data = False):
        width, length, height, weight = CommonMethod.GetParcelRandomWLH()
        order_template_data = CommonMethod.GetJsonData("./Config/Order_Template", "Basic")
        path = "v2/merchant/orders/single?include_transactions=true"
        # order_template_data["pickup_time"] = str(date.today() + timedelta(days=1)) + "T02:00:07.000Z"
        # order_template_data["dropoff_time"] = str(date.today() + timedelta(days=1)) + "T06:00:07.000Z"
        order_template_data["width"] = width
        order_template_data["height"] = height
        order_template_data["length"] = length
        order_template_data["weight"] = weight
        order_template_data["service_type"] = service_type
        order_template_data["service_offering_id"] = so_config[service_type][GlobalAdapter.FrameworkVar.Environment]
        order_template_data["client_reference_number"] = CommonMethod.GenClientReferenceNumber()
        payload = json.dumps(order_template_data)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
        order_id = ""
        if status_code == 201:
            if full_data:
                response_data = response['data']
                order_id = response['data']['transactions'][0]['order_id']
                return response_data, order_id, True
            else:
                order_id = response['data']['transactions'][0]['order_id']
                return ResponseHandler(status_code,"Create order success, and order id is :" + order_id), order_id, True
        if status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
            if payment == "Wallet":
                topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
                if topup_status_code == 201:
                    return CreateOrder(so_config, service_type, "Wallet")
                else:
                    return ResponseHandler(topup_status_code, topup_response), order_id, False
            elif payment == "CreditCard":
                card_status_code, card_response = PaymentAPI.AddCreditCard()
                if card_status_code == 201:
                    return CreateOrder(so_config, service_type, "CreditCard")
                else:
                    return ResponseHandler(card_status_code, card_response), order_id, False
        else:
            return ResponseHandler(status_code, response), order_id, False

    @DecoratorHelper.FuncRecorder
    def CreateExpressOrder(config, service_type, isMultiple=None):
        if isMultiple:
            order_template_data = CommonMethod.GetJsonData("Order_Template", "Express_Multiple")
            order_template_data["parcel_client_reference_numbers"] = ["11", "22"]
            order_template_data["total_parcel"] = 2
        else:
            order_template_data = CommonMethod.GetJsonData("Order_Template", "Express_" + service_type)
        # order_template_data["pickup_contact_person"] = config["condition_"+service_type]['pickup_contact_person']
        # order_template_data["pickup_address_line_1"] = config["condition_"+service_type]['pickup_address_line_1']
        # order_template_data["pickup_contact_phone"] = config["condition_"+service_type]['pickup_contact_phone']
        # order_template_data["pickup_latitude"] = config["condition_"+service_type]['pickupp_lat']
        # order_template_data["pickup_longitude"] = config["condition_"+service_type]['pickupp_lng']
        # order_template_data["dropoff_contact_person"] = config["condition_"+service_type]['dropoff_contact_person']
        # order_template_data["dropoff_address_line_1"] = config["condition_"+service_type]['dropoff_address_line_1']
        # order_template_data["dropoff_address_line_2"] = config["condition_"+service_type]['dropoff_address_line_2']
        # order_template_data["dropoff_contact_phone"] = config["condition_"+service_type]['pickup_contact_phone']
        # order_template_data["dropoff_latitude"] = config["condition_"+service_type]['dropoff_lat']
        # order_template_data["dropoff_longitude"] = config["condition_"+service_type]['dropoff_lng']
        path = "v2/merchant/orders/single?include_transactions=true"
        payload = json.dumps(order_template_data)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
        if status_code == 201:
            OrderID = response['data']['transactions'][0]['order_id']
            return status_code, OrderID, True
        else:
            return status_code, response, False

    @DecoratorHelper.FuncRecorder
    def InternationalOrder(config, region, mode, status, Multi=False):
        conditionchoose = "condition_International" + region
        path = "v2/merchant/orders/single?include_transactions=true"
        itemlist = []
        if Multi == True:
            for i in range(random.randint(2, 5)):
                ItemDictFormat = {
                    "name":"AutoBag - %d" % i,
                    "count":1,
                    "currency":config[conditionchoose]['currency'],
                    "declared_value":1,
                    "hs_code":"1",
                    "weight":1}
                itemlist.append(ItemDictFormat)
        else:
            ItemDictFormat = {
                "name":"AutoBag",
                "count":1,
                "currency":config[conditionchoose]['currency'],
                "declared_value":1,
                "hs_code":"1",
                "weight":1}
            itemlist.append(ItemDictFormat)
        payload = json.dumps({
            "id":"",
            "pickup_contact_person":config[conditionchoose]['pickup_contact_person'],
            "pickup_address_line_1":config[conditionchoose]['pickup_address_line_1'],
            "pickup_address_line_2":config[conditionchoose]['pickup_address_line_2'],
            "pickup_contact_phone":config[conditionchoose]['pickup_contact_phone'],
            "pickup_latitude":config[conditionchoose]['pickup_latitude'],
            "pickup_longitude":config[conditionchoose]['pickup_longitude'],
            "pickup_zip_code":config[conditionchoose]['pickup_longitude'],
            "pickup_city":config[conditionchoose]['pickup_longitude'],
            "dropoff_contact_person":config[conditionchoose]['dropoff_contact_person'],
            "dropoff_address_line_1":config[conditionchoose]['dropoff_address_line_1'],
            "dropoff_address_line_2":config[conditionchoose]['dropoff_address_line_2'],
            "dropoff_contact_phone":config[conditionchoose]['pickup_longitude'],
            "dropoff_zip_code":config[conditionchoose]['dropoff_zip_code'],
            "dropoff_city":config[conditionchoose]['dropoff_city'],
            "width":"1",
            "length":"1",
            "height":"1",
            "weight":"1",
            "item_name":"",
            "total_parcel":1,
            "parcel_client_reference_numbers":[],
            "is_fragile":False,
            "cash_on_delivery":False,
            "cash_on_delivery_amount":"0",
            "dropoff_notes":"",
            "client_reference_number":CommonMethod.GenClientReferenceNumber(),
            "pickup_sms":False,
            "reliable":False,
            "has_delivery_note":False,
            "origin":"portal",
            "single_or_bulk":"single",
            "enforce_validation":True,
            "outsource_partner":config[conditionchoose]['outsource_partner'],
            "outsource_id":config[conditionchoose]['outsource_id'],
            "service_type":config[conditionchoose]['service_type'],
            "service_time":0,
            "service_offering_id":config["service_offering_id"][GlobalAdapter.FrameworkVar.Environment],
            "promo_code":"",
            "items":itemlist,
            "is_pickupp_care":False,
            "agent_type_id":"",
            "location_id":config[conditionchoose]['location_id'],
            "dropoff_country_code":config[conditionchoose]['dropoff_country_code'],
            "dropoff_admin_division":config[conditionchoose]['dropoff_admin_division'],
            "dropoff_settlement":config[conditionchoose]['dropoff_settlement'],
            "dropoff_country":config[conditionchoose]['dropoff_country'],
            "contacts":[]
        })
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)

        if status_code == 201:
            order_id = response["data"]['id']
            return order_id, True
        else:
            return ResponseHandler(status_code, response), False

    def PayRolls(status):
        path = "v2/admin/payrolls/confirm"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            return ResponseHandler(status_code, response), True
        else:
            return ResponseHandler(status_code, response), False


class DeliveryAgentAPI:

    def AcceptedBundleOrder(setting_config, bundle_id, bundle_dict):
        '''
        AcceptedBundleOrder : Delivery Agent Accepted Bundle
        '''
        path = "v2/agent/bundles/%s/accept" % bundle_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'content-type': 'application/x-www-form-urlencoded'
        }
        order_dict = BundleAPI.GetBundleOrderList(bundle_dict)
        order_dict.update({"price":"0"})
        payload = json.dumps(order_dict)
        dumplogger.info("Bundle Status : %s " % bundle_dict['status'])
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

        if status_code == 200:
            return response['data'], True
        else:
            return response['meta'], False

    def GetAndCheckDAOrderStatus(order_status, order_uid):
        '''
        GetAndCheckDAOrderStatus : Review Order Detail in DA My orders
        '''
        path = "v2/agent/trips/%s" % order_uid
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            if response['data']['status'] == order_status:
                return status_code, response['data']['status'], True
            else:
                return status_code, "Mapping status fail, the status you want %s, but current is %s" % (order_status, response['data']['status']), False
        else:
            return status_code, response, False

    def GetAndCheckDAOrderDetail(order_uid):
        '''
            GetAndCheckDAOrderDetail : Review Order Detail in DA My orders
        '''
        path = "v2/agent/trips/%s" % order_uid
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            return response
        else:
            return ""

    @DecoratorHelper.FuncRecorder
    def GetDAMyOrderList(limit):
        '''
            GetDAMyOrderList : Get all order in my order page
        '''
        path = "v2/agent/trips/me?&statuses[0]=ACCEPTED&statuses[1]=ARRIVED_AT_PICKUP&statuses[2]=ENROUTE&statuses[3]=ARRIVED_AT_DROPOFF&statuses[4]=BACK_TO_WAREHOUSE&offset=0&limit=%s" % str(limit)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        return status_code, response

class MerchantPortal:

    def GetOrderDetail(OrderNumber):
        path = "v2/merchant/orders/%s" % OrderNumber
        headers = {
            'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'content-type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)

        if status_code == 200:
            return response['data']
        else:
            return ""

    @DecoratorHelper.FuncRecorder
    def GetAndCheckOrderStatus(order_status, order_number):
        '''
        GetAndCheckOrderStatus : Get order status and check status by order_number in MerchantPortal
                Input argu:
                    order_status - order status we want to check this point
                    order_number - should be order_number not use order id to send http request
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/merchant/orders/%s?include_history=true&include_transactions=true" % order_number
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        time.sleep(3)
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

        if status_code == 200:
            if order_number:
                if response['data']['status'] == order_status:
                    return "Order %s Status is : %s" % (order_number,response['data']['status']), True
                elif response['data']['status'] in order_status:
                    return "Order %s Status is : %s" % (order_number, response['data']['status']), True
                elif response['data']['status'] == "SCHEDULED":
                    return "Order %s Status is : %s" % (order_number, response['data']['status']), True
                else:
                    return "Can't match order's(%s) status (corrent :%s now :%s)" % (order_number, order_status, response['data']['status']), False
            else:
                return "Can't find order's in response, please check api response", False
        else:
            return response, False

    @DecoratorHelper.FuncRecorder
    def GetTransactionHistory(order_id):
        '''
        GetTransactionHistory : Get TransactionHistory
                Input argu:
                    order_status - order status we want to check this point
                    order_number - should be order_number not use order id to send http request
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/merchant/entity/transactions?offset=0&limit=10"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        return status_code, response

    @DecoratorHelper.FuncRecorder
    def CreateStandardOrder(config, service_type, isMultiple=None):
        if isMultiple:
            order_template_data = CommonMethod.GetJsonData("Order_Template", "Standard_Multiple")
            order_template_data["parcel_client_reference_numbers"] = ["11", "22"]
            order_template_data["total_parcel"] = 2
        else:
            order_template_data = CommonMethod.GetJsonData("Order_Template", "Standard_" + service_type)
        order_template_data["pickup_contact_person"] = config[service_type]['pickup_contact_person']
        order_template_data["pickup_address_line_1"] = config[service_type]['pickup_address_line_1']
        order_template_data["pickup_contact_phone"] = config[service_type]['pickup_contact_phone']
        order_template_data["pickup_latitude"] = config[service_type]['pickupp_lat']
        order_template_data["pickup_longitude"] = config[service_type]['pickupp_lng']
        order_template_data["dropoff_contact_person"] = config[service_type]['dropoff_contact_person']
        order_template_data["dropoff_address_line_1"] = config[service_type]['dropoff_address_line_1']
        order_template_data["dropoff_address_line_2"] = config[service_type]['dropoff_address_line_2']
        order_template_data["dropoff_contact_phone"] = config[service_type]['pickup_contact_phone']
        order_template_data["dropoff_latitude"] = config[service_type]['dropoff_lat']
        order_template_data["dropoff_longitude"] = config[service_type]['dropoff_lng']
        order_template_data["dropoff_zip_code"] = config[service_type]['dropoff_zip_code']
        order_template_data["dropoff_city"] = config[service_type]['dropoff_city']
        order_template_data["service_type"] = config[service_type]['service_type']
        order_template_data["service_time"] = 0
        order_template_data["service_offering_id"] = config[service_type]['service_offering_id']
        if service_type == "SelfPickUp":
            order_template_data["outsource_id"] = "HYWH"
            order_template_data["outsource_partner"] = "warehousePickUp"
        path = "v2/merchant/orders/single?include_transactions=true"
        payload = json.dumps(order_template_data)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
        order_id = ""
        if status_code == 201:
            order_id = response['data']['transactions'][0]['order_id']
            return ResponseHandler(status_code, "Create order success, and order id is :" + order_id), order_id, True
        else:
            return ResponseHandler(status_code, response), order_id, False

    @DecoratorHelper.FuncRecorder
    def CreatePickuppCareOrder(config, country):
        # import os
        # root_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
        # order_template_data = CommonMethod.GetJsonData(root_path + "\\Config\\Order_Template", "PickuppCare_" + country)
        order_template_data = CommonMethod.GetJsonData("./Config/Order_Template", "PickuppCare_" + country)
        path = "v2/merchant/orders/single?include_transactions=true"
        if country != "HK":
            order_template_data["service_offering_id"] = config["service_offering_id"][GlobalAdapter.FrameworkVar.Environment]
        payload = json.dumps(order_template_data)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }

        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
        order_id = ""

        if status_code == 201:
            order_id = response['data']['transactions'][0]['order_id']
            return ResponseHandler(status_code, "Create order success, and order id is :" + order_id), order_id, True
        else:
            return ResponseHandler(status_code, response), order_id, False

    def GetOrderFees(order_number):
        path = "v2/merchant/fees?order_numbers[]=%s" % order_number
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
        if status_code == 200 and len(response["data"]['fees']) > 0:
            fee_price = response["data"]['fees'][0]['fee_price']
            fee_cofficient = response["data"]['fees'][0]['fee_cofficient']
            return fee_price, fee_cofficient
        else:
            return "",""

    @DecoratorHelper.FuncRecorder
    def CancelOrder(order_id,cancel_reason):
        path = "v2/merchant/orders/%s?cancellation_reason=%s" % (order_id, cancel_reason)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.PortalUrl + path, headers)

        if status_code == 200:
            return "The Order canceled , Order ID : %s" % order_id, True
        else:
            return response, False

    @DecoratorHelper.FuncRecorder
    def GetOrderListByOrderNumber(OrderNumber):
        # path = "v2/merchant/orders?offset=0&limit=10&query=%s&sort_field=created_at&sort_order=DESC" % OrderNumber
        path = "v2/merchant/backbone/orders?offset=0&limit=10&sort_field=created_at&sort_order[created_at]=DESC&query=%s" % OrderNumber
        headers = {
            'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'content-type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
        if status_code == 200:
            filter_status = response['data']["total"]
            if filter_status == 1:
                return ResponseHandler(status_code, "Total order list just has %s data in order list" % str(filter_status)), True
            else:
                return ResponseHandler(status_code, "Order list have problem, please check response, we want one data, but get %s datas" % str(filter_status)), True
        else:
            return ResponseHandler(status_code, response), False

    @DecoratorHelper.FuncRecorder
    def GetMerchantPaymentProfilePromoCredit(self):
        path = "v2/merchant/profiles"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
        if status_code == 200:
            Promolist= []
            for i in range(len(response['data']['expiry_profiles'])):
                if float(response['data']['expiry_profiles'][i]['credit']) >= 1:    
                    Promolist.append([response['data']['expiry_profiles'][i]['id'],response['data']['expiry_profiles'][i]['credit']])
            if Promolist == []:
                topup_status_code, topup_response = TopUpMoneyInToWallet("1000")
                if topup_status_code == 201:
                    return MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
                else:
                    return topup_response, False
            else:
                return Promolist, True
        else:
            return response, False

    @DecoratorHelper.FuncRecorder
    def GetMerchantPaymentProfilePromoCredit(self):
        path = "v2/merchant/profiles"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
        if status_code == 200:
            Promolist= []
            for i in range(len(response['data']['expiry_profiles'])):
                if float(response['data']['expiry_profiles'][i]['credit']) >= 1:    
                    Promolist.append([response['data']['expiry_profiles'][i]['id'],response['data']['expiry_profiles'][i]['credit']])
            if Promolist == []:
                topup_status_code, topup_response = TopUpMoneyInToWallet("1000")
                if topup_status_code == 201:
                    return MerchantPortal.GetMerchantPaymentProfilePromoCredit(self)
                else:
                    return topup_response, False
            else:
                return Promolist, True
        else:
            return response, False

    @DecoratorHelper.FuncRecorder
    def GetMerchantPaymentProfileWallet(self):
        path = "v2/merchant/profiles"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
        if status_code == 200:
            if float(response['data']['credit']['credit']) < 40:
                topup_status_code, topup_response = TopUpMoneyInToWallet("1000")
                if topup_status_code == 201:
                    return MerchantPortal.GetMerchantPaymentProfileWallet(self)
                else:
                    return topup_response, False
            else:
                return float(response['data']['credit']['credit']), True
        else:
            return response, False

class JobAPI:

    ##Job flow
    @DecoratorHelper.FuncRecorder
    def CreateJobs(config, timedict, ServiceTypeList=None):
        '''
            Create Admin Jobs Varible:
                1. Commom Config
                2. Time was used by dict
                3. ServiceType default was empty, if you want, set to list plz
        '''
        path = "v2/admin/jobs"
        servicetypelist = ServiceTypeList
        stl = []
        job_id = ""
        def ServiceTypeDictTemp(item):
            return {'service_type':item, 'service_time':-1}

        for item in servicetypelist:
            servicetypedict = ServiceTypeDictTemp(item)
            stl.append(servicetypedict)
        service_type = {"service_types":stl}

        commonset = {
            "price":config['condition']['price'],
            "capacity":config['condition']['capacity'],
            "pickup_region":config['condition']['pickup_region'],
            "dropoff_region":config['condition']['dropoff_region'],
            "release_time":timedict['release_time'],
            "release_time_changed":False,
            "start_time":timedict['start_time'],
            "start_time_changed":False,
            "end_time":timedict['end_time'],
            "end_time_changed":False,
            "cutoff_time":timedict['cutoff_time'],
            "cutoff_time_changed":False,
            "notes":"",
            "delivery_agent_type_ids":[],
            "warehouse_orders_only":config['condition']['warehouse_orders_only'],
            "allow_distribute":config['condition']['allow_distribute'],
            "projectType":config['condition']['projectType'],
            "pickup_threshold":config['condition']['pickup_threshold'],
            "dropoff_threshold":config['condition']['dropoff_threshold'],
            "min_payout":config['condition']['min_payout'],
            "is_ia":config['condition']['is_ia'],
            "is_urgent":config['condition']['is_urgent'],
            "Price_changed":config['condition']['Price_changed'],
            "Capacity_changed":config['condition']['Capacity_changed'],
            "min_payout_changed":config['condition']['min_payout_changed'],
            "order_types":[]
        }
        if ServiceTypeList == None:
            payload = commonset
        else:
            payload = {**commonset, **service_type}
        headers = {
            'authorization':GlobalAdapter.AuthVar.AdminAuth,
            'content-type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, json.dumps(payload))

        if status_code == 200:
            JobAPI.ReleaseJob(response['data']['id'])
            job_id = response['data']['id']
            return ResponseHandler(status_code, "Create job success, and job id is :" + job_id), job_id, True
        else:
            return ResponseHandler(status_code, response), job_id, False

    @DecoratorHelper.FuncRecorder
    def AssignDaToJobs(setting_config, job_id, da_id):
        ''' AssignDaToJobs : Assign Da To Jobs
                Input argu:
                    setting_config - which env order you use
                    job_id - which job id you want to add at this time
                    order_id - which order id you add to job this time
                    da_id - which DA you want to assign
                Return code:
                    status_code,response, boolean
        '''
        headers = {
            'authorization':GlobalAdapter.AuthVar.AdminAuth,
            'content-type':'application/json'
        }
        path = "v2/admin/jobs/%s/assign/%s" % (job_id, da_id)
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            return ResponseHandler(status_code, "Assign DA success, and DA id is :" + da_id), True
        else:
            return ResponseHandler(status_code, response), False

    @DecoratorHelper.FuncRecorder
    def AddOrderToJobs(setting_config, job_id, order_number, assign_price):
        ''' AddOrderToJobs : add order into Job
                Input argu:
                    setting_config - which env order you use
                    job_id - which job id you want to add at this time
                    order_id - which order id you add to job this time
                    assign_price - addmin assign order to DA's price
                Return code:
                    status_code,response, boolean
        '''
        headers = {
            'authorization':GlobalAdapter.AuthVar.AdminAuth,
            'content-type':'application/json'
        }
        payload = json.dumps({
            "admin_assign_price":assign_price
        })
        time.sleep(3)
        path = "v2/admin/jobs/%s/orders/%s" % (job_id, order_number)
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

        if status_code == 200:
            return ResponseHandler(status_code, "Add order success, and order number is :" + order_number), response, True
        else:
            return ResponseHandler(status_code, response), response, False

    @DecoratorHelper.FuncRecorder
    def ChangeJobStatus(config, job_id, job_status):
        ''' ChangeJobStatus : Change Job Status
                Input argu:
                    setting_config - which env order you use
                    job_id - which job id you want to add at this time
                    job_status - finish/cancel
                Return code:
                    status_code,response, boolean
        '''
        headers = {
            'authorization':GlobalAdapter.AuthVar.AdminAuth,
            'content-type':'application/json'
        }
        url = "v2/admin/jobs/%s/%s" % (job_id, job_status)
        if job_status == "cancel":
            status_code, response = APIController.SendAPIPacket("delete", config['Admin_Setting']['url'] + url, headers)
        else:
            status_code, response = APIController.SendAPIPacket("put", config['Admin_Setting']['url'] + url, headers)

        if status_code == 200:
            return response['data']['job_number'], True
        else:
            return response, False

    @DecoratorHelper.FuncRecorder
    def ReleaseJob(job_id):
        ''' ReleaseJob : release Job
                Input argu:
                    setting_config - which env order you use
                    job_id - which job id you want to add at this time
                Return code:
                    status_code,response, boolean
        '''
        headers = {
            'authorization':GlobalAdapter.AuthVar.AdminAuth,
            'content-type':'application/json'
        }
        payload = json.dumps({
            "id":job_id
        })
        path = "v2/admin/jobs/release_job"
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

        if status_code == 200:
            return response, True
        else:
            return response, False

    def GetAndCheckAPOrderDetail(job_id, order_id):
        '''
        GetAndCheckAPOrderDetail : Get order status and check status by order_number in AdminPortal
                Input argu:
                    job_id - which job id you want to check at this time
                    order_id - which env setting you use this time.
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/orders/%s" % order_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

        if status_code == 200:
            for list_raw in range(len(response['data']['trips'])):
                if response['data']['trips'][list_raw]['job_id'] == job_id:
                    return status_code, job_id, True
            else:
                return status_code, response, False
        else:
            return status_code, response, False


class AdminLastLegAPI:

    def GetTripListByOrderNumber(setting_config, order_number):
        '''
        GetTripListByOrderNumber : Get Wallet History
                Input argu:
                    merchant_id : merchant information from setting.ini
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/admin_query/pool_trips"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        params = {
            "limit":10,
            "page":1,
            "orderNumber":order_number
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, None, params)

        if status_code == 200:
            return response
        else:
            return response

    @DecoratorHelper.FuncRecorder
    def GetTripPoolListByOrderNumber(setting_config, order_number):
        '''
        GetTripPoolListByOrderNumber : Get Trip Pool List By OrderNumber
                Input argu:
                    order_number : order number form LL
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/admin_query/pool_trips"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        params = {
            "limit":10,
            "page":1,
            "orderNumber":order_number
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, None, params)

        if status_code == 200:
            return response['data']['items'][0]['id'], True
        else:
            return response, True

    def GetBundleIdByNewTripId(setting_config, new_trip_id):
        path = "v2/admin/admin_query/pool_trips/%s" % new_trip_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

        if status_code == 200:
            bundle_id = response['data']['poolId']
            return bundle_id, True
        else:
            return "", False

    def GetBundleListByBundleId(setting_config, bundle_id):
        '''
        GetBundleListByBundleId : Get Bundle Pool List
                Input argu:
                    bundle_id : get from new trip id
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/admin_query/bundle_pools/%s" % bundle_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

        if status_code == 200:

            return response['data']['serviceOfferingId'], True
        else:
            return response, False



class AdminMerchantAPI:

    @DecoratorHelper.FuncRecorder
    def GetMerchantId(setting_config, merchant_info):
        '''
        GetMerchantId : Get merchant id
                Input argu:
                    merchant_info : merchant information from setting.ini
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/entities"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        params = {
            "query":setting_config[merchant_info]['email'],
            "limit":10,
            "offset":0,
            "has_shop":"false",
            "sort_by":"id",
            "sort_direction":"DESC"
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, None, params)

        if status_code == 200:
            return response['data'][0]['id']
        else:
            return ""

    @DecoratorHelper.FuncRecorder
    def UpdateMerchantSetting(setting_config, merchant_id, pickup_drop_setting=None):
        '''
        UpdateMerchantSetting : Get merchant id
                Input argu:
                    setting_config - which env setting you use this time.
                    merchant_id - merchant id
                    pickup_drop_setting - default was all false, if you need, set to dict plz
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/entities/%s" % merchant_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        if pickup_drop_setting == None:
            payload = CommonMethod.GetJsonData("merchants_default_setting", "Basic")
        else:
            payload = pickup_drop_setting
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, json.dumps(payload))

        if status_code == 200:
            return merchant_id, response, True
        else:
            return status_code, response, False

    @DecoratorHelper.FuncRecorder
    def UpdateServiceOffering(setting_config, merchant_id, service_offering_id):
        randomuuid = str(uuid.uuid4())
        path = "v2/admin/service_offering/entity_services"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        payload = {
            "id":randomuuid,
            "entity_id":merchant_id,
            "service_id":service_offering_id,
            "priority":0
        }
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, json.dumps(payload))

        if status_code == 200:
            return status_code, response, True
        else:
            return status_code, response, False

    @DecoratorHelper.FuncRecorder
    def DeleteServiceOffering(setting_config, entity_services_id):
        path = "v2/admin/service_offering/entity_services/%s" % entity_services_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)

        if status_code == 200:
            return status_code, True
        else:
            return status_code, False

    @DecoratorHelper.FuncRecorder
    def GetWalletHistory(merchant_id):
        '''
        GetWalletHistory : Get Wallet History
                Input argu:
                    merchant_id : merchant information from setting.ini
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/entities/%s/transactions" % merchant_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        params = {
            "limit":10,
            "offset":0,
            "order":"DESC"
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, None, params)
        return status_code, response


class AdminPortal:

    @DecoratorHelper.FuncRecorder
    def GetBundleIdByOrder(setting_config, order_id):
        path = "v2/admin/orders/%s" % order_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            bundle_id = response['data']['trips'][0]['bundle_id']
            return bundle_id, True
        else:
            return "", False

    @DecoratorHelper.FuncRecorder
    def UnableToPickup(trip_id):
        path = "v2/admin/admin_operation/agentTrips/%s/unable_to_pickup" % trip_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        payload = json.dumps({
            "id": trip_id,
            "utpReasonType": "UNREACHABLE",
            "utpNote": ""
            })
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
        if status_code == 200:
            return ResponseHandler(status_code, "Unable To Pickup : %s" % trip_id), True
        else:
            return ResponseHandler(status_code, response), True

class AdminOrderAPI:

    def GetAdminOrderStatus(order_id):
        path = "v2/admin/orders/%s" % order_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            return response['data']['status']
        else:
            return response

    @DecoratorHelper.FuncRecorder
    def CancelOrder(EntityID, OrderID, refund_amount = 0):
        path = "v2/admin/entities/%s/orders/%s?refund=%d&cancellation_reason=&cancellation_detail=" % (EntityID, OrderID,refund_amount)
        headers = {
            'authorization':GlobalAdapter.AuthVar.AdminAuth,
            'content-type':'application/json'
        }
        time.sleep(5)
        status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            return ResponseHandler(status_code, "The Order canceled by Merchant (%s), Order ID : %s" % (EntityID,OrderID)), True
        else:
            return ResponseHandler(status_code, "Cancel Order Fail by Merchant (%s), Order ID : %s" % (EntityID,OrderID)), False

    @DecoratorHelper.FuncRecorder
    def GetAndCheckOrderStatus(order_status, order_id):
        path = "v2/admin/orders/%s" % order_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        time.sleep(3)
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        #response = r.json()
        if status_code == 200:
            if response['data']['status'] == order_status:
                return "Order (%s) Status is : %s" % (order_id,response['data']['status']), True
            else:
                return "Can't match order's(%s) status (corrent :%s now :%s)" % (order_id, order_status,response['data']['status']), True
        else:
            return response, False

    @DecoratorHelper.FuncRecorder
    def GetAndCheckTripStatus(order_status, trip_id):
        path = "v2/admin/admin_query/pool_trips/%s" % trip_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        time.sleep(3)
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            if response['data']['status'] == order_status:
                return "Trip (%s) Status is : %s" % (trip_id, response['data']['status']), True
            else:
                return "Can't match order's(%s) status (corrent :%s now :%s)" % (trip_id, order_status,response['data']['status']), True
        else:
            return ResponseHandler(status_code, response), False

    @DecoratorHelper.FuncRecorder
    def ItemNotReceived(trip_id):
        path = "/v2/admin/trips/%s/item_not_received" % trip_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        time.sleep(3)
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        if status_code == 200:
            return ResponseHandler(status_code, "Item Not Received : %s" % trip_id), True
        else:
            return ResponseHandler(status_code, response), True

    @DecoratorHelper.FuncRecorder
    def UpdateOrderDetail(order_id, response_data):
        width, length, height, weight = CommonMethod.GetParcelRandomWLH()
        order_template_data = CommonMethod.GetJsonData("./Config/Order_Template", "OrderUpdate_BackBone")
        path = "v2/admin/backbone/orders/%s" % order_id
        order_template_data["pickup_time"] = str(date.today() + timedelta(days=1)) + "T02:00:07.000Z"
        order_template_data["dropoff_time"] = str(date.today() + timedelta(days=1)) + "T06:00:07.000Z"
        order_template_data["width"] = width
        order_template_data["height"] = height
        order_template_data["length"] = length
        order_template_data["weight"] = weight
        order_template_data["service_offering_id"] = response_data["service_offering_id"]
        order_template_data["client_reference_number"] = response_data["client_reference_number"]
        payload = json.dumps(order_template_data)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

        if status_code == 200:
            return ResponseHandler(status_code, "update order success, orderid : %s" % str(order_id)), True
        else:
            return ResponseHandler(status_code, response), False

class AdminWareHousesAPI:

    @DecoratorHelper.FuncRecorder
    def GetWareHousesID(warehouses_name):
        path = "/v2/admin/warehouses"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        payload = json.dumps({
            "limit": 10,
            "offset":0,
            "name":warehouses_name,
            "statuses[0]": "ACTIVE",
            "sort_by": "created_at",
            "sort_order": "DESC",
            "page": 0
            })
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
        if status_code == 200:
            warehouses_id = response["data"][0]["id"]
            return ResponseHandler(status_code, "Get Ware Houses ID : %s" % warehouses_id), True
        else:
            return ResponseHandler(status_code, response), True

    @DecoratorHelper.FuncRecorder
    def Inbound(warehouses_id,order_number,warehouse_marking = None,barcode = None):
        path  = "v2/admin/warehouses/%s/inbound/%s" % (warehouses_id, order_number)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        payload = json.dumps({
            "warehouse_marking": warehouse_marking,
            "barcode":barcode,
            })
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers,payload)
        if status_code == 200:
            return ResponseHandler(status_code, "Order Inbound Success"), True
        else:
            return ResponseHandler(status_code, response), True


class BundleAPI:

    def AddOrderToBundle(setting_config, bundle_id, order_number):
        '''
        AddOrderToBundle : Get merchant id
                Input argu:
                    setting_config - which env setting you use this time.
                    merchant_id - merchant id
                    pickup_drop_setting - default was all false, if you need, set to dict plz
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/bundles/%s/orders/%s" % (bundle_id, order_number)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)

        if status_code == 200:
            return status_code, response, True
        else:
            return status_code, response, False

    def AssignDAToBundle(setting_config, bundle_id, da_id):
        '''
        AssignDAToBundle : Get merchant id
                Input argu:
                    setting_config - which env setting you use this time.
                    merchant_id - merchant id
                    pickup_drop_setting - default was all false, if you need, set to dict plz
                Return code:
                    status_code,response, boolean
        '''
        bundle_dict = BundleAPI.GetBundleInformation(setting_config, bundle_id)
        dumplogger.info("Bundle Status : %s " % bundle_dict['status'])
        if bundle_dict['status'] != "READY" or bundle_dict['status'] != "CONTACTING_AGENT":
            bundle_dict = BundleAPI.ChangeBundleStatus(setting_config, bundle_id, bundle_dict)

        path = "v2/admin/bundles/%s/agents/%s" % (bundle_id, da_id)
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        order_dict = BundleAPI.GetBundleOrderList(bundle_dict)
        payload = json.dumps(order_dict)
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

        if status_code == 200:
            return "bundle_id : %s, Da_id : %s" % (bundle_id, str(da_id)), True
        else:
            return response, False

    def ChangeBundleStatus(setting_config, bundle_id, bundle_dict):
        '''
        AssignDAToBundle : Get merchant id
                Input argu:
                    setting_config - which env setting you use this time.
                    merchant_id - merchant id
                    pickup_drop_setting - default was all false, if you need, set to dict plz
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/bundles/%s" % bundle_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }

        bundle_dict.update({"status":"READY"})
        bundle_dict.update({"release_time":datetime.utcnow().isoformat() + 'Z'})

        payload = json.dumps(bundle_dict)
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

        if status_code == 200:
            return response['data']['bundle']
        else:
            return ""

    def GetBundleInformation(setting_config, bundle_id):
        '''
        GetBundleInformation : Get merchant id
                Input argu:
                    setting_config - which env setting you use this time.
                    merchant_id - merchant id
                    pickup_drop_setting - default was all false, if you need, set to dict plz
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/bundles/%s" % bundle_id
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)

        if status_code == 200:
            return response['data']['bundle']
        else:
            return ""

    def GetBundleOrderList(bundle_dict):
        my_dict = {}
        for order_raw in range(len(bundle_dict['trips'])):
            str_key = str("trip_ids[" + str(order_raw) + "]")
            my_dict.update({str_key:bundle_dict['trips'][order_raw]['id']})
        return my_dict


class ServiceOfferingAPI:

    def GetServiceOfferingInfo(setting_config, so_setting_name):
        '''
        GetServiceOfferingInfo : get service offering data
                Input argu:
                    so_setting_name - input service offering name
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/service_offering/services"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        payload = {
            'query':so_setting_name,
            'limit':10,
            'offset':0
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers, json.dumps(payload))

        if status_code == 200:
            return status_code, response['data']['services'], True
        else:
            return status_code, response, False

    def UpdateServiceOffering(setting_config, service_offering_info):
        '''
        UpdateServiceOffering : Update service offering
                Input argu:
                    service_offering_info - data come from Service_Offering_Setting.json
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/service_offering/services"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        # r = requests.post(GlobalAdapter.CommonVar.AdminUrl + path, headers=headers, data=json.dumps(service_offering_info))
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, json.dumps(service_offering_info))

        if status_code == 200:
            return status_code, response, True
        else:
            return status_code, response, False

    def UpdateGroupedConfigurations(setting_config, grouped_configurations_info):
        '''
        UpdateGroupedConfigurations : Update Grouped Configurations
                Input argu:
                    grouped_configurations_info - data come from Service_Offering_Setting.json
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/service_offering/grouped_configurations"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        # r = requests.post(GlobalAdapter.CommonVar.AdminUrl + path, headers=headers, data=json.dumps(grouped_configurations_info))
        # 
        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, json.dumps(grouped_configurations_info))
        if status_code == 200:
            return status_code, response, True
        else:
            return status_code, response, False

    def UpdateServiceOfferingOrderFlows(setting_config, so_order_flows_info):
        '''
        UpdateServiceOfferingOrderFlows : Update service offering order flows setting
                Input argu:
                    so_order_flows_info - data come from Service_Offering_Setting.json
                Return code:
                    status_code,response, boolean
        '''
        path = "v2/admin/backbone/service_offering_order_flows"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type':'application/json'
        }
        # r = requests.post(GlobalAdapter.CommonVar.AdminUrl + path, headers=headers, data=json.dumps(so_order_flows_info))

        status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.AdminUrl + path, headers, json.dumps(so_order_flows_info))
        if status_code == 200:
            return status_code, response, True
        else:
            return status_code, response, False


class PaymentAPI:

    def AddCreditCard(self):
        '''
            AddCreditCard : add credit card when you need card to top up or payment.
                    Notice: please get one time token first, and send request after get token.
        '''
        tokens_status, tokens_response = GetStripeTokens()

        if tokens_status == 200:
            path = GlobalAdapter.CommonVar.CreditCardUrl
            payload = json.dumps({
                "expire_date":"11/30",
                "token":tokens_response["id"],
                "vendor":"stripe"
            })
            headers = {
                'authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
                'content-type':'application/json'
            }
            status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
            if status_code == 201:
                return status_code, response
        else:
            return tokens_status, tokens_response

def Special_Settings(special_setting_info, merchantID):
    path = "v2/admin/entities/%s" % merchantID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps(special_setting_info)
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

    if status_code == 200:
        return status_code, response, True
    else:
        return status_code, response, False


def TierCapability(tier_data, AgentID, status):
    path = "v2/admin/agents/tiers/%s" % AgentID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    payload = json.dumps(tier_data)
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)


    if status_code == 200:
        return status_code, response, status
    else:
        return status_code, response, False

class TripsSolution:
    @DecoratorHelper.FuncRecorder
    def CheckAdminTripsList(AgentID,Tripstatus):
        path = "v2/admin/agents/%s/trips?statuses[0]=%s&limit=100&offset=0" % (AgentID, Tripstatus)
        headers = {
            'Authorization': GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type': 'application/json'
        }
        TripsIDList = []
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)
        try:
            DataList = response['data']
            for index in range(len(DataList)):
                TripsID = response['data'][index]['trips'][0]['id']
                TripsIDList.append(TripsID)
        except KeyError as err:
            dumplogger.exception(err)
        except Exception as err:
            dumplogger.exception(err)
        return TripsIDList

    @DecoratorHelper.FuncRecorder
    def ClickAllTripsToEnroute(AgentID, TripsID):
        path = "v2/admin/agents/%s/trips/%s/enroute" % (AgentID, TripsID)
        headers = {
            'Authorization': GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type': 'application/json'
        }
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)


    @DecoratorHelper.FuncRecorder
    def ClickAllTripsToDropoff(AgentID, TripsID):
        path = "v2/admin/agents/%s/trips/%s/dropoff" % (AgentID, TripsID)
        headers = {
            'Authorization': GlobalAdapter.AuthVar.AdminAuth,
            'Content-Type': 'application/json'
        }
        status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers)


@DecoratorHelper.FuncRecorder
def InternationalHKtoOther(config, region, mode, status,Multi=False):
    width, length, height, weight = CommonMethod.GetParcelRandomWLH()
    conditionchoose = "condition_International" + region
    path = "v2/merchant/orders/single?include_transactions=true"
    itemlist = []
    if Multi == True:
        for i in range(random.randint(2,5)):
            ItemDictFormat = { 
                "name": "AutoBag - %d" % i,
                "count": 1,
                "currency": config[conditionchoose]['currency'],
                "declared_value": 1,
                "hs_code": "1",
                "weight": 1}
            itemlist.append(ItemDictFormat)
    else:
        ItemDictFormat = { 
            "name": "AutoBag" ,
            "count": 1,
            "currency": config[conditionchoose]['currency'],
            "declared_value": 1,
            "hs_code": "1",
            "weight": 1}
        itemlist.append(ItemDictFormat)
    payload = json.dumps({
        "id": "",
        "pickup_contact_person": config[conditionchoose]['pickup_contact_person'],
        "pickup_address_line_1": config[conditionchoose]['pickup_address_line_1'],
        "pickup_address_line_2": config[conditionchoose]['pickup_address_line_2'],
        "pickup_contact_phone": config[conditionchoose]['pickup_contact_phone'],
        "pickup_latitude": config[conditionchoose]['pickup_latitude'],
        "pickup_longitude": config[conditionchoose]['pickup_longitude'],
        "pickup_zip_code": config[conditionchoose]['pickup_longitude'],
        "pickup_city": config[conditionchoose]['pickup_longitude'],
        "dropoff_contact_person": config[conditionchoose]['dropoff_contact_person'],
        "dropoff_address_line_1": config[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2": config[conditionchoose]['dropoff_address_line_2'],
        "dropoff_contact_phone": config[conditionchoose]['pickup_longitude'],
        "dropoff_zip_code": config[conditionchoose]['dropoff_zip_code'],
        "dropoff_city": config[conditionchoose]['dropoff_city'],
        "width": width,
        "length": length,
        "height": height,
        "weight": weight,
        "item_name": "",
        "total_parcel": 1,
        "parcel_client_reference_numbers": [],
        "is_fragile": False,
        "cash_on_delivery": False,
        "cash_on_delivery_amount": "0",
        "dropoff_notes": "",
        "client_reference_number": CommonMethod.GenClientReferenceNumber(),
        "pickup_sms": False,
        "reliable": False,
        "has_delivery_note": False,
        "origin": "portal",
        "single_or_bulk": "single",
        "enforce_validation": True,
        "outsource_partner": config[conditionchoose]['outsource_partner'],
        "outsource_id": config[conditionchoose]['outsource_id'],
        "service_type": config[conditionchoose]['service_type'],
        "service_time": 0,
        "service_offering_id": config["service_offering_id"][GlobalAdapter.FrameworkVar.Environment],
        "promo_code": "",
        "items": itemlist,
        "is_pickupp_care": False,
        "agent_type_id": "",
        "location_id": config[conditionchoose]['location_id'],
        "dropoff_country_code": config[conditionchoose]['dropoff_country_code'],
        "dropoff_admin_division": config[conditionchoose]['dropoff_admin_division'],
        "dropoff_settlement": config[conditionchoose]['dropoff_settlement'],
        "dropoff_country": config[conditionchoose]['dropoff_country'],
        "contacts": []
        })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)     
    if status_code == 201:
        OrderID = response["data"]['id']
        OrderNumber = response["data"]['order_number']
        return status_code, [OrderID,OrderNumber], True
    if status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return CreateOrder(config, type, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def ExpressSingleOrder(config, size, mode, status):
    conditionchoose = "condition_%s" % size
    path = "v2/merchant/orders/single?include_transactions=true"
    payload = json.dumps({
        "id": "",
        "pickup_contact_person": config[conditionchoose]['pickup_contact_person'],
        "pickup_address_line_1": config[conditionchoose]['pickup_address_line_1'],
        "pickup_address_line_2": config[conditionchoose]['pickup_address_line_2'],
        "pickup_contact_phone": config[conditionchoose]['pickup_contact_phone'],
        "pickup_latitude": config[conditionchoose]['pickup_latitude'],
        "pickup_longitude": config[conditionchoose]['pickup_longitude'],
        "pickup_zip_code": config[conditionchoose]['pickup_longitude'],
        "pickup_city": config[conditionchoose]['pickup_longitude'],
        "dropoff_contact_person": config[conditionchoose]['dropoff_contact_person'],
        "dropoff_address_line_1": config[conditionchoose]['dropoff_address_line_1'],
        "dropoff_address_line_2": config[conditionchoose]['dropoff_address_line_2'],
        "dropoff_contact_phone": config[conditionchoose]['pickup_longitude'],
        "dropoff_latitude": config[conditionchoose]['dropoff_latitude'],
        "dropoff_longitude": config[conditionchoose]['dropoff_longitude'],
        "dropoff_zip_code": config[conditionchoose]['dropoff_zip_code'],
        "dropoff_city": config[conditionchoose]['dropoff_city'],
        "width": config[conditionchoose]['width'],
        "length": config[conditionchoose]['length'],
        "height": config[conditionchoose]['height'],
        "weight": config[conditionchoose]['weight'],
        "item_name": config[conditionchoose]['item_name'],
        "total_parcel": config[conditionchoose]['total_parcel'],
        "parcel_client_reference_numbers": [],
        "is_fragile": False,
        "cash_on_delivery": False,
        "cash_on_delivery_amount": "0",
        "dropoff_notes": "",
        "client_reference_number": "",
        "pickup_sms": False,
        "reliable": False,
        "has_delivery_note": False,
        "origin": "portal",
        "single_or_bulk": "single",
        "enforce_validation": True,
        "outsource_partner": "",
        "outsource_id": "",
        "convenience_store_parcel_price": "",
        "service_type": "express",
        "service_time": 120,
        "service_offering_id": config[conditionchoose]['service_offering_id'],
        "duty_type": "",
        "promo_code": "",
        "items": [],
        "is_pickupp_care": False,
        "agent_type_id": "",
        "location_id": None,
        "dropoff_country_code": config[conditionchoose]['dropoff_country_code'],
        "dropoff_settlement": config[conditionchoose]['dropoff_settlement'],
        "dropoff_country": config[conditionchoose]['dropoff_country'],
        "contacts": []
        })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("post", GlobalAdapter.CommonVar.PortalUrl + path, headers, payload)
    if status_code == 201:
        OrderID = response["data"]['id']
        OrderNumber = response["data"]['order_number']
        return status_code, [OrderID,OrderNumber], True
    if status_code == 400 and (response["meta"]["error_type"] == "005003" or response["meta"]["error_type"] == "005005"):
        topup_status_code, topup_response = TopUpMoneyInToWallet(GlobalAdapter.CommonVar.TopUpAmount)
        if topup_status_code == 201:
            return CreateOrder(config, type, status)
        else:
            return topup_status_code, topup_response, False
    else:
        return status_code, response, False

def SetupOrderDetail(OrderID):
    path = "v2/admin/orders/%s" % OrderID
    payload = json.dumps({
        "pickup_address_line_1": "香港鶴翔街維港中心1座",
        "pickup_address_line_2": "1",
        "pickup_contact_person": "Gerben",
        "pickup_contact_phone": "87654321",
        "pickup_contact_company": "Pickupp",
        "pickup_zip_code": "",
        "pickup_city": "HK",
        "pickup_district_level_1": "L1_KOWLOON_WEST",
        "pickup_district_level_2": "L2_YAU_TSIM_MONG",
        "pickup_district_level_3": "L3_HOK_YUEN",
        "pickup_notes": "AutoBag",
        "dropoff_address_line_1": "香港鶴園鶴翔街1號維港中心1座ß",
        "dropoff_address_line_2": "1",
        "dropoff_contact_person": "Gerben",
        "dropoff_contact_phone": "87654321",
        "dropoff_contact_company": "",
        "dropoff_zip_code": "",
        "dropoff_city": "HK",
        "dropoff_district_level_1": "L1_KOWLOON_WEST",
        "dropoff_district_level_2": "L2_YAU_TSIM_MONG",
        "dropoff_district_level_3": "L3_HOK_YUEN",
        "dropoff_notes": "",
        "client_reference_number": "",
        "pickup_latitude": "22.310138",
        "pickup_longitude": "114.191588",
        "dropoff_latitude": "22.309559",
        "dropoff_longitude": "114.190843",
        "width": "1",
        "height": "1",
        "length": "1",
        "weight": "1",
        "cash_on_delivery": False,
        "cash_on_delivery_amount": "0",
        "entity_id": "1311",
        "is_fragile": False,
        "pickup_sms": False,
        "core_merchant": True,
        "promo_order": True,
        "reliable": True,
        "status": "CONTACTING_AGENT",
        "pay_on_success": True,
        "has_delivery_note": False,
        "is_in_available_pool": True,
        "metadata":{
            "webhook": False,
            "own_crew": True,
            "fcm_token": "",
            "shopify_id": "",
            "shopify_email": "",
            "shopify_domain": "",
            "basic_rate": "40",
            "weight_rate": "0",
            "express_rate": "",
            "discount_rate": "0",
            "distance_rate": "0",
            "wall_surcharge": "0",
            "adjustment_rate": "0",
            "pickup_surcharge": "0",
            "reliability_rate": "0",
            "dropoff_surcharge": "0",
            "warehouse_marking": "",
            "attempts": "",
            "utd_reason": "",
            "exchange_rate": "",
            "next_order_number": "",
            "previous_order_number": "",
            "cancellation_reason": "",
            "mask_pickup_notes": True,
            "pickup_attempts": "",
            "dropoff_attempts": "",
            "cvs_store": "",
            "cvs_parcel_price": "",
            "cancellation_detail": "",
            "freight_collect": False,
            "gbg_quote_id": "",
            "woocommerce_order_id": "",
            "woocommerce_shop": "",
            "pickup_timeslot_id": "",
            "sop_delivery_option": "",
            "promotion_code": "",
            "path_code": "",
            "shopline_domain": "",
            "convenience_store_parcel_price": "",
            "_convenience_store_parcel_price": "convenience_store_parcel_price",
            "duty_type": "",
            "_duty_type": "duty_type",
            "is_first_order": True,
            "_is_first_order": "is_first_order",
            "outbound_request_number": " ",
            "_outbound_request_number": "outbound_request_number",
            "inbound_request_number": "",
            "_inbound_request_number": "inbound_request_number",
            "self_dropoff_location_id": "",
            "_self_dropoff_location_id": "self_dropoff_location_id",
            "agent_type_id": " ",
            "_agent_type_id": "agent_type_id"
        },
        "address_meta":{
            "pickup_address_confidence": "WHITE",
            "dropoff_address_confidence": "WHITE",
            "pickup_address_type": "commercial",
            "dropoff_address_type": "residential",
            "pickup_address_segment":{
                "road_name": "鶴翔街",
                "block": "1",
                "building": "維港中心",
                "category": "commercial"
            },
            "dropoff_address_segment":{
                "road_name": "鶴翔街",
                "house_number": "號",
                "block": "1",
                "estate": "香港鶴園",
                "building": "維港中心",
                "category": "residential"
            }
        },
        "pickup_recognized_address": "",
        "dropoff_recognized_address": "",
        "allow_unable_to_pickup": "NOT_ALLOWED",
        "service_type": "four_hours",
        "service_time": "-1",
        "service_offering_id": "",
        "price": "40",
        "pickup_time": str(date.today() + timedelta(days=1))+"T02:00:07.000Z",
        "dropoff_time": str(date.today() + timedelta(days=1))+"T06:00:07.000Z"
    })
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

    if status_code == 200:
        corestatus = response["data"]["trips"][0]['order']['core_merchant']
        promostatus = response["data"]["trips"][0]['order']['promo_order']
        reliablestatus = response["data"]["trips"][0]['order']['reliable']
        poolstatus = response["data"]['is_in_available_pool']
        crewstatus = response["data"]['metadata']['own_crew']
        maskstatus = response["data"]['metadata']['mask_pickup_notes']
        return status_code, [corestatus,promostatus,reliablestatus,poolstatus,crewstatus,maskstatus], True
    else:
        return status_code, response, False

def AssignBundleToDeliveryAgent(bundle_id, da_id, triplist):
    path = "v2/admin/bundles/%s/agents/%s" % (bundle_id, da_id)
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/x-www-form-urlencoded'
    }
    tripdict = {}
    for index in range(len(triplist)):
        tripdict['trip_ids[%s]' % index ]=triplist[index]
    tripdict['admin_assign_price'] = ""
    payload = tripdict
    status_code, response = APIController.SendAPIPacket("put", GlobalAdapter.CommonVar.AdminUrl + path, headers, payload)

    if status_code == 200:
        return ResponseHandler(status_code, "Assign DA success"), True
    else:
        return ResponseHandler(status_code, response), False

def GetDAReceiveStatus(Bundle_id):
    path = "v2/agent/bundles/%s" % Bundle_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.DAAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers)


    DATotal = 0
    if status_code == 200:
        for i in range(len(response['data']['bundle']['trips'])):
            DAPriceTmp = response['data']['bundle']['trips'][i]['trip_price']
            DATotal += float(DAPriceTmp)
        return status_code, DATotal, True
    else:
        return status_code, response, False

@DecoratorHelper.FuncRecorder
def GetBundleIDInOrder(order_id):
    path = "v2/admin/orders/%s" % order_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

    if status_code == 200:
        return response['data']['trips'][0]['bundle_id'], True
    else:
        return response, False

@DecoratorHelper.FuncRecorder
def GetTripsPriceInOrder(order_id):
    path = "v2/admin/orders/%s" % order_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

    if status_code == 200:
        return response['data']['trips'][0]['order']['total_price']
    else:
        return response

def GetBundleOrderTotalPrice(Bundle_id):
    path = "v2/admin/bundles/%s/" % (Bundle_id)
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

    if status_code == 200:
        TotalPrice = 0
        for i in range(len(response['data']['bundle']['trips'])):
            Price_tmp= response['data']['bundle']['trips'][i]['trip_price']
            TotalPrice += float(Price_tmp)
        return TotalPrice, True
    else:
        return response, False
def GetAdminOrderTripsID(OrderID):
    path = "v2/admin/orders/%s" % OrderID
    headers = {
        'Authorization':GlobalAdapter.AuthVar.AdminAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.AdminUrl + path, headers)

    TripStatus = response['data']['trips'][0]['id']
    return TripStatus

def GetBackBoneOrderStatus(order_id,Datamapping=False):
    path = "v2/merchant/backbone/order?order_id=%s" % order_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200 and Datamapping==True:
        return response
    if status_code == 200:
        return response['data']['order']['waypoints'][0]['order_id']
    else:
        return response

def GetBackBoneOrderStatusByShopAuth(order_id,Datamapping=False):
    path = "v2/merchant/backbone/order?order_id=%s" % order_id
    headers = {
        'Authorization':GlobalAdapter.AuthVar.ShopAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200 and Datamapping==True:
        return response
    if status_code == 200:
        return response['data']['order']['waypoints'][0]['order_id']
    else:
        return response

@DecoratorHelper.FuncRecorder
def GetMerchantOrderPrice(OrderNumber):
    path = "v2/merchant/orders/%s?include_history=true&include_transactions=true" % OrderNumber
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)

    if status_code == 200:
        return response['data']['trips'][0]['order']['total_price']
    else:
        return response

@DecoratorHelper.FuncRecorder
def UnbundleOrder(bundleID, OrderNumber):
    path = "v2/admin/bundles/%s/orders/%s" % (bundleID, OrderNumber)
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)
    if status_code == 200:
        return response, True
    else:
        return response, False

def AdminCancelOrder(EntityID,OrderID):
    path = "v2/admin/entities/%s/orders/%s?refund=0&cancellation_reason=&cancellation_detail=" % (EntityID, OrderID)
    headers = {
        'authorization':GlobalAdapter.AuthVar.AdminAuth,
        'content-type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("delete", GlobalAdapter.CommonVar.AdminUrl + path, headers)

    if status_code == 200:
        return response, True
    else:
        return response, False

class V3API:

    def GetAndCheckPHBanners(self):
        path = "v2/agent/settings/ph_banners"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers)

        if status_code == 200:
            return ResponseHandler(status_code, "PH Banner setting success" + response['data']['value']), True
        else:
            return ResponseHandler(status_code, response), False

    def CheckPHAPPMessageSetting(self):
        path = "v2/agent/settings/ph_in_app_message"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers)

        if status_code == 200:
            return ResponseHandler(status_code, "PH message setting success" + response['data']['value']), True
        else:
            return ResponseHandler(status_code, response), False

    def GetAndCheckNewAvailableOrder(order_number):
        path = "v2/agent/trips/new/all"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        params = {
            "group":"",
            "limit":50,
            "offset":0,
            "project_tag_id":0,
            "city":"",
            "select":"compact.availableOrder"
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers, None, params)
        if status_code == 200:
            return ResponseHandler(status_code, "Order Available in P2P page correctly"), True
        else:
            return ResponseHandler(status_code, response), False

    @DecoratorHelper.FuncRecorder
    def GetAndCheckMyLastLegTripPage(order_number):
        path = "v2/last_leg_trip/me/warehouses"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        params = {
            "page":10,
            "limit":12
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers, None, params)

        if status_code == 200:
            return ResponseHandler(status_code, "Order in My LastLeg Trip Page correctly"), True
        else:
            return ResponseHandler(status_code, response), False

    def GetAndCheckMyLastLegJob(job_id):
        path = "v2/agent/jobs/me"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        params = {
            "is_last_leg":"true"
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers, None, params)

        if status_code == 200:
            return ResponseHandler(status_code, "Order in My LastLeg Job page correctly"), True
        else:
            return ResponseHandler(status_code, response), False

    def GetAndCheckDARegions(da_id):
        path = "v2/agent/regions"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        params = {
            "lat":"23.042205966958424",
            "lng":"120.23232395225406"
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers, None, params)
        if status_code == 200:
            return ResponseHandler(status_code, "DA Regions correctly : " + response['data'][0]['city']), True
        else:
            return ResponseHandler(status_code, response), False

    def GetAndCheckMyLastLegHistories(self):
        path = "v2/last_leg_trip/agent_trip_histories"
        headers = {
            'Authorization':GlobalAdapter.AuthVar.DAAuth,
            'Content-Type':'application/json'
        }
        params = {
            "limit":50,
            "page":1
        }
        status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.DAUrl + path, headers, None, params)

        if status_code == 200:
            return ResponseHandler(status_code,response['data']['page']), True
        else:
            return ResponseHandler(status_code,"Cant find order in trip_histories"), False

@DecoratorHelper.FuncRecorder
def GetMerchantOrderPaymentStatus(OrderNumber,Promotion=False):
    path = "v2/merchant/orders/%s?include_history=true&include_transactions=true" % OrderNumber
    headers = {
        'Authorization':GlobalAdapter.AuthVar.MerchantPortalAuth,
        'Content-Type':'application/json'
    }
    status_code, response = APIController.SendAPIPacket("get", GlobalAdapter.CommonVar.PortalUrl + path, headers)
    if status_code == 200:
        VerificationDict={}
        for i in range(len(response['data']['transactions'])):
            VerificationDict[response['data']['transactions'][i]['payment_profile_id']] = response['data']['transactions'][i]['amount']
        return VerificationDict,True
    else:
        return response, False


def ResponseHandler(status_code, return_message):
    '''
        ResponseHandler : To make response format
        input:
            status_code, return_message
        return :
         response format like {status code : 200, return message : Drop off order success}
    '''
    return {"status_code ":status_code, "return_message ": return_message}

