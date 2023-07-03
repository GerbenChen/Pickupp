#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 GlobalAdapter.py: The def of this file called
'''

class FrameworkVar:
    ApiSpentTime = 0.0
    Environment = "uat"

class AuthApiSpentTime:
    AdminAuth = 0.0
    MerchantAuth = 0.0
    DAAuth = 0.0
    ShopPortalAuth = 0.0

class AuthVar:
    MerchantPortalAuth = ""
    AdminAuth = ""
    ShopAuth = ""
    DAAuth = ""

class CommonVar:
    SettingConfig={}
    ApiUrl = ""
    AdminUrl = ""
    DAUrl = ""
    PortalUrl = ""
    ShopHomeUrl = ""
    ShopControlUrl = ""
    TopUpUrl = ""
    CreditCardUrl = ""
    StripeTokensUrl = ""
    TopUpAmount = "25"
    DeliveryAgentID = ""
    WaypointKey= ("id","order_id","ordering","contact_name","contact_phone","contact_company","address","lat","lng","district_level_1","district_level_2","district_level_3","city","zip_code","note","location_id","address_confidence","address_type","address_segment","recognized_address")
    OrdersKey= ("entity_id" ,"user_id" ,"service_offering_id" ,"origin","order_price" ,"total_price","city","outsource_partner","is_dummy_service" ,"cash_on_delivery_amount" ,"is_fragile" ,"pickup_sms" ,"reliable" ,"has_delivery_note" ,"pay_on_success" ,"allow_unable_to_pickup" ,"service_type" ,"service_time")
    OrderPropertiesKey = ("basic_rate" ,"weight_rate" ,"express_rate" ,"discount_rate" ,"distance_rate" ,"wall_surcharge" ,"adjustment_rate" ,"pickup_surcharge" ,"reliability_rate" ,"dropoff_surcharge" ,"exchange_rate" ,"is_pickupp_care","import_tax_rate","surcharge_rate","promotion_code" ,"duty_type" ,"shopify_id" ,"shopify_email" ,"shopify_domain" ,"woocommerce_order_id", "woocommerce_shop" ,"shopline_order_id" ,"shopline_domain" ,"sop_delivery_option")
    ReferenceNumberKey = ("value","key")
