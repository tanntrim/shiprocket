from pprint import pprint
from lib import *

token = get_token(email="", password="")

# Initialize with order id or token
# s = ShipRocketOrder(shipment_id=77881411, token=token['token'])
# s = ShipRocketOrder(awb_code='788830567028', token=token['token'])
# s.track_shipment()
# s.get_manifest()
# print(s.delivered())
# s.assign_awb()
# s.get_shipping_label()
# s.cancel_order()
s = ShipRocketOrder(
        token=token['token'],
        payment_method='cod',
        merchant_order_id="hasdj2323",
        order_date="2020-12-23",
        sub_total=100,
        shipping_is_billing=True,
        billing_customer_name="Mudit",
        billing_last_name="Jain",
        billing_email="muditsjain@gmail.com",
        billing_address="115 Rishabh Vihar, Karkardooma",
        billing_city="Delhi",
        billing_state="Delhi",
        billing_country="India",
        billing_phone="9873267618",
        billing_pincode="110092",
        length="0.51",
        breadth="0.51",
        height="0.51",
        weight="0.1",
        order_items=[{
            "sku": "TJ-MK-202-01",
            "name": "Abc",
            "units": 1,
            "selling_price": 100,
            "discount": 0,
            "tax": 0,
            "hsn": 232
        }],
    )
print(s.place_order_one_step())
# pprint(s.__dict__)