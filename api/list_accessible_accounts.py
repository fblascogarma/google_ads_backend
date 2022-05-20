# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def list_accounts(refresh_token):

    # Configurations
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
    GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
    # GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)

    # Configure using dict (the refresh token will be a dynamic value)
    credentials = {
    "developer_token": GOOGLE_DEVELOPER_TOKEN,
    "refresh_token": refresh_token,
    "client_id": GOOGLE_CLIENT_ID,
    "client_secret": GOOGLE_CLIENT_SECRET,
    # "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
    "use_proto_plus": True}

    try:
        client = GoogleAdsClient.load_from_dict(credentials)

        customer_service = client.get_service("CustomerService")
        ga_service = client.get_service("GoogleAdsService")

        accessible_customers = customer_service.list_accessible_customers()

        resource_names = accessible_customers.resource_names
        
        customer_data = []
        for resource_name in resource_names:
            try:
                customer_id = resource_name.split('/')[1]
                query = (f'''
                    SELECT 
                        customer.currency_code, 
                        customer.descriptive_name, 
                        customer.id, 
                        customer.manager, 
                        customer.resource_name, 
                        customer.time_zone 
                    FROM customer
                    WHERE customer.resource_name = '{resource_name}'
                    '''
                )
                stream = ga_service.search_stream(
                    customer_id=customer_id,
                    query=query
                )

                for batch in stream:
                    for row in batch.results:
                        data = {}
                        data["customer_id"] = row.customer.id
                        data["description"] = row.customer.descriptive_name
                        data["time_zone"] = row.customer.time_zone
                        data["currency"] = row.customer.currency_code
                        if row.customer.manager == 1:
                            data["account_type"] = "Manager"
                        elif row.customer.manager == 0:
                            data["account_type"] = "Client"
                        # customer_data.append(data)
                        # data["status"] = row.customer.status  # comes in API v10
                        # get billing status too
                        query = """
                            SELECT
                                billing_setup.id,
                                billing_setup.status
                            FROM billing_setup"""

                        response = ga_service.search_stream(customer_id=customer_id, query=query)

                        # print("Found the following billing setup results:")
                        for batch in response:
                            for row in batch.results:
                                billing_setup = row.billing_setup
                                # print(
                                #     f"Billing setup with ID {billing_setup.id}, "
                                #     f'status "{billing_setup.status.name}", '
                                # )

                        try:
                            billing_status = billing_setup.status.name
                        except NameError:
                            billing_status = "no billing"

                        # possible statuses are: PENDING, APPROVED, CANCELLED, and APPROVED_HELD
                        # https://developers.google.com/google-ads/api/reference/rpc/v8/BillingSetupStatusEnum.BillingSetupStatus
                        # print('billing_status:')
                        # print(billing_status)
                        data["billing_status"] = billing_status

                        # check if client is linked to your Manager account
                        query = """
                            SELECT
                                customer_manager_link.manager_customer, 
                                customer_manager_link.resource_name, 
                                customer_manager_link.status
                            FROM customer_manager_link"""

                        response = ga_service.search_stream(customer_id=customer_id, query=query)
                        for batch in response:
                            for row in batch.results:
                                print("row.customer_manager_link.status:")
                                print(row.customer_manager_link.status.name)
                                if row.customer_manager_link.status.name == "ACTIVE":
                                    manager_linked_id = row.customer_manager_link.manager_customer.split('/')[1]
                                    data["manager_account_linked"] = manager_linked_id
                                else:
                                    data["manager_account_linked"] = "0"
                        
                        customer_data.append(data)
            
            # the exception below is in case the user has a test account, 
            # which would throw an error
            except GoogleAdsException as ex:
                print(
                    f'Request with ID "{ex.request_id}" failed with status '
                    f'"{ex.error.code().name}" and includes the following errors:'
                )
                for error in ex.failure.errors:
                    print(f'\tError with message "{error.message}".')
                    if error.location:
                        for field_path_element in error.location.field_path_elements:
                            print(f"\t\tOn field: {field_path_element.field_name}")

        json.dumps(customer_data)
        print(customer_data)

        return customer_data
    
    except GoogleAdsException as ex:
        print(
            f'Request with ID "{ex.request_id}" failed with status '
            f'"{ex.error.code().name}" and includes the following errors:'
        )
        for error in ex.failure.errors:
            print(f'\tError with message "{error.message}".')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
