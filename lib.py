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
        'edd',
        'shipment_status',
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
        'sub_total',
        'charges',
        'courier_name',
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
        if self.shipment_id:
            r = requests.get(
                SHIPMENT_ID_TRACKING_URL % self.shipment_id,
                headers=headers
            )
        elif self.awb_code:
            r = requests.get(
                AWB_TRACKING_URL % self.awb_code,
                headers=headers
            )
        else:
            raise ValueError("Please initialise with shipment_id or awb_code to track the order")
        data = r.json()
        if 'tracking_data' in data:
            self.set_attributes(data)
        return r.json()
    
    def get_order_details(self):
        '''
            Get order details of a particular order, updates object variables as well.
        '''
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
    
    def get_manifest(self):
        '''
            Get manifest for this order
        '''
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
            GENERATE_MANIFEST,
            headers=headers,
            data=json.dumps(payload)
        )
        data = r.json()
        pprint(data)
        # if 'label_created' in data and data['label_created']:
        #     self.set_attributes(data)
        return data
    
    def get_shipping_label(self):
        '''
            Get shipping label for this order
        '''
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
        '''
            Assign an AWB to this order
        '''
        if not self.token:
            raise ValueError("token not set")
        if not self.order_id:
            raise ValueError("order_id not set")
        if self.awb_code:
            raise ValueError("AWB code is already assigned")
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
        '''
            Place order on shiprocket
        '''
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
            "billing_city",
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
        order_items_mandatory_fields = [
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
            if isinstance(item, dict):
                pass
            else:
                raise ValueError("order_item should be a dictionary")
            for key in order_items_mandatory_fields:
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
        return data
    

    def place_order_one_step(self):
        '''
            Places an order on shiprocket, ship it, assign AWB, create label, and manifest in one step
        '''
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
            "billing_city",
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
        order_items_mandatory_fields = [
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
            if isinstance(item, dict):
                pass
            else:
                raise ValueError("order_item should be a dictionary")
            for key in order_items_mandatory_fields:
                if key not in item:
                    raise ValueError("%s key missing in order item" % key)

        payload['order_id'] = payload['merchant_order_id']
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % self.token
        }
        r = requests.post(
            ONE_STEP_CREATE_ORDER,
            headers=headers,
            data=json.dumps(payload)
        )
        data = r.json()
        if 'shipment_id' in data and 'order_id' in data:
            self.set_attributes(data)
            # self.assign_awb()
            # self.get_shipping_label()
        return data

    def cancel_order(self):
        '''
            Cancel an order
        '''
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
    
    def delivered(self):
        '''
            Check delivery status of an order
        '''
        if self.shipment_status and self.shipment_status == 7:
            return True
        elif not self.shipment_status:
            data = self.track_shipment()
            if 'tracking_data' in data and 'shipment_status' in data['tracking_data'] and data['tracking_data']['shipment_status'] == 7:
                return True
            else:
                return False
        else:
            return False
    
    def rto(self):
        '''
            Check RTO status of an order
        '''
        if self.shipment_status and (self.shipment_status == 9 or self.shipment_status == 10 or self.shipment_status == 14):
            return True
        elif not self.shipment_status:
            data = self.track_shipment()
            if 'tracking_data' in data and 'shipment_status' in data['tracking_data'] and (data['tracking_data']['shipment_status'] == 9 or data['tracking_data']['shipment_status'] == 10 or data['tracking_data']['shipment_status'] == 14):
                return True
            else:
                return False
        else:
            return False

    
    def get_estimated_delievery_date(self):
        '''
            Get estimated delivery date for an order
        '''
        if self.edd:
            return self.edd
        else:
            data = self.track_shipment()
            if 'tracking_data' in data and 'edd' in data['tracking_data']:
                return data['tracking_data']['edd']
    
    def get_last_tracking_update(self):
        '''
            Get last tracking update
        '''
        data = self.track_shipment()
        if 'tracking_data' in data and 'shipment_track_activities' in data['tracking_data'] and isinstance(data['tracking_data']['shipment_track_activities'], list) and len(data['tracking_data']['shipment_track_activities']) > 0:
            return data['tracking_data']['shipment_track_activities'][0]
        else:
            return []
    
    def get_billing_data(self):
        '''
            Get billing data
        '''
        if self.charges:
            return self.charges
        else:
            data = self.get_order_details()
            if 'data' in data and 'awb_data' in data['data'] and 'charges' in data['data']['awb_data']:
                return data['data']['awb_data']['charges']
            else:
                return {}