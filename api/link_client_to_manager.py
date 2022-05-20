# Copyright 2022 Google LLC
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
'''
Link existing Google Ads account to your Manager account (MCC)
'''
import os
import sys

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers

def link_to_manager(
    refresh_token,
    customer_id
):
    try:
        # Configurations
        GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
        GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
        GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
        GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)
        GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)

        '''
        Step 1 - Use app's credentials to send link request from Manager to Client
        '''
        # Configure using dict (the refresh token will be a dynamic value)
        credentials = {
        "developer_token": GOOGLE_DEVELOPER_TOKEN,
        "refresh_token": GOOGLE_REFRESH_TOKEN,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
        # "linked_customer_id": customer_id,
        "use_proto_plus": True}

        client = GoogleAdsClient.load_from_dict(credentials)
        print('client initiated using Manager credentials...')

        manager_customer_id = GOOGLE_LOGIN_CUSTOMER_ID  # id of manager account

        customer_client_link_service = client.get_service(
            "CustomerClientLinkService"
        )

        # Extend an invitation to the client while authenticating as the manager.
        client_link_operation = client.get_type("CustomerClientLinkOperation")
        client_link = client_link_operation.create
        client_link.client_customer = customer_client_link_service.customer_path(
            customer_id
        )
        client_link.status = client.enums.ManagerLinkStatusEnum.PENDING
        print("client_link_operation:")
        print(client_link_operation)
        '''
        create {
        status: PENDING
        client_customer: "customers/6341155848"
        }
        '''

        response = customer_client_link_service.mutate_customer_client_link(
            customer_id=manager_customer_id, operation=client_link_operation
        )
        print("response on sending invite from Manager to Client:")
        print(response)
        '''
        result {
        resource_name: "customers/4642579541/customerClientLinks/6341155848~257046870"
        }
        '''
        resource_name = response.result.resource_name
        print(
            f'Extended an invitation from customer "{manager_customer_id}" to '
            f'customer "{customer_id}" with client link resource_name '
            f'"{resource_name}"'
        )
    
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

    # Find the manager_link_id of the link we just created, so we can construct
    # the resource name for the link from the client side. Note that since we
    # are filtering by resource_name, a unique identifier, only one
    # customer_client_link resource will be returned in the response
    query = f'''
        SELECT
            customer_client_link.manager_link_id
        FROM
            customer_client_link
        WHERE
            customer_client_link.resource_name = "{resource_name}"'''

    ga_service = client.get_service("GoogleAdsService")

    try:
        response = ga_service.search(
            customer_id=manager_customer_id, query=query
        )
        # Since the googleads_service.search method returns an iterator we need
        # to initialize an iteration in order to retrieve results, even though
        # we know the query will only return a single row.
        for row in response:
            manager_link_id = row.customer_client_link.manager_link_id
            print("manager_link_id:")
            print(manager_link_id)
            '''
            manager_link_id:
            257046870
            '''
        '''
        for row in response.result:
            manager_link_id = row.customer_client_link.manager_link_id
        AttributeError: 'result'
        '''
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

    '''
    Step 2 - Use client's refresh token to accept link invitation
    '''
    # Configure using dict (the refresh token will be a dynamic value)
    credentials = {
    "developer_token": GOOGLE_DEVELOPER_TOKEN,
    "refresh_token": refresh_token,
    "client_id": GOOGLE_CLIENT_ID,
    "client_secret": GOOGLE_CLIENT_SECRET,
    # "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
    # "login_customer_id": customer_id,
    "linked_customer_id": customer_id,
    "use_proto_plus": True}

    client = GoogleAdsClient.load_from_dict(credentials)
    print('client initiated using user credentials...')
    customer_manager_link_service = client.get_service(
        "CustomerManagerLinkService"
    )
    manager_link_operation = client.get_type("CustomerManagerLinkOperation")
    manager_link = manager_link_operation.update
    manager_link.resource_name = (
        customer_manager_link_service.customer_manager_link_path(
            customer_id,
            manager_customer_id,
            manager_link_id,
        )
    )

    manager_link.status = client.enums.ManagerLinkStatusEnum.ACTIVE
    client.copy_from(
        manager_link_operation.update_mask,
        protobuf_helpers.field_mask(None, manager_link._pb),
    )
    print("manager_link_operation:")
    print(manager_link_operation)
    '''
    manager_link_operation:
    update {
    resource_name: "customers/6341155848/customerManagerLinks/4642579541~257046870"
    status: ACTIVE
    }
    update_mask {
    paths: "resource_name"
    paths: "status"
    }
    '''
    try:
        response = customer_manager_link_service.mutate_customer_manager_link(
            customer_id=customer_id, operations=[manager_link_operation]
        )

        print("response when Client accepts invite link:")
        print(response)
        '''
        results {
        resource_name: "customers/6341155848/customerManagerLinks/4642579541~260013338"
        }
        '''
        print(
            "Client accepted invitation with resource_name: "
            f'"{response.results[0].resource_name}"'
        )
        '''
        Client accepted invitation with resource_name: "customers/6341155848/customerManagerLinks/4642579541~260013338"
        '''
        return response.results[0].resource_name
    
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
