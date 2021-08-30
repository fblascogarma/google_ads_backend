import os
from uuid import uuid4
import json

from google.ads.googleads.client import GoogleAdsClient

refresh_token = '1//06p0agHdIYOviCgYIARAAGAYSNwF-L9Ir39B3AqLvuVUU4p1oUhDqiM_ikxYW0tCVBsqih7xew8DVmSgBtu_WfzItBaPyl5tNDjI'
language_code = 'es'
country_code = 'AR'
geo_target_location = ['1000073', '9041027'] # buenos aires and martinez geo target constants
landing_page = 'https://www.enjoymommyhood.com.ar/'
customer_id = '2916870939'
keyword_text = ["ropa para embarazada","ropa de fiesta para embarazadas","corpiños para embarazadas","artículos de maternidad con delivery"]


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

# get infos from keyword themes display name

query = """
            SELECT 
                keyword_theme_constant.resource_name 
            FROM keyword_theme_constant 
            WHERE keyword_theme_constant.display_name = 'ropa de fiesta para embarazadas'
        """

# query = """
#             SELECT 
#                 smart_campaign_search_term_view.resource_name 
#             FROM smart_campaign_search_term_view 
#             WHERE smart_campaign_search_term_view.display_name = 'ropa de fiesta para embarazadas'
#         """

ga_service = client.get_service("GoogleAdsService")

# Issues a search request using streaming.
response = ga_service.search_stream(customer_id=customer_id, query=query)

infos = []
for batch in response:
    for row in batch.results:
        data = {}
        data["keyword_theme_constant"] = row.resouce_name
        infos.append(data)

print(infos)

# keyword_theme_constant_service = client.get_service(
#     "KeywordThemeConstantService"
# )
# request = client.get_type("SuggestKeywordThemeConstantsRequest")
# for i in keyword_text:

# request.query_text = keyword_text
# request.country_code = country_code
# request.language_code = language_code

# response = keyword_theme_constant_service.suggest_keyword_theme_constants(
#     request=request
# )

# print(
#     f"Retrieved {len(response.keyword_theme_constants)} keyword theme "
#     f"constants using the keyword: '{keyword_text}'"
# )

# keyword_theme_constants = response.keyword_theme_constants
# print(keyword_theme_constants)

# infos = []
# for constant in keyword_theme_constants:
#     info = client.get_type("KeywordThemeInfo")
#     info.keyword_theme_constant = constant.resource_name
#     infos.append(info)

# print(infos)

# start of budget suggestion
# sc_suggest_service = client.get_service("SmartCampaignSuggestService")
# request = client.get_type("SuggestSmartCampaignBudgetOptionsRequest")
# request.customer_id = customer_id
# # You can retrieve suggestions for an existing campaign by setting the
# # "campaign" field of the request equal to the resource name of a campaign
# # and leaving the rest of the request fields below unset:
# # request.campaign = INSERT_CAMPAIGN_RESOURCE_NAME_HERE

# # Since these suggestions are for a new campaign, we're going to
# # use the suggestion_info field instead.
# suggestion_info = request.suggestion_info

# # Add the URL of the campaign's landing page.
# suggestion_info.final_url = landing_page

# # Construct location information using the given geo target constant. It's
# # also possible to provide a geographic proximity using the "proximity"
# # field on suggestion_info, for example:
# #
# # suggestion_info.proximity.address.post_code = INSERT_POSTAL_CODE
# # suggestion_info.proximity.address.province_code = INSERT_PROVINCE_CODE
# # suggestion_info.proximity.address.country_code = INSERT_COUNTRY_CODE
# # suggestion_info.proximity.address.province_name = INSERT_PROVINCE_NAME
# # suggestion_info.proximity.address.street_address = INSERT_STREET_ADDRESS
# # suggestion_info.proximity.address.street_address2 = INSERT_STREET_ADDRESS_2
# # suggestion_info.proximity.address.city_name = INSERT_CITY_NAME
# # suggestion_info.proximity.radius = INSERT_RADIUS
# # suggestion_info.proximity.radius_units = RADIUS_UNITS
# #
# # For more information on proximities see:
# # https://developers.google.com/google-ads/api/reference/rpc/latest/ProximityInfo
# location = client.get_type("LocationInfo")
# # Set the location to the resource name of the given geo target constant.
# location.geo_target_constant = client.get_service(
#     "GeoTargetConstantService"
# ).geo_target_constant_path(geo_target_location)
# # Add the LocationInfo object to the list of locations on the
# # suggestion_info object. You have the option of providing multiple
# # locations when using location-based suggestions.
# suggestion_info.location_list.locations.append(location)

# # Add the KeywordThemeInfo objects to the SuggestionInfo object.
# suggestion_info.keyword_themes.extend(keyword_theme_infos)

# # If provided, add the GMB location ID.
# if business_location_id:
#     suggestion_info.business_location_id = business_location_id

# # Add a schedule detailing which days of the week the business is open.
# # This schedule describes a schedule in which the business is open on
# # Mondays from 9am to 5pm.
# ad_schedule_info = client.get_type("AdScheduleInfo")
# # Set the day of this schedule as Monday.
# ad_schedule_info.day_of_week = client.enums.DayOfWeekEnum.MONDAY
# # Set the start hour to 9am.
# ad_schedule_info.start_hour = 9
# # Set the end hour to 5pm.
# ad_schedule_info.end_hour = 17
# # Set the start and end minute of zero, for example: 9:00 and 5:00.
# zero_minute_of_hour = client.enums.MinuteOfHourEnum.ZERO
# ad_schedule_info.start_minute = zero_minute_of_hour
# ad_schedule_info.end_minute = zero_minute_of_hour
# suggestion_info.ad_schedules.append(ad_schedule_info)

# # Issue a request to retrieve a budget suggestion.
# response = sc_suggest_service.suggest_smart_campaign_budget_options(
#     request=request
# )

# # Three tiers of options will be returned, a "low", "high" and
# # "recommended". Here we will use the "recommended" option. The amount is
# # specified in micros, where one million is equivalent to one currency unit.
# recommendation = response.recommended
# print(
#     f"A daily budget amount of {recommendation.daily_amount_micros} micros "
#     "was suggested, garnering an estimated minimum of "
#     f"{recommendation.metrics.min_daily_clicks} clicks and an estimated "
#     f"maximum of {recommendation.metrics.max_daily_clicks} per day."
# )

# print(recommendation.daily_amount_micros)
# [END add_smart_campaign_1]

# # start of geo location recommendation

# gtc_service = client.get_service("GeoTargetConstantService")

# gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

# # language_code and country_code come from the frontend
# gtc_request.locale = language_code
# gtc_request.country_code = country_code

# # location has the location names to get suggested geo target constants.
# gtc_request.location_names.names.extend(location)
# # gtc_request.location_names.names.extend([location])

# # gtc_request.location_names.names.extend(
# #     ["Paris", "Quebec", "Spain", "Deutschland"]
# # )

# # get suggestions of locations based on the user's input
# results = gtc_service.suggest_geo_target_constants(gtc_request)

# # for suggestion in results.geo_target_constant_suggestions:
# #     geo_target_constant = suggestion.geo_target_constant
# #     print(
# #         f"{geo_target_constant.resource_name} "
# #         f"({geo_target_constant.name}, "
# #         f"{geo_target_constant.country_code}, "
# #         f"{geo_target_constant.target_type}, "
# #         f"{geo_target_constant.status.name}) "
# #         f"is found in locale ({suggestion.locale}) "
# #         f"with reach ({suggestion.reach}) "
# #         f"from search term ({suggestion.search_term})."
# #     )

# # store the geo constant ids from the location names input by user on the frontend
# geo_constant_id_list = []
# for suggestion in results.geo_target_constant_suggestions:
#     geo_target_constant = suggestion.geo_target_constant
#     data = {}
#     # data["location_by_user"] = suggestion
#     data["geo_id"] = geo_target_constant.id
#     data["geo_name"] = geo_target_constant.name
#     geo_constant_id_list.append(data)

# print(geo_constant_id_list)
