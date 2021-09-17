import os
import sys
import json

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def get_geo_location_recommendations(refresh_token, language_code, country_code, location):

    try:

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
        "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
        "use_proto_plus": True}

        client = GoogleAdsClient.load_from_dict(credentials)

        gtc_service = client.get_service("GeoTargetConstantService")

        gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

        # language_code and country_code come from the frontend
        gtc_request.locale = language_code
        gtc_request.country_code = country_code

        # location has the location name from the frontend
        gtc_request.location_names.names.extend([location])

        # get suggestions of locations based on the user's input
        results = gtc_service.suggest_geo_target_constants(gtc_request)

        # for suggestion in results.geo_target_constant_suggestions:
        #     geo_target_constant = suggestion.geo_target_constant
        #     print(
        #         f"{geo_target_constant.resource_name} "
        #         f"({geo_target_constant.name}, "
        #         f"{geo_target_constant.country_code}, "
        #         f"{geo_target_constant.target_type}, "
        #         f"{geo_target_constant.status.name}) "
        #         f"is found in locale ({suggestion.locale}) "
        #         f"with reach ({suggestion.reach}) "
        #         f"from search term ({suggestion.search_term})."
        #     )

        # store the recommendations
        location_recommendations = []
        for suggestion in results.geo_target_constant_suggestions:
            geo_target_constant = suggestion.geo_target_constant
            data = {}
            # data["location_by_user"] = suggestion
            data["geo_id"] = geo_target_constant.id
            data["geo_name"] = geo_target_constant.name
            location_recommendations.append(data)

        #print(location_recommendations)
        json.dumps(location_recommendations)

        return location_recommendations

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