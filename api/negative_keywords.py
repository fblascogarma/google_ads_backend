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

import os
import sys
import json

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def get_negative_keywords(
    refresh_token, 
    customer_id,
    campaign_id,
    use_login_id
    ):

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
        print("client initiated...")

        ga_service = client.get_service("GoogleAdsService")

        query = (f'''
        SELECT 
            campaign_criterion.type, 
            campaign_criterion.status, 
            campaign_criterion.criterion_id, 
            campaign_criterion.keyword_theme.keyword_theme_constant, 
            campaign_criterion.keyword_theme.free_form_keyword_theme, 
            campaign_criterion.negative 
        FROM campaign_criterion 
        WHERE campaign_criterion.type = 'KEYWORD_THEME'
        AND campaign_criterion.negative = 'TRUE'
        AND campaign.id = {campaign_id}
        ''')
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        keyword_theme_free_form_list = []
        campaign_criterion_id_list = []
        for batch in response:
            for row in batch.results:
                if row.campaign_criterion.keyword_theme.free_form_keyword_theme:
                    keyword_theme_free_form_list.append(
                        row.campaign_criterion.keyword_theme.free_form_keyword_theme
                    )
                    campaign_criterion_id_list.append(
                        row.campaign_criterion.criterion_id
                    )

        print("keyword_theme_free_form_list:")
        print(keyword_theme_free_form_list)
        return(keyword_theme_free_form_list)

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

def edit_negative_keywords(
    refresh_token, 
    customer_id,
    campaign_id,
    new_kt_negative_list,
    use_login_id
    ):

    try:

        '''
        Step 1 - Configurations
        '''
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
        print("client initiated...")

        '''
        Step 1 - Get the current negative keyword themes.
        These will only be in free form (not constant) only.
        '''
        ga_service = client.get_service("GoogleAdsService")

        query = (f'''
        SELECT 
            campaign_criterion.type, 
            campaign_criterion.status, 
            campaign_criterion.criterion_id, 
            campaign_criterion.keyword_theme.keyword_theme_constant, 
            campaign_criterion.keyword_theme.free_form_keyword_theme, 
            campaign_criterion.negative 
        FROM campaign_criterion 
        WHERE campaign_criterion.type = 'KEYWORD_THEME'
        AND campaign_criterion.negative = 'TRUE'
        AND campaign.id = {campaign_id}
        ''')
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        keyword_theme_free_form_list = []
        campaign_criterion_id_list = []
        for batch in response:
            for row in batch.results:
                if row.campaign_criterion.keyword_theme.free_form_keyword_theme:
                    keyword_theme_free_form_list.append(
                        row.campaign_criterion.keyword_theme.free_form_keyword_theme
                    )
                    campaign_criterion_id_list.append(
                        row.campaign_criterion.criterion_id
                    )

        print("keyword_theme_free_form_list:")
        print(keyword_theme_free_form_list)

        ''''
        Step 2 - Create list of negative keywords to remove and to add
        '''
        kw_to_remove = []       # list of keyword constants to remove from campaign
        kw_to_remove_index = [] # this is used to identify the campaign_criterion_id
        kw_to_add = []          # list of keyword constants to add to the campaign

        print("start creating list of keywords to remove")
        for kw in keyword_theme_free_form_list:
            print("kw:")
            print(kw)
            if kw not in new_kt_negative_list:
                kw_to_remove.append(kw)
                # get the index to use it later
                kw_to_remove_index.append(keyword_theme_free_form_list.index(kw))

        print("start creating list of keywords to add")
        for kw in new_kt_negative_list:
            print("kw:")
            print(kw)
            if kw not in keyword_theme_free_form_list:
                kw_info = client.get_type("KeywordThemeInfo")
                kw_info.free_form_keyword_theme = kw
                kw_to_add.append(kw_info)

        print("kw_to_remove:")
        print(kw_to_remove)
        print("kw_to_add:")
        print(kw_to_add)

        '''
        Step 3 - Create remove and create operations
        '''
        # we are going to append all mutate operations under operations
        operations = []

        # get the campaign_criterion_id of those that we need to remove
        campaign_criterion_id_to_remove = []
        for i in kw_to_remove_index:
            campaign_criterion_id_to_remove.append(campaign_criterion_id_list[i])

        # create operation to remove them
        campaign_criterion_service = client.get_service("CampaignCriterionService")
        for i in campaign_criterion_id_to_remove:
            # get the resource name
            # that will be in this form: customers/{customer_id}/campaignCriteria/{campaign_id}~{criterion_id}
            campaign_criterion_resource_name = campaign_criterion_service.campaign_criterion_path(
            customer_id, campaign_id, i
            )
            # start mutate operation to remove
            mutate_operation = client.get_type("MutateOperation")
            campaign_criterion_operation = mutate_operation.campaign_criterion_operation
            campaign_criterion_operation.remove = campaign_criterion_resource_name
            operations.append(campaign_criterion_operation)

        # create operation to add keywords
        for kw in kw_to_add:
            mutate_operation = client.get_type("MutateOperation")
            campaign_criterion_operation = mutate_operation.campaign_criterion_operation

            campaign_criterion = campaign_criterion_operation.create

            # Set the campaign
            campaign_service = client.get_service("CampaignService")
            campaign_criterion.campaign = campaign_service.campaign_path(
                customer_id, campaign_id
            )
            # Set the criterion type to KEYWORD_THEME.
            campaign_criterion.type_ = client.enums.CriterionTypeEnum.KEYWORD_THEME
            # Set the criterion to negative.
            campaign_criterion.negative = True
            # Set the keyword theme to the given KeywordThemeInfo.
            campaign_criterion.keyword_theme = kw
            operations.append(campaign_criterion_operation)

        print("operations to send as a mutate request:")
        print(operations)

        '''
        Step 4 - Send all mutate requests
        '''
        response = campaign_criterion_service.mutate_campaign_criteria(
            customer_id=customer_id,
            operations=[ 
                # Expand the list of campaign criterion operations into the list of
                # other mutate operations
                *operations,
            ],
        )
        print("response:")
        print(response)

        '''
        Step 5 - Query keyword themes to send to frontend
        '''
        query = (f'''
        SELECT 
            campaign_criterion.type, 
            campaign_criterion.status, 
            campaign_criterion.criterion_id, 
            campaign_criterion.keyword_theme.keyword_theme_constant, 
            campaign_criterion.keyword_theme.free_form_keyword_theme, 
            campaign_criterion.negative 
        FROM campaign_criterion 
        WHERE campaign_criterion.type = 'KEYWORD_THEME'
        AND campaign_criterion.negative = 'TRUE'
        AND campaign.id = {campaign_id}
        ''')
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        new_keyword_theme_free_form_list = []
        campaign_criterion_id_list = []
        for batch in response:
            for row in batch.results:
                if row.campaign_criterion.keyword_theme.free_form_keyword_theme:
                    new_keyword_theme_free_form_list.append(
                        row.campaign_criterion.keyword_theme.free_form_keyword_theme
                    )
                    campaign_criterion_id_list.append(
                        row.campaign_criterion.criterion_id
                    )

        print("new_keyword_theme_free_form_list:")
        print(new_keyword_theme_free_form_list)

        # eliminate duplicates and add unique values only
        updated_kw = list(dict.fromkeys(new_keyword_theme_free_form_list))

        json.dumps(updated_kw)
        print("updated_kw:")
        print(updated_kw)
        return(updated_kw)

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