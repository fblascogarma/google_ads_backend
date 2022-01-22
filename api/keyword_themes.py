import os
import sys
import json

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from .models import KeywordThemesRecommendations
from .serializers import KeywordThemesRecommendationsSerializer

'''
We are going to use two services to get keyword theme recommendations.
1) SmartCampaignSuggestService 
https://developers.google.com/google-ads/api/reference/rpc/v9/SmartCampaignSuggestService
2) KeywordThemeConstantService
https://developers.google.com/google-ads/api/reference/rpc/v9/KeywordThemeConstantService
'''
def get_keyword_themes_suggestions(
    refresh_token, 
    keyword_text, 
    country_code, 
    language_code,
    customer_id,
    final_url,
    business_name,
    business_location_id,
    geo_target_names
    ):

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
        # "linked_customer_id": customer_id,
        "use_proto_plus": True}

        client = GoogleAdsClient.load_from_dict(credentials)

        '''
        Here starts the new service to get keyword theme recommendations
        https://developers.google.com/google-ads/api/reference/rpc/v9/SmartCampaignSuggestService#suggestkeywordthemes
        '''
        print("customer_id")
        print(customer_id)
        print("final_url")
        print(final_url)
        print("business_name")
        print(business_name)
        print("business_location_id")
        print(business_location_id)
        print("geo_target_names")
        print(geo_target_names)

        # Create a list of locations to target to be used in the recommendations
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

        print('geo_targets:')
        print(geo_targets)

        location_targets = []
        for location in geo_targets:
            # Construct location information using the given geo target constant.
            location_info = client.get_type("LocationInfo")
            location_info.geo_target_constant = location
            location_targets.append(location_info)

        print("location_targets")
        print(location_targets)

        # Create SmartCampaignSuggestionInfo object to get recommendations
        suggestion_info = client.get_type("SmartCampaignSuggestionInfo")

        suggestion_info.final_url = final_url
        suggestion_info.language_code = language_code
        if business_location_id:
            suggestion_info.business_location_id = business_location_id
        else:
            suggestion_info.business_context.business_name = business_name
        suggestion_info.location_list.locations = location_targets

        sc_suggest_service = client.get_service(
        "SmartCampaignSuggestService"
        )
        request = client.get_type("SuggestKeywordThemesRequest")
        request.customer_id = customer_id
        request.suggestion_info = suggestion_info

        print("request")
        print(request)

        response = sc_suggest_service.suggest_keyword_themes(
            request=request
        )
        print("response")
        print(response)

        keyword_theme_constants = response.keyword_themes
        print('keyword_theme_constants:')
        print(keyword_theme_constants)

        recommendations = []
        for i in keyword_theme_constants:

            display_name = i.display_name
            # send only the display_name to the frontend
            # and in title case (fist letter of every word in upper case)
            display_name = display_name.title()
            recommendations.append(display_name)
            resource_name = i.resource_name
            # save display_name and resource_name in model
            data_model = {}
            data_model["resource_name"] = resource_name
            data_model["display_name"] = display_name
            serializer = KeywordThemesRecommendationsSerializer(data=data_model)
            if serializer.is_valid():
                # save it only if it is new data
                try:
                    KeywordThemesRecommendations.objects.get(display_name=display_name)
                    print('data already exists in model')
                except KeywordThemesRecommendations.DoesNotExist:
                    serializer.save()

        # json.dumps(recommendations)
        '''
        Here ends the new service to get keyword theme recommendations
        '''

        """
        Here starts the old service used to get keyword theme recommendations,
        which used the KeywordThemeConstantService that was part of the
        closed beta. With open beta, the preferred service to use is
        SmartCampaignSuggestService that is used to get recommendations on
        ad creatives and budget as well.
        However, we are using both to get more recommendations and it gives you
        the flexibility of designing your own solution as you see best.

        Retrieves KeywordThemeConstants for the given criteria.
        Args:
            client: an initialized GoogleAdsClient instance.
            keyword_text: a keyword used for generating keyword themes.
        Returns:
            a list of KeywordThemeConstants.
        """

        keyword_theme_constant_service = client.get_service(
        "KeywordThemeConstantService"
        )
        request = client.get_type("SuggestKeywordThemeConstantsRequest")
        request.query_text = keyword_text
        request.country_code = country_code
        request.language_code = language_code

        print("request")
        print(request)

        response = keyword_theme_constant_service.suggest_keyword_theme_constants(
            request=request
        )
        print("response")
        print(response)
    
        keyword_theme_constants = response.keyword_theme_constants
        print('keyword_theme_constants:')
        print(keyword_theme_constants)

        recommendations_older_service = []
        for i in keyword_theme_constants:

            display_name = i.display_name
            # send only the display_name to the frontend
            # and in title case (fist letter of every word in upper case)
            display_name = display_name.title()
            recommendations_older_service.append(display_name)
            resource_name = i.resource_name
            # save display_name and resource_name in model
            data_model = {}
            data_model["resource_name"] = resource_name
            data_model["display_name"] = display_name
            serializer = KeywordThemesRecommendationsSerializer(data=data_model)
            if serializer.is_valid():
                # save it only if it is new data
                try:
                    KeywordThemesRecommendations.objects.get(display_name=display_name)
                    print('data already exists in model')
                except KeywordThemesRecommendations.DoesNotExist:
                    serializer.save()
        '''
        Here ends the recommendations from the older service
        '''

        # join recommendations from both services
        for i in recommendations_older_service:
            recommendations.append(i)

        json.dumps(recommendations)

        return recommendations
    
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