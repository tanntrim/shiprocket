# ShipRocket

Use this package as a wrapper for ShipRocket API.

## Get authentication token
Create an authentication token using email and password generated on the ShipRocket dashboard
```
from lib import *

token = get_token(email="<EMAIL>", password="<PASSWORD>")
```

---

## Place an order
Only creates an order and `doesn't assigns AWB or generates it's manifest`
```
from lib import *

token = get_token(email="<EMAIL>", password="<PASSWORD>")
s = ShipRocketOrder(
    token=token['token'],
    payment_method='',
    merchant_order_id="",
    order_date="",
    sub_total=10,
    shipping_is_billing=True,
    billing_customer_name="",
    billing_last_name="",
    billing_email="",
    billing_address="",
    billing_city="",
    billing_state="",
    billing_country="",
    billing_phone="",
    billing_pincode="",
    length="",
    breadth="",
    height="",
    weight="",
    order_items=[{
        "sku": "",
        "name": "",
        "units": 1,
        "selling_price": X,
        "discount": Y,
        "tax": Z,
        "hsn": XYZ
    }],
)
s.place_order()
```

---

## Place an order in one step
Creates an order, assigns AWB, then generates its manifest and label in one step.

```
from lib import *

token = get_token(email="<EMAIL>", password="<PASSWORD>")
s = ShipRocketOrder(
    token=token['token'],
    payment_method='',
    merchant_order_id="",
    order_date="",
    sub_total=10,
    shipping_is_billing=True,
    billing_customer_name="",
    billing_last_name="",
    billing_email="",
    billing_address="",
    billing_city="",
    billing_state="",
    billing_country="",
    billing_phone="",
    billing_pincode="",
    length="",
    breadth="",
    height="",
    weight="",
    order_items=[{
        "sku": "",
        "name": "",
        "units": 1,
        "selling_price": X,
        "discount": Y,
        "tax": Z,
        "hsn": XYZ
    }],
)
s.place_order_one_step()
```
---
## Track an Order
Get tracking data for an order
### Using shipment id
```
from lib import *

token = get_token(email="mudit@tjori.com", password="tjori@123")
s = ShipRocketOrder(shipment_id=77881411, token=token['token'])
data = s.track_shipment()
```

### Using awb
```
from lib import *

token = get_token(email="mudit@tjori.com", password="tjori@123")
s = ShipRocketOrder(awb_code='788830567028', token=token['token'])
data = s.track_shipment()
```