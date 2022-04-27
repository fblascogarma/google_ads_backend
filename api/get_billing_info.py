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
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

def billing_info(
    refresh_token, 
    customer_id,
    use_login_id):
    try:
        # Configurations
        GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
        GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
        GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
        GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)

        # Configure using dictionary.
        # Check if we need to use login_customer_id in the headers,
        # which is needed if the Ads account was created by the app.
        if use_login_id == True:
            credentials = {
            "developer_token": GOOGLE_DEVELOPER_TOKEN,
            "refresh_token": refresh_token,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
            # "linked_customer_id": customer_id,
            "use_proto_plus": True}
        else:
            credentials = {
            "developer_token": GOOGLE_DEVELOPER_TOKEN,
            "refresh_token": refresh_token,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            # "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
            "linked_customer_id": customer_id,
            "use_proto_plus": True}

        client = GoogleAdsClient.load_from_dict(credentials)


        ga_service = client.get_service("GoogleAdsService")

        query = """
            SELECT
                billing_setup.id,
                billing_setup.status,
                billing_setup.payments_account,
                billing_setup.payments_account_info.payments_account_id,
                billing_setup.payments_account_info.payments_account_name,
                billing_setup.payments_account_info.payments_profile_id,
                billing_setup.payments_account_info.payments_profile_name,
                billing_setup.payments_account_info.secondary_payments_profile_id
            FROM billing_setup"""

        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("Found the following billing setup results:")
        for batch in response:
            for row in batch.results:
                billing_setup = row.billing_setup
                pai = billing_setup.payments_account_info

                if pai.secondary_payments_profile_id:
                    secondary_payments_profile_id = (
                        pai.secondary_payments_profile_id
                    )
                else:
                    secondary_payments_profile_id = "None"

                print(
                    f"Billing setup with ID {billing_setup.id}, "
                    f'status "{billing_setup.status.name}", '
                    f'payments_account "{billing_setup.payments_account}" '
                    f"payments_account_id {pai.payments_account_id}, "
                    f'payments_account_name "{pai.payments_account_name}", '
                    f"payments_profile_id {pai.payments_profile_id}, "
                    f'payments_profile_name "{pai.payments_profile_name}", '
                    "secondary_payments_profile_id "
                    f"{secondary_payments_profile_id}."
                )

        try:
            billing_status = billing_setup.status.name
        except NameError:
            billing_status = "no billing"

        # possible statuses are: PENDING, APPROVED, CANCELLED, and APPROVED_HELD
        # https://developers.google.com/google-ads/api/reference/rpc/v8/BillingSetupStatusEnum.BillingSetupStatus
        print('billing_status:')
        print(billing_status)
        return billing_status

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