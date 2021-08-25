import os
from uuid import uuid4
import json

from google.ads.googleads.client import GoogleAdsClient

refresh_token = '1//06mVOJo1Fv533CgYIARAAGAYSNwF-L9Ir7JAGoG96Ma1p02o8CLRBQBJ0MuGeAnJhsApJPE8grDmyKqenhdVsEoJTnAW_4jASX7A'
language_code = 'es'
country_code = 'AR'
location = ['buenos aires', 'martinez']


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
# gtc_request.location_names.names.extend([location])

# gtc_request.location_names.names.extend(
#     ["Paris", "Quebec", "Spain", "Deutschland"]
# )

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

# store the geo constant ids from the location names input by user on the frontend
geo_constant_id_list = []
for suggestion in results.geo_target_constant_suggestions:
    geo_target_constant = suggestion.geo_target_constant
    data = {}
    # data["location_by_user"] = suggestion
    data["geo_id"] = geo_target_constant.id
    data["geo_name"] = geo_target_constant.name
    geo_constant_id_list.append(data)

print(geo_constant_id_list)
