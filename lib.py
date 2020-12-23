import requests
import json
from config import *
from pprint import pprint

def get_token(email=None, password=None):
    '''
        Calls authentication API and returns the tokens
        takes email and password as args
    '''
    if email and password:
        pass
    else:
        raise ValueError("Email and Password are mandatory to authenticate")
    r = requests.post(
        AUTH_URL,
        {
            'email': email,
            'password': password
        }
    )
    return r.json()


class ShipRocketOrder():
    KEYS = [
        'shipment_id',
        'order_id',
        'awb_code',
        'shipment_track_activities',
        'token',
        'track_url',
        'billing_email',
        'billing_address',
        'billing_address2',
        'billing_city',
        'billing_country',
        'billing_name',
        'billing_customer_name',
        'billing_last_name',
        'billing_phone',
        'billing_pincode',
        'billing_state',
        'order_date',
        'payment_method',
        'height',
        'weight',
        'length',
        'breadth',
        'total',
        'shipping_is_billing',
        'label_url',
        'order_items',
        'merchant_order_id',
        'sub_total'
    ]

    unique_keys_traversed = []
    
    def __init__(self, **kwargs):
        '''
            Initializes all keys of the object from KEYS
            if passed in object definition then set to that value else set as null
        '''
        for key in self.KEYS:
            if key in kwargs:
                setattr(self, key, kwargs[key])
            else:
                setattr(self, key, None)
    

    def set_attributes(self, data):
        '''
            Checks if the data has any attribute matching to object attribute 
            if data has attribute matching as that of object then updates else ignores
            loops over lists, iterates over all dict values.

            Built to traverse nested objects with lists having nested JSON
        '''
        if isinstance(data, dict):
            for key, value in data.items():
                if key not in self.unique_keys_traversed:
                    self.unique_keys_traversed.append(key)
                self.set_attributes(value)
                if hasattr(self, key):
                    setattr(self, key, value)
        elif isinstance(data, list):
            for value in data:
                self.set_attributes(value)
        else:
            pass

    def track_shipment(self):
        '''
            Track a shipment
            If object is initialized with awb then gets tracking information from AWB
            If object is initialized with order_id then gets tracking information from order_id
            updates objects attributes
            returns tracking info
        '''
        if not self.token:
            raise ValueError("token not set")
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
        if self.order_id:
            r = requests.get(
                SHIPMENT_ID_TRACKING_URL % self.order_id,
                headers=headers
            )
        elif self.awb_code:
            r = requests.get(
                AWB_TRACKING_URL % self.awb_code,
                headers=headers
            )
        else:
            raise ValueError("Please initialise with order_id or awb_code to track the order")
        data = r.json()
        if 'tracking_data' in data:
            self.set_attributes(data)
        return r.json()
    
    def get_order_details(self):
        if not self.token:
            raise ValueError("token not set")
        if not self.order_id:
            raise ValueError("order_id not set")
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
        r = requests.get(
            SINGLE_ORDER_DETAILS % self.order_id,
            headers=headers
        )
        data = r.json()
        if 'data' in data:
            self.set_attributes(data)
        return data
    
    def get_shipping_label(self):
        if not self.token:
            raise ValueError("token not set")
        if not self.order_id:
            raise ValueError("order_id not set")
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
        payload = {
            "shipment_id": [str(self.shipment_id)]
        }
        r = requests.post(
            GENERATE_SHIPPING_LABEL,
            headers=headers,
            data=json.dumps(payload)
        )
        data = r.json()
        if 'label_created' in data and data['label_created']:
            self.set_attributes(data)
        return data
    
    def assign_awb(self):
        if not self.token:
            raise ValueError("token not set")
        if not self.order_id:
            raise ValueError("order_id not set")
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
        payload = {
            "shipment_id": [str(self.shipment_id)]
        }
        r = requests.post(
            GENERATE_AWB_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        data = r.json()
        if 'awb_assign_status' in data and data['awb_assign_status']:
            self.set_attributes(data)
        return data
    
    def place_order(self):
        mandatory_fields = [
            "payment_method",
            "merchant_order_id",
            "order_date",
            "sub_total",
            "shipping_is_billing",
            "billing_customer_name",
            "billing_last_name",
            "billing_email",
            "billing_address",
            "billing_state",
            "billing_country",
            "billing_phone",
            "billing_pincode",
            "length",
            "breadth",
            "height",
            "weight",
            "order_items"
        ]
        order_items_mandatory_field = [
            "name",
            "sku",
            "units",
            "selling_price",
            "discount",
            "tax",
            "hsn",
        ]
        if not self.token:
            raise ValueError("token not set")
        if self.order_id:
            raise ValueError("order_id shouldn't be set")
        if self.awb_code:
            raise ValueError("awb_code shouldn't be set")
        if self.shipment_id:
            raise ValueError("shipment_id shouldn't be set")
        payload = {}
        for field in mandatory_fields:
            if not getattr(self, field):
                raise ValueError("%s shouldn't be empty" % field)
            else:
                payload[field] = getattr(self, field)
        
        if isinstance(self.order_items, list):
            pass
        else:
            raise ValueError("order_items should be a list")
        
        for item in self.order_items:
            for key in order_items_mandatory_field:
                if key not in item:
                    raise ValueError("%s key missing in order item" % key)

        payload['order_id'] = payload['merchant_order_id']
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
        r = requests.post(
            CREATE_ORDER_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        data = r.json()
        if 'shipment_id' in data and 'order_id' in data:
            self.set_attributes(data)
            self.assign_awb()
            self.get_shipping_label()
        return data

    def cancel_order(self):
        if not self.token:
            raise ValueError("token not set")
        if not self.order_id:
            raise ValueError("order_id should be set")
        payload = {
            'ids': [self.order_id]
            }
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
        r = requests.post(
            CANCEL_ORDER_URL,
            headers=headers,
            data=json.dumps(payload)
        )
        data = r.json()
        return data