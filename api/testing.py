import os
from uuid import uuid4
import json

from google.ads.googleads.client import GoogleAdsClient


language_code = 'es'
country_code = 'AR'
locations = ['buenos aires', 'martinez']
# geo_target_location = ['1000073', '9041027'] # buenos aires and martinez geo target constants
# landing_page = 'https://www.enjoymommyhood.com.ar/'
# customer_id = '2916870939'


# Configurations
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DEVELOPER_TOKEN = os.environ.get("GOOGLE_DEVELOPER_TOKEN", None)
GOOGLE_LOGIN_CUSTOMER_ID = os.environ.get("GOOGLE_LOGIN_CUSTOMER_ID", None)
GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)

# Configure using dict (the refresh token will be a dynamic value)
credentials = {
"developer_token": GOOGLE_DEVELOPER_TOKEN,
"refresh_token": GOOGLE_REFRESH_TOKEN,
"client_id": GOOGLE_CLIENT_ID,
"client_secret": GOOGLE_CLIENT_SECRET,
"login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID}

client = GoogleAdsClient.load_from_dict(credentials)

geo_targets = []
for location in locations:

    gtc_service = client.get_service("GeoTargetConstantService")

    gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

    gtc_request.locale = language_code
    gtc_request.country_code = country_code
    print('location:')
    print(location)
    # The location names to get suggested geo target constants.
    gtc_request.location_names.names.append(
        location
    )
    print('gtc_request.location_names')
    print(gtc_request.location_names)

    results = gtc_service.suggest_geo_target_constants(gtc_request)

    location_resource_names = []
    for suggestion in results.geo_target_constant_suggestions:
        geo_target_constant = suggestion.geo_target_constant
        
        location_resource_names.append(geo_target_constant.resource_name)

    # get the first one that is the one selected by the user
    geo_targets.append(location_resource_names[0])

print(geo_targets)