import os
from uuid import uuid4
import json

from google.ads.googleads.client import GoogleAdsClient
# from google.ads.googleads.errors import GoogleAdsException

# from google.api_core import protobuf_helpers

def get_keyword_themes_suggestions(refresh_token, keyword_text, country_code, language_code):

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

    client = GoogleAdsClient.load_from_dict(credentials)

    """Retrieves KeywordThemeConstants for the given criteria.
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

    response = keyword_theme_constant_service.suggest_keyword_theme_constants(
        request=request
    )
   
    keyword_theme_constants = response.keyword_theme_constants

    data = []
    for i in keyword_theme_constants:

        # display_resource_data = {}
        # display_resource_data["keyword_theme_suggestion"] = i.display_name
        # display_resource_data["resource_name"] = i.resource_name

        # data.append(display_resource_data)

        test_keyword_theme_sugg = i.display_name
        data.append(test_keyword_theme_sugg)
        
    print("print data type: ", type(data))
    print("print data: ", data)

    json.dumps(data)

    return data

def get_geo_target_constants(refresh_token, country_code, language_code, location):

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

    client = GoogleAdsClient.load_from_dict(credentials)

    gtc_service = client.get_service("GeoTargetConstantService")

    gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

    # language_code and country_code come from the frontend
    gtc_request.locale = language_code
    gtc_request.country_code = country_code

    # location has the location names to get suggested geo target constants.
    gtc_request.location_names.names.extend(location)
    
    # gtc_request.location_names.names.extend(
    #     ["Paris", "Quebec", "Spain", "Deutschland"]
    # )

    results = gtc_service.suggest_geo_target_constants(gtc_request)

    for suggestion in results.geo_target_constant_suggestions:
        geo_target_constant = suggestion.geo_target_constant
        print(
            f"{geo_target_constant.resource_name} "
            f"({geo_target_constant.name}, "
            f"{geo_target_constant.country_code}, "
            f"{geo_target_constant.target_type}, "
            f"{geo_target_constant.status.name}) "
            f"is found in locale ({suggestion.locale}) "
            f"with reach ({suggestion.reach}) "
            f"from search term ({suggestion.search_term})."
        )

    return geo_target_constant