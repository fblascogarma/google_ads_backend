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
import json

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from .models import KeywordThemesRecommendations


def get_ad_recommendation(
    refresh_token, 
    customer_id, 
    display_name, 
    landing_page, 
    geo_target_names, 
    language_code, 
    country_code, 
    business_location_id,
    business_name):

    try:
    
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
        "linked_customer_id": customer_id,
        "use_proto_plus": True}

        client = GoogleAdsClient.load_from_dict(credentials)

        '''
        step 1 - create the suggestion_info object that will
        be used to get ad creative recommendations
        '''
        suggestion_info = client.get_type("SmartCampaignSuggestionInfo")

        '''
        step 2 - set landing_page, language code, business_name, and
        ad_schedules to the suggestion_info object 
        (country_code is not possible)
        '''
        # Add the URL of the campaign's landing page.
        suggestion_info.final_url = landing_page

        # Add the language code for the campaign.
        suggestion_info.language_code = language_code

        # Set either of the business_location_id or business_name, depending on
        # whichever is provided.
        if business_location_id:
            suggestion_info.business_location_id = business_location_id
        else:
            suggestion_info.business_context.business_name = business_name

        # Add a schedule detailing which days of the week the business is open.
        # This schedule describes a schedule in which the business is open on
        # Mondays from 9am to 5pm.
        ad_schedule_info = client.get_type("AdScheduleInfo")
        # Set the day of this schedule as Monday.
        ad_schedule_info.day_of_week = client.enums.DayOfWeekEnum.MONDAY
        # Set the start hour to 9am.
        ad_schedule_info.start_hour = 9
        # Set the end hour to 5pm.
        ad_schedule_info.end_hour = 17
        # Set the start and end minute of zero, for example: 9:00 and 5:00.
        zero_minute_of_hour = client.enums.MinuteOfHourEnum.ZERO
        ad_schedule_info.start_minute = zero_minute_of_hour
        ad_schedule_info.end_minute = zero_minute_of_hour
        suggestion_info.ad_schedules.append(ad_schedule_info)

        '''
        step 3 - map selected keyword themes to KeywordThemeInfo object,
        and add it to the suggestion_info object.

        Lookup in model to retrieve keyword_theme_constant using the display_name,
        and if no value founded, it means it is a free_form_keyword_theme,
        so you will set it up as that
        '''

        infos = []
        for i in display_name:
            try:
                            
                resource_name = KeywordThemesRecommendations.objects.get(display_name=i)
                # transform object into a string
                resource_name = str(resource_name)
                info = client.get_type("KeywordThemeInfo")
                info.keyword_theme_constant = resource_name
                infos.append(info)

            except KeywordThemesRecommendations.DoesNotExist:
                info = client.get_type("KeywordThemeInfo")
                info.free_form_keyword_theme = i
                infos.append(info)

        print('print infos:')
        print(infos)

        # Add the KeywordThemeInfo objects to the SuggestionInfo object.
        suggestion_info.keyword_themes.extend(infos)

        '''
        step 4 - add locations to the suggestion_info object
        using the LocationInfo object
        '''
        # get geo target constants for the geo target names selected by user
        geo_targets = []
        for name in geo_target_names:

            gtc_service = client.get_service("GeoTargetConstantService")

            gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

            gtc_request.locale = language_code
            gtc_request.country_code = country_code

            # The location names to get suggested geo target constants.
            gtc_request.location_names.names.append(
                name
            )

            results = gtc_service.suggest_geo_target_constants(gtc_request)

            location_resource_names = []
            for suggestion in results.geo_target_constant_suggestions:
                geo_target_constant = suggestion.geo_target_constant
                
                location_resource_names.append(geo_target_constant.resource_name)

            # get the first one that is the one selected by the user
            geo_targets.append(location_resource_names[0])

        print(geo_targets)

        for location in geo_targets:
            # Construct location information using the given geo target constant.
            location_info = client.get_type("LocationInfo")
            location_info.geo_target_constant = location
            suggestion_info.location_list.locations.append(location_info)

        '''
        step 4 - send the suggestion_info object to
        get the recommendations of ad creatives
        '''
        print('suggestion_info to be sent:')
        print(suggestion_info)

        sc_suggest_service = client.get_service("SmartCampaignSuggestService")

        # get the SuggestSmartCampaignAdRequest to get the ad creatives recomm.
        request = client.get_type("SuggestSmartCampaignAdRequest")
        request.customer_id = customer_id

        # Unlike the SuggestSmartCampaignBudgetOptions method, it's only possible
        # to use suggestion_info to retrieve ad creative suggestions.
        request.suggestion_info = suggestion_info

        # Issue a request to retrieve ad creative suggestions.
        response = sc_suggest_service.suggest_smart_campaign_ad(request=request)
        print('response of the request to retrieve ad creative suggestions:')
        print(response)

        # The SmartCampaignAdInfo object in the response contains a list of up to
        # three headlines and two descriptions. Note that some of the suggestions
        # may have empty strings as text. Before setting these on the ad you should
        # review them and filter out any empty values.
        ad_suggestions = response.ad_info
        print('ad_suggestions:')
        print(ad_suggestions)

        '''
        step 5 - prepare data to be sent to the frontend
        and send it
        '''
        headlines_recomm = []
        print("The following headlines were suggested:")
        for headline in ad_suggestions.headlines:
            print(f"\t{headline.text or '<None>'}")
            headlines_recomm.append(headline.text)

        description_recomm = []
        print("And the following descriptions were suggested:")
        for description in ad_suggestions.descriptions:
            print(f"\t{description.text or '<None>'}")
            description_recomm.append(description.text)

        print(headlines_recomm)
        print(description_recomm)

        data = {}
        data["headlines"] = headlines_recomm
        data["descriptions"] = description_recomm
        
        json.dumps(data)

        return data

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