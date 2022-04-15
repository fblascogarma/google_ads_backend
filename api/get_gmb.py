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
import re

from googleapiclient.discovery import build
import google.oauth2.credentials

def business_profile(refresh_token):

    try:
        '''
        Step 1 - Configurations
        '''
        # env variables
        GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
        GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)

        # documentation that explains the fields of the credentials
        # https://google-auth.readthedocs.io/en/stable/reference/google.oauth2.credentials.html
        credentials = {
            'refresh_token': refresh_token,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'token': None,
            'token_uri': "https://oauth2.googleapis.com/token"
        }

        # build the credentials object
        google_credentials = google.oauth2.credentials.Credentials(**credentials)

        '''
        Step 2 - Get the account information using the Account Managment API
        https://developers.google.com/my-business/reference/accountmanagement/rest
        '''
        # start the service
        service = build(
            'mybusinessaccountmanagement',      # serviceName
            'v1',                               # version
            credentials=google_credentials      # user's credentials
            )
        
        # build the request to accounts using list method
        request = service.accounts().list()

        # execute the request and print the result
        result = request.execute()
        print("result:")
        print(result)
        account = result['accounts'][0]['name']
        print("account:")
        print(account)

        '''
        Step 3 - Get the business information using the Business Information API
        https://developers.google.com/my-business/reference/businessinformation/rest/v1/accounts.locations/list
        '''
        # start the service
        service = build(
            'mybusinessbusinessinformation',    # serviceName
            'v1',                               # version
            credentials=google_credentials      # user's credentials
            )

        # set the fields you want to get of the Business Information profile
        # follow the link below to see all the fields you can get
        # https://developers.google.com/my-business/reference/businessinformation/rest/v1/accounts.locations#Location
        fields_we_want = 'name,title,websiteUri,languageCode,phoneNumbers'

        # build the request to accounts.locations using list method
        request = service.accounts().locations().list(
            parent=account,
            readMask=fields_we_want
            )

        # execute the request and print the result
        result = request.execute()
        print("result:")
        print(result)

        # get the business_location_id
        business_location_id = result['locations'][0]['name'].split('/')[1]
        print("business_location_id:")
        print(business_location_id)
        # get the business_name
        business_name = result['locations'][0]['title']
        print("business_name:")
        print(business_name)
        # get the phone_number
        phone_number = result['locations'][0]['phoneNumbers']['primaryPhone']
        # eliminate spaces and dashes
        phone_number = re.sub('[^0-9a-zA-Z]+', '', phone_number)
        print("phone_number:")
        print(phone_number)
        # get the final_url
        final_url = result['locations'][0]['websiteUri']
        print("final_url:")
        print(final_url)

        '''
        Step 4 - Consolidate info and send return object
        '''
        business_data = []
        data = {}
        data['account'] = account
        data['business_location_id'] = business_location_id
        data['business_name'] = business_name
        data['phone_number'] = phone_number
        data['final_url'] = final_url
        print("data:")
        print(data)
        business_data.append(data)
        print("business_data:")
        print(business_data)

        # json.dumps(business_data)

        return business_data

    except Exception as e:
        print('There was an error trying to get Business Information.' + str(e))
        