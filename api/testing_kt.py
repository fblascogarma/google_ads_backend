import os
from uuid import uuid4

from google.ads.googleads.client import GoogleAdsClient

from google.api_core import protobuf_helpers

language_code = 'es'
country_code = 'AR'
phone_number = '1156574920'
business_name = 'Enjoy Mommyhood'
# geo_target_location = "1000073" # buenos aires geo target constant
geo_target_location = ['1000073', '9041027'] # buenos aires and martinez geo target constants
landing_page = 'https://www.enjoymommyhood.com.ar/'
customer_id = '2916870939'
keyword_text = "ropa para embarazada"
# Geo target constant for New York City.
# _GEO_TARGET_CONSTANT = "1023191"
_BUDGET_TEMPORARY_ID = "-1"
_SMART_CAMPAIGN_TEMPORARY_ID = "-2"
_AD_GROUP_TEMPORARY_ID = "-3"
# keyword_text = ["ropa para embarazada","ropa de fiesta para embarazadas","corpiños para embarazadas","artículos de maternidad con delivery"]
headline_1_user = 'test headline 1'
headline_2_user = 'test headline 2'
headline_3_user = 'test headline 3'
desc_1_user = 'test description 1'
desc_2_user = 'test description 2'
campaign_name = f"Smart campaign test5 via api"

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

# Step 1: get keyword theme constants recommendations
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
print('print keyword_theme_constants recommended:')
print(keyword_theme_constants)

# need to save the keyword_theme_constants in memory so then I can lookup those that the user selected in the ui

# Step 2: user selects keyword themes from the recommendation and also creates new ones
keyword_theme_constants_selected = keyword_theme_constants[:3] # replicating user selected the first 4 options

keyword_theme_by_user = ["ropa para embarazada"]


# Step 3: map selected keyword_theme_constant and created free_form_keyword_theme to info
infos = []
for constant in keyword_theme_constants_selected:
    info = client.get_type("KeywordThemeInfo")
    info.keyword_theme_constant = constant.resource_name
    infos.append(info)

for i in keyword_theme_by_user:
    info = client.get_type("KeywordThemeInfo")
    info.free_form_keyword_theme = i
    infos.append(info)

print('print infos:')
print(infos)

# Step 4: get budget recommendation
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

# # Construct location information using the given geo target constant.
# for geo in geo_target_location:
#     # Construct location information using the given geo target constant.
#     location = client.get_type("LocationInfo")
#     # Set the location to the resource name of the given geo target constant.
#     location.geo_target_constant = client.get_service(
#         "GeoTargetConstantService"
#     ).geo_target_constant_path(geo)
#     print('location:')
#     print(location)
#     # Add the LocationInfo object to the list of locations on the
#     # suggestion_info object.
#     suggestion_info.location_list.locations.append(location)

locations = ['geoTargetConstants/1000073', 'geoTargetConstants/9041027']
for location in locations:
    # Construct location information using the given geo target constant.
    location_info = client.get_type("LocationInfo")
    location_info.geo_target_constant = location
    suggestion_info.location_list.locations.append(location_info)

print('suggestion_info.location_list.locations')
print(suggestion_info.location_list.locations)

# Add the LocationInfo object to the list of locations on the
# suggestion_info object. You have the option of providing multiple
# locations when using location-based suggestions.
# suggestion_info.location_list.locations.append(location)

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

# # Step 5: user selects budget
# selected_budget = recommendation.daily_amount_micros

# # Step 6: create budget operation for the campaign to be created
# """Creates a MutateOperation that creates a new CampaignBudget.
# A temporary ID will be assigned to this campaign budget so that it can be
# referenced by other objects being created in the same Mutate request.
# Args:
#     client: an initialized GoogleAdsClient instance.
#     customer_id: a client customer ID.
#     suggested_budget_amount: a numeric daily budget amount in micros.
# Returns:
#     a MutateOperation that creates a CampaignBudget.
# """
# mutate_operation = client.get_type("MutateOperation")
# campaign_budget_operation = mutate_operation.campaign_budget_operation
# campaign_budget = campaign_budget_operation.create
# campaign_budget.name = f"Smart campaign budget #{uuid4()} created via the api during testing"
# # A budget used for Smart campaigns must have the type SMART_CAMPAIGN.
# # Note that the field name "type_" is an implementation detail in Python,
# # the field's actual name is "type".
# campaign_budget.type_ = client.enums.BudgetTypeEnum.SMART_CAMPAIGN
# # The suggested budget amount from the SmartCampaignSuggestService is
# # a daily budget. We don't need to specify that here, because the budget
# # period already defaults to DAILY.
# campaign_budget.amount_micros = selected_budget
# # Set a temporary ID in the budget's resource name so it can be referenced
# # by the campaign in later steps.
# campaign_budget.resource_name = client.get_service(
#     "CampaignBudgetService"
# ).campaign_budget_path(customer_id, _BUDGET_TEMPORARY_ID)

# campaign_budget_operation = mutate_operation
# print('campaign_budget_operation')
# print(campaign_budget_operation)

# # Step 6: create SC operation
# """Creates a MutateOperation that creates a new Smart campaign.
# A temporary ID will be assigned to this campaign so that it can
# be referenced by other objects being created in the same Mutate request.
# Args:
#     client: an initialized GoogleAdsClient instance.
#     customer_id: a client customer ID.
# Returns:
#     a MutateOperation that creates a campaign.
# """
# mutate_operation = client.get_type("MutateOperation")
# campaign = mutate_operation.campaign_operation.create
# campaign.name = campaign_name
# # Set the campaign status as PAUSED. The campaign is the only entity in
# # the mutate request that should have its' status set.
# campaign.status = client.enums.CampaignStatusEnum.PAUSED
# # Campaign.AdvertisingChannelType is required to be SMART.
# campaign.advertising_channel_type = (
#     client.enums.AdvertisingChannelTypeEnum.SMART
# )
# # Campaign.AdvertisingChannelSubType is required to be SMART_CAMPAIGN.
# campaign.advertising_channel_sub_type = (
#     client.enums.AdvertisingChannelSubTypeEnum.SMART_CAMPAIGN
# )
# # Assign the resource name with a temporary ID.
# campaign_service = client.get_service("CampaignService")
# campaign.resource_name = campaign_service.campaign_path(
#     customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
# )
# # Set the budget using the given budget resource name.
# campaign.campaign_budget = campaign_service.campaign_budget_path(
#     customer_id, _BUDGET_TEMPORARY_ID
# )


# smart_campaign_operation = mutate_operation
# print('smart_campaign_operation:')
# print(smart_campaign_operation)

# # Step 7: create SC setting operation
# """Creates a MutateOperation to create a new SmartCampaignSetting.
# SmartCampaignSettings are unique in that they only support UPDATE
# operations, which are used to update and create them. Below we will
# use a temporary ID in the resource name to associate it with the
# campaign created in the previous step.
# Args:
#     client: an initialized GoogleAdsClient instance.
#     customer_id: a client customer ID.
#     business_location_id: the ID of a Google My Business location.
#     business_name: the name of a Google My Business.
# Returns:
#     a MutateOperation that creates a SmartCampaignSetting.
# """
# mutate_operation = client.get_type("MutateOperation")
# smart_campaign_setting = (
#     mutate_operation.smart_campaign_setting_operation.update
# )
# # Set a temporary ID in the campaign setting's resource name to associate it
# # with the campaign created in the previous step.
# smart_campaign_setting.resource_name = client.get_service(
#     "SmartCampaignSettingService"
# ).smart_campaign_setting_path(customer_id, _SMART_CAMPAIGN_TEMPORARY_ID)

# # Below we configure the SmartCampaignSetting using many of the same
# # details used to generate a budget suggestion.
# smart_campaign_setting.phone_number.country_code = country_code
# smart_campaign_setting.phone_number.phone_number = phone_number
# smart_campaign_setting.final_url = landing_page
# smart_campaign_setting.advertising_language_code = language_code

# # It's required that either a business location ID or a business name is
# # added to the SmartCampaignSetting.
# # if business_location_id:
# #     smart_campaign_setting.business_location_id = business_location_id
# # else:
# #     smart_campaign_setting.business_name = business_name
# smart_campaign_setting.business_name = business_name

# # Set the update mask on the operation. This is required since the smart
# # campaign setting is created in an UPDATE operation. Here the update
# # mask will be a list of all the fields that were set on the
# # SmartCampaignSetting.
# client.copy_from(
#     mutate_operation.smart_campaign_setting_operation.update_mask,
#     protobuf_helpers.field_mask(None, smart_campaign_setting._pb),
# )

# smart_campaign_setting_operation = mutate_operation

# print('smart_campaign_setting_operation:')
# print(smart_campaign_setting_operation)

# # Step 8: create campaign criterion operation

# """Creates a list of MutateOperations that create new campaign criteria.
# Args:
#     client: an initialized GoogleAdsClient instance.
#     customer_id: a client customer ID.
#     keyword_theme_infos: a list of KeywordThemeInfos.
# Returns:
#     a list of MutateOperations that create new campaign criteria.
# """
# campaign_service = client.get_service("CampaignService")

# operations = []
# for info in infos:
#     mutate_operation = client.get_type("MutateOperation")
#     campaign_criterion = (
#         mutate_operation.campaign_criterion_operation.create
#     )
#     # Set the campaign ID to a temporary ID.
#     campaign_criterion.campaign = campaign_service.campaign_path(
#         customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
#     )
#     # Set the criterion type to KEYWORD_THEME.
#     campaign_criterion.type_ = client.enums.CriterionTypeEnum.KEYWORD_THEME
#     # Set the keyword theme to the given KeywordThemeInfo.
#     campaign_criterion.keyword_theme = info
#     # Add the mutate operation to the list of other operations.
#     operations.append(mutate_operation)

# # create location criterion to add locations the user wants to target
# for i in suggestion_info.location_list.locations:
#     mutate_operation = client.get_type("MutateOperation")
#     campaign_criterion = (
#         mutate_operation.campaign_criterion_operation.create
#     )
#     # Set the campaign ID to a temporary ID.
#     campaign_criterion.campaign = campaign_service.campaign_path(
#         customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
#     )
#     # Set the criterion type to LOCATION.
#     campaign_criterion.type_ = client.enums.CriterionTypeEnum.LOCATION
#     # Set the location to the given location.
#     campaign_criterion.location = i
#     # Add the mutate operation to the list of other operations.
#     operations.append(mutate_operation)

# campaign_criterion_operations = operations

# print('campaign_criterion_operations:')
# print(campaign_criterion_operations)

# # Step 9: create ad group operation
# """Creates a MutateOperation that creates a new ad group.
# A temporary ID will be used in the campaign resource name for this
# ad group to associate it with the Smart campaign created in earlier steps.
# A temporary ID will also be used for its own resource name so that we can
# associate an ad group ad with it later in the process.
# Only one ad group can be created for a given Smart campaign.
# Args:
#     client: an initialized GoogleAdsClient instance.
#     customer_id: a client customer ID.
# Returns:
#     a MutateOperation that creates a new ad group.
# """
# mutate_operation = client.get_type("MutateOperation")
# ad_group = mutate_operation.ad_group_operation.create
# # Set the ad group ID to a temporary ID.
# ad_group.resource_name = client.get_service("AdGroupService").ad_group_path(
#     customer_id, _AD_GROUP_TEMPORARY_ID
# )
# ad_group.name = f"Smart campaign ad group #{uuid4()} created via the api during testing"
# # Set the campaign ID to a temporary ID.
# ad_group.campaign = client.get_service("CampaignService").campaign_path(
#     customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
# )
# # The ad group type must be set to SMART_CAMPAIGN_ADS.
# ad_group.type_ = client.enums.AdGroupTypeEnum.SMART_CAMPAIGN_ADS

# ad_group_operation = mutate_operation

# print('ad_group_operation:')
# print(ad_group_operation)

# # step 10: create ad group ad operation
# """Creates a MutateOperation that creates a new ad group ad.
# A temporary ID will be used in the ad group resource name for this
# ad group ad to associate it with the ad group created in earlier steps.
# Args:
#     client: an initialized GoogleAdsClient instance.
#     customer_id: a client customer ID.
# Returns:
#     a MutateOperation that creates a new ad group ad.
# """
# mutate_operation = client.get_type("MutateOperation")
# ad_group_ad = mutate_operation.ad_group_ad_operation.create
# # Set the ad group ID to a temporary ID.
# ad_group_ad.ad_group = client.get_service("AdGroupService").ad_group_path(
#     customer_id, _AD_GROUP_TEMPORARY_ID
# )
# # Set the type to SMART_CAMPAIGN_AD.
# ad_group_ad.ad.type_ = client.enums.AdTypeEnum.SMART_CAMPAIGN_AD
# ad = ad_group_ad.ad.smart_campaign_ad
# # At most, three headlines can be specified for a Smart campaign ad.
# headline_1 = client.get_type("AdTextAsset")
# headline_1.text = headline_1_user
# headline_2 = client.get_type("AdTextAsset")
# headline_2.text = headline_2_user
# headline_3 = client.get_type("AdTextAsset")
# headline_3.text = headline_3_user
# ad.headlines.extend([headline_1, headline_2, headline_3])
# # At most, two descriptions can be specified for a Smart campaign ad.
# description_1 = client.get_type("AdTextAsset")
# description_1.text = desc_1_user
# description_2 = client.get_type("AdTextAsset")
# description_2.text = desc_2_user
# ad.descriptions.extend([description_1, description_2])

# ad_group_ad_operation = mutate_operation

# print('ad_group_ad_operation:')
# print(ad_group_ad_operation)

# # step 11: create smart campaign
# googleads_service = client.get_service("GoogleAdsService")

# # Send the operations into a single Mutate request.
# response = googleads_service.mutate(
#     customer_id=customer_id,
#     mutate_operations=[
#         # It's important to create these entities in this order because
#         # they depend on each other, for example the SmartCampaignSetting
#         # and ad group depend on the campaign, and the ad group ad depends
#         # on the ad group.
#         campaign_budget_operation,
#         smart_campaign_operation,
#         smart_campaign_setting_operation,
#         # Expand the list of campaign criterion operations into the list of
#         # other mutate operations
#         *campaign_criterion_operations,
#         ad_group_operation,
#         ad_group_ad_operation,
#     ],
# )

# """Prints the details of a MutateGoogleAdsResponse.
# Parses the "response" oneof field name and uses it to extract the new
# entity's name and resource name.
# Args:
#     response: a MutateGoogleAdsResponse object.
# """
# # Parse the Mutate response to print details about the entities that
# # were created by the request.
# for result in response.mutate_operation_responses:
#     resource_type = "unrecognized"
#     resource_name = "not found"

#     if result._pb.HasField("campaign_budget_result"):
#         resource_type = "CampaignBudget"
#         resource_name = result.campaign_budget_result.resource_name
#     elif result._pb.HasField("campaign_result"):
#         resource_type = "Campaign"
#         resource_name = result.campaign_result.resource_name
#     elif result._pb.HasField("smart_campaign_setting_result"):
#         resource_type = "SmartCampaignSettingResult"
#         resource_name = result.smart_campaign_setting_result.resource_name
#     elif result._pb.HasField("campaign_criterion_result"):
#         resource_type = "CampaignCriterion"
#         resource_name = result.campaign_criterion_result.resource_name
#     elif result._pb.HasField("ad_group_result"):
#         resource_type = "AdGroup"
#         resource_name = result.ad_group_result.resource_name
#     elif result._pb.HasField("ad_group_ad_result"):
#         resource_type = "AdGroupAd"
#         resource_name = result.ad_group_ad_result.resource_name

#     print(
#         f"Created a(n) {resource_type} with "
#         f"resource_name: '{resource_name}'."
#     )

# print('smart campaign created!!')