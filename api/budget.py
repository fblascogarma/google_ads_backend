import os
import sys
import json

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from .models import KeywordThemesRecommendations


def get_budget_recommendation(
    refresh_token, customer_id, display_name, 
    landing_page, geo_target_names, language_code, 
    country_code):

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
        Step 1: map selected keyword themes to info

        lookup in model to retrieve keyword_theme_constant using the display_name
        if no value founded, it means it is a free_form_keyword_theme
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

        # Step 2: get budget recommendation
        """Retrieves a suggested budget amount for a new budget.
        Using the SmartCampaignSuggestService to determine a daily budget for new
        and existing Smart campaigns is highly recommended because it helps the
        campaigns achieve optimal performance.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
            business_location_id: the ID of a Google My Business location.
            keyword_theme_infos: a list of KeywordThemeInfos.
        Returns:
            a daily budget amount in micros.
        """
        sc_suggest_service = client.get_service("SmartCampaignSuggestService")
        request = client.get_type("SuggestSmartCampaignBudgetOptionsRequest")
        request.customer_id = customer_id
        # You can retrieve suggestions for an existing campaign by setting the
        # "campaign" field of the request equal to the resource name of a campaign
        # and leaving the rest of the request fields below unset:
        # request.campaign = INSERT_CAMPAIGN_RESOURCE_NAME_HERE

        # Since these suggestions are for a new campaign, we're going to
        # use the suggestion_info field instead.
        suggestion_info = request.suggestion_info

        # Add the URL of the campaign's landing page.
        suggestion_info.final_url = landing_page

        # get geo target constants for the geo target names selected by user
        geo_targets = []
        for name in geo_target_names:

            gtc_service = client.get_service("GeoTargetConstantService")

            gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

            gtc_request.locale = language_code
            gtc_request.country_code = country_code
            # print('name:')
            # print(name)
            # The location names to get suggested geo target constants.
            gtc_request.location_names.names.append(
                name
            )
            # print('gtc_request.location_names')
            # print(gtc_request.location_names)

            results = gtc_service.suggest_geo_target_constants(gtc_request)

            location_resource_names = []
            for suggestion in results.geo_target_constant_suggestions:
                geo_target_constant = suggestion.geo_target_constant
                
                location_resource_names.append(geo_target_constant.resource_name)

            # get the first one that is the one selected by the user
            geo_targets.append(location_resource_names[0])

        print(geo_targets)


        # locations = geo_targets
        # locations = ['geoTargetConstants/1000073', 'geoTargetConstants/9041027']
        for location in geo_targets:
            # Construct location information using the given geo target constant.
            location_info = client.get_type("LocationInfo")
            location_info.geo_target_constant = location
            suggestion_info.location_list.locations.append(location_info)

        # Add the KeywordThemeInfo objects to the SuggestionInfo object.
        suggestion_info.keyword_themes.extend(infos)
        print('suggestion_info:')
        print(suggestion_info)

        # If provided, add the GMB location ID.
        # if business_location_id:
        #     suggestion_info.business_location_id = business_location_id

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

        # Issue a request to retrieve a budget suggestion.
        response = sc_suggest_service.suggest_smart_campaign_budget_options(
            request=request
        )

        # Three tiers of options will be returned, a "low", "high" and
        # "recommended". Here we will use the "recommended" option. The amount is
        # specified in micros, where one million is equivalent to one currency unit.
        recommendation = response.recommended
        low_budget = response.low
        high_budget = response.high

        print(
            f"A daily budget amount of {recommendation.daily_amount_micros} micros "
            "was suggested, garnering an estimated minimum of "
            f"{recommendation.metrics.min_daily_clicks} clicks and an estimated "
            f"maximum of {recommendation.metrics.max_daily_clicks} per day."
        )

        print('recommendation budget is:')
        print(recommendation.daily_amount_micros)
        print('low budget recommendation is:')
        print(low_budget.daily_amount_micros)
        print('high budget recommendation is:')
        print(high_budget.daily_amount_micros)

        data = {}
        # budgets
        data["high"] = high_budget.daily_amount_micros
        data["recommended"] = recommendation.daily_amount_micros
        data["low"] = low_budget.daily_amount_micros
        # metrics
        data["high_min_clicks"] = high_budget.metrics.min_daily_clicks
        data["high_max_clicks"] = high_budget.metrics.max_daily_clicks
        data["recommended_min_clicks"] = recommendation.metrics.min_daily_clicks
        data["recommended_max_clicks"] = recommendation.metrics.max_daily_clicks
        data["low_min_clicks"] = low_budget.metrics.min_daily_clicks
        data["low_max_clicks"] = low_budget.metrics.max_daily_clicks

        # get currency of the budget recommendations
        customer_service = client.get_service("CustomerService")
        customer_resource_name = str('customers/'+customer_id)
        customer_data = customer_service.get_customer(resource_name=customer_resource_name)
        currency_code = customer_data.currency_code
        data["currency"] = currency_code
        

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