import os
import json

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def list_accounts(refresh_token):

    # Configurations
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
    GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)

    # Configure using dict (the refresh token will be a dynamic value)
    credentials = {
    "developer_token": GOOGLE_DEVELOPER_TOKEN,
    "refresh_token": refresh_token,
    "client_id": GOOGLE_CLIENT_ID,
    "client_secret": GOOGLE_CLIENT_SECRET,
    "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID}

    googleads_client = GoogleAdsClient.load_from_dict(credentials)

    customer_service = googleads_client.get_service("CustomerService")

    accessible_customers = customer_service.list_accessible_customers()
    # result_total = len(accessible_customers.resource_names)

    resource_names = accessible_customers.resource_names
    
    customer_data = []
    for resource_name in resource_names:
        try:
            customer = customer_service.get_customer(resource_name=resource_name)
           
            if customer.manager == 1:
                account_type = "Manager"
            else:
                if customer.manager == 0:
                    account_type = "Client"

            data = {}
            data["customer_id"] = customer.id
            data["description"] = customer.descriptive_name
            data["time_zone"] = customer.time_zone
            data["currency"] = customer.currency_code
            data["account_type"] = account_type
            customer_data.append(data)
           
        # need to write an exception in case the user has a test account, which would throw an error
        except: print("user permission denied")

    json.dumps(customer_data)

    return customer_data

