import os
import sys
from uuid import uuid4
import json

from google.ads.googleads.client import GoogleAdsClient
# from google.ads.googleads.errors import GoogleAdsException
from google.api_core import protobuf_helpers


# customer_id = str(4037974191) # billing set up    | account created via api
# # customer_id = str(4597538560) # no billing        | account created via api
customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14648734935)    # used it to test remove campaign, and it was successful
campaign_id = str(14652304508)
new_budget = 3*1000000
landing_page = 'https://www.enjoymommyhood.com.ar/'     # for suggestion_info
language_code = 'es'                                    # for suggestion_info
business_name = 'Enjoy Mommyhood'                       # for suggestion_info
country_code = 'AR'                                     # for suggestion_info
display_name = [
    "ropa para embarazadas",
    "corpiños para embarazadas",
    "ropa formal para embarazadas",
    "ropa de fiesta para embarazadas",
    "ropa para embarazadas barata"
    ]                                                   # for suggestion_info
geo_target_names = [
    "buenos aires",
    "martinez",
    "san isidro",
    "olivos"
    ]                                                   # for suggestion_info


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
"login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID,
"use_proto_plus": True}

client = GoogleAdsClient.load_from_dict(credentials)

'''
Get ad suggestions - ERROR
Parameters needed: credentials, customer_id, suggestion_info, landing_page,
language_code, business_name, country_code, geo_target_names,
display_name (in the test we use infos but in production it will be display_name)
'''
# # step 1: get suggestion_info
# suggestion_info = client.get_type("SmartCampaignSuggestionInfo")

# # Add the URL of the campaign's landing page.
# suggestion_info.final_url = landing_page

# # Add the language code for the campaign.
# suggestion_info.language_code = language_code

# # get the infos
# # for the app we will use these lines that are commented out
# # infos = []
# # for i in display_name:
# #     try:
                    
# #         resource_name = KeywordThemesRecommendations.objects.get(display_name=i)
# #         # transform object into a string
# #         resource_name = str(resource_name)
# #         info = client.get_type("KeywordThemeInfo")
# #         info.keyword_theme_constant = resource_name
# #         infos.append(info)

# #     except KeywordThemesRecommendations.DoesNotExist:
# #         info = client.get_type("KeywordThemeInfo")
# #         info.free_form_keyword_theme = i
# #         infos.append(info)

# # print('print infos:')
# # print(infos)
# # for testing, we'll use the below lines that mimick the above lines
# infos = []
# resource_name_list = [
#     "keywordThemeConstants/6003199~0",
#     "keywordThemeConstants/154114~0",
#     "keywordThemeConstants/154114~119103"
#     ]
# for resource_name in resource_name_list:
#     info = client.get_type("KeywordThemeInfo")
#     info.keyword_theme_constant = resource_name
#     infos.append(info)

# free_kw_list = ["ropa para embarazada"]
# for kw in free_kw_list:
#     info = client.get_type("KeywordThemeInfo")
#     info.free_form_keyword_theme = kw
#     infos.append(info)



# # get geo target constants for the geo target names selected by user
# geo_targets = []
# for name in geo_target_names:

#     gtc_service = client.get_service("GeoTargetConstantService")

#     gtc_request = client.get_type("SuggestGeoTargetConstantsRequest")

#     gtc_request.locale = language_code
#     gtc_request.country_code = country_code
#     # print('name:')
#     # print(name)
#     # The location names to get suggested geo target constants.
#     gtc_request.location_names.names.append(
#         name
#     )
#     # print('gtc_request.location_names')
#     # print(gtc_request.location_names)

#     results = gtc_service.suggest_geo_target_constants(gtc_request)

#     location_resource_names = []
#     for suggestion in results.geo_target_constant_suggestions:
#         geo_target_constant = suggestion.geo_target_constant
        
#         location_resource_names.append(geo_target_constant.resource_name)

#     # get the first one that is the one selected by the user
#     geo_targets.append(location_resource_names[0])

# print(geo_targets)


# # locations = geo_targets
# # locations = ['geoTargetConstants/1000073', 'geoTargetConstants/9041027']
# for location in geo_targets:
#     # Construct location information using the given geo target constant.
#     location_info = client.get_type("LocationInfo")
#     location_info.geo_target_constant = location
#     suggestion_info.location_list.locations.append(location_info)

# # Add the KeywordThemeInfo objects to the SuggestionInfo object.
# suggestion_info.keyword_themes.extend(infos)
# # print('suggestion_info:')
# # print(suggestion_info)

# # Set either of the business_location_id or business_name, depending on
# # whichever is provided.
# # if business_location_id:
# #     suggestion_info.business_location_id = business_location_id
# # else:
# #     suggestion_info.business_context.business_name = business_name
# suggestion_info.business_context.business_name = business_name

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

# print('suggestion_info:')
# print(suggestion_info)

# # step 2: get ad suggestion
# sc_suggest_service = client.get_service("SmartCampaignSuggestService")
# request = client.get_type("SuggestSmartCampaignAdRequest")
# request.customer_id = customer_id

# # Unlike the SuggestSmartCampaignBudgetOptions method, it's only possible
# # to use suggestion_info to retrieve ad creative suggestions.
# request.suggestion_info = suggestion_info

# # Issue a request to retrieve ad creative suggestions.
# response = sc_suggest_service.suggest_smart_campaign_ad(request=request)
# print('response:')
# print(response)

# # The SmartCampaignAdInfo object in the response contains a list of up to
# # three headlines and two descriptions. Note that some of the suggestions
# # may have empty strings as text. Before setting these on the ad you should
# # review them and filter out any empty values.
# ad_suggestions = response.ad_info
# print('ad_suggestions:')
# print(ad_suggestions)

# print("The following headlines were suggested:")
# for headline in ad_suggestions.headlines:
#     print(f"\t{headline.text or '<None>'}")

# print("And the following descriptions were suggested:")
# for description in ad_suggestions.descriptions:
#     print(f"\t{description.text or '<None>'}")

# print(ad_suggestions)

'''
Edit keyword themes - Current bug doesn't let you query the keyword_themes (500 Internal error encountered.)
Parameters needed: credentials, customer_id, campaign_id, new_display_name
'''
# customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14652304508)

# # get the resource_name and text assets (headlines and descriptions)
# ga_service = client.get_service("GoogleAdsService")
# query = (f'''
# SELECT campaign.id, campaign_criterion.resource_name, 
# campaign_criterion.keyword_theme.keyword_theme_constant, 
# campaign_criterion.keyword_theme.free_form_keyword_theme  
# FROM campaign_criterion 
# WHERE campaign.id = {campaign_id} ''')
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
#         kw_theme_constant = row.campaign_criterion.keyword_theme.keyword_theme_constant
#         kw_theme_free_form = row.campaign_criterion.keyword_theme.free_form_keyword_theme
#         print('kw_theme_constant:')
#         print(kw_theme_constant) 
#         print('kw_theme_free_form:')
#         print(kw_theme_free_form) 

'''
Edit geo location targeting
Parameters needed: credentials, customer_id, campaign_id,
'''
customer_id = str(2916870939) # billing set up      | account created via ui
campaign_id = str(14652304508)

# get the current geo location targets names
ga_service = client.get_service("GoogleAdsService")
query = (f'''
SELECT campaign.id, campaign_criterion.resource_name, 
campaign_criterion.location.geo_target_constant  
FROM campaign_criterion 
WHERE campaign.id = {campaign_id} ''')
response = ga_service.search_stream(customer_id=customer_id, query=query)

locations = []
for batch in response:
    for row in batch.results:
        geo_target_constants = row.campaign_criterion.location.geo_target_constant
        # print('geo_target_constants:')
        # print(geo_target_constants) 
        if geo_target_constants:
            locations.append(geo_target_constants)

print('locations:')
print(locations)

location_targets = []
for location in locations:
    # Construct location information using the given geo target constant.
    location_info = client.get_type("LocationInfo")
    location_info.geo_target_constant = location
    location_targets.append(location_info)

print('location_targets:')
print(location_targets)

for geo_constants in locations:

    print(geo_constants)
    query = (f'''
    SELECT geo_target_constant.name,  
    campaign_criterion.location.geo_target_constant  
    FROM geo_target_constant 
    WHERE campaign_criterion.location.geo_target_constant = {geo_constants} ''')
    response = ga_service.search_stream(customer_id=customer_id, query=query)

    geo_target_names = []
    for batch in response:
        for row in batch.results:
            geo_target_constant_name = row.geo_target_constant.name
            geo_target_names.append(geo_target_constant_name)

print('geo_target_names:')
print(geo_target_names)
'''
Edit ad text - Error saying that headlines and descriptions cannot be mutated
Parameters needed: credentials, customer_id, campaign_id, new_headline_1,
new_headline_2, new_headline_3, new_desc_1, new_desc_2
'''
# customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14652304508)
# new_headline_1 = 'edit head 1 test'
# new_headline_2 = 'edit head 2 test'
# new_headline_3 = 'edit head 3 test'
# new_desc_1 = 'edit desc 1 test'
# new_desc_2 = 'edit desc 2 test'

# # get the resource_name and text assets (headlines and descriptions)
# ga_service = client.get_service("GoogleAdsService")
# query = (f'''
# SELECT campaign.id, ad_group_ad.ad.id, ad_group_ad.resource_name, 
# ad_group_ad.ad.smart_campaign_ad.headlines, 
# ad_group_ad.ad.smart_campaign_ad.descriptions  
# FROM ad_group_ad 
# WHERE campaign.id = {campaign_id} ''')
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
#         ad_group_ad_id = row.ad_group_ad.ad.id
#         ad_group_ad_text_ad_descriptions = row.ad_group_ad.ad.smart_campaign_ad.descriptions
#         ad_group_ad_text_ad_headlines = row.ad_group_ad.ad.smart_campaign_ad.headlines
#         ad_group_ad_resource_name = row.ad_group_ad.resource_name
#         print('ad_group_ad_resource_name:')
#         print(ad_group_ad_resource_name) 

# current_headline_1_user = ad_group_ad_text_ad_headlines[0].text
# current_headline_2_user = ad_group_ad_text_ad_headlines[1].text
# current_headline_3_user = ad_group_ad_text_ad_headlines[2].text
# print('current_headline_1_user:')
# print(current_headline_1_user)
# print('current_headline_2_user:')
# print(current_headline_2_user)
# print('current_headline_3_user:')
# print(current_headline_3_user)
# current_desc_1_user = ad_group_ad_text_ad_descriptions[0].text
# current_desc_2_user = ad_group_ad_text_ad_descriptions[1].text
# print('current_desc_1_user:')
# print(current_desc_1_user)
# print('current_desc_2_user:')
# print(current_desc_2_user)

# # start update ad group ad mutate operation
# mutate_operation = client.get_type("MutateOperation")
# ad_group_ad = mutate_operation.ad_group_ad_operation.update

# # set the resource name of the ad_group_ad
# ad_group_ad.resource_name = ad_group_ad_resource_name
# print('ad_group_ad:')
# print(ad_group_ad)

# # set new ad
# ad = ad_group_ad.ad.smart_campaign_ad

# headline_1 = client.get_type("AdTextAsset")
# headline_1.text = new_headline_1
# headline_2 = client.get_type("AdTextAsset")
# headline_2.text = new_headline_2
# headline_3 = client.get_type("AdTextAsset")
# headline_3.text = new_headline_3
# ad.headlines.extend([headline_1, headline_2, headline_3])

# description_1 = client.get_type("AdTextAsset")
# description_1.text = new_desc_1
# description_2 = client.get_type("AdTextAsset")
# description_2.text = new_desc_2
# ad.descriptions.extend([description_1, description_2])

# print('ad:')
# print(ad)

# ad_group_ad_operation = mutate_operation

# # create a FieldMask for the fields updated in the campaign and 
# # copy it to the operation's update_mask field
# client.copy_from(
#     mutate_operation.ad_group_ad_operation.update_mask,
#     protobuf_helpers.field_mask(None, ad_group_ad._pb),
# )

# # send the mutate request
# response = ga_service.mutate(
#     customer_id=customer_id,
#     mutate_operations=[
#         # ad_group_operation, 
#         ad_group_ad_operation,
#     ],
# )
# print('response:')
# print(response)

# for result in response.mutate_operation_responses:
#         resource_type = "unrecognized"
#         resource_name = "not found"

#         if result._pb.HasField("campaign_budget_result"):
#             resource_type = "CampaignBudget"
#             resource_name = result.campaign_budget_result.resource_name
#         elif result._pb.HasField("campaign_result"):
#             resource_type = "Campaign"
#             resource_name = result.campaign_result.resource_name
#         elif result._pb.HasField("smart_campaign_setting_result"):
#             resource_type = "SmartCampaignSettingResult"
#             resource_name = result.smart_campaign_setting_result.resource_name
#         elif result._pb.HasField("campaign_criterion_result"):
#             resource_type = "CampaignCriterion"
#             resource_name = result.campaign_criterion_result.resource_name
#         elif result._pb.HasField("ad_group_result"):
#             resource_type = "AdGroup"
#             resource_name = result.ad_group_result.resource_name
#         elif result._pb.HasField("ad_group_ad_result"):
#             resource_type = "AdGroupAd"
#             resource_name = result.ad_group_ad_result.resource_name

#         print(
#             f"Edited text assets of campaign with resource_name: '{resource_name}'."
#         )


'''
Edit budget of smart campaign - OK
Parameters needed: credentials, customer_id, campaign_id, new_budget (in micros)
'''
# customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14652304508)
# new_budget = 3*1000000

# # get the current budget id and amount
# ga_service = client.get_service("GoogleAdsService")
# query = ('SELECT campaign.id, campaign_budget.id, campaign_budget.amount_micros '
# 'FROM campaign_budget '
# 'WHERE campaign.id = '+ campaign_id + ' ')
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
#         budget_id = row.campaign_budget.id
#         current_budget_micros = row.campaign_budget.amount_micros
#         print('budget_id is:')
#         print(budget_id)
#         print('current_budget_micros:')
#         print(current_budget_micros)    # you will show the current budget to the user

# # start update mutate operation
# mutate_operation = client.get_type("MutateOperation")
# campaign_budget_operation = mutate_operation.campaign_budget_operation
# campaign_budget = campaign_budget_operation.update

# # set new budget amount
# campaign_budget.amount_micros = new_budget



# # use  the buget id for the CampaignBudgetservice to set the resource name of the campaign budget
# campaign_budget.resource_name = client.get_service(
#     "CampaignBudgetService"
# ).campaign_budget_path(customer_id, budget_id)

# # Retrieve a FieldMask for the fields configured in the campaign.
# client.copy_from(
#     mutate_operation.campaign_budget_operation.update_mask,
#     protobuf_helpers.field_mask(None, campaign_budget._pb),
# )

# # send the mutate request
# response = ga_service.mutate(
#     customer_id=customer_id,
#     mutate_operations=[
#         mutate_operation,
#     ],
# )

# for result in response.mutate_operation_responses:
#         resource_type = "unrecognized"
#         resource_name = "not found"

#         if result._pb.HasField("campaign_budget_result"):
#             resource_type = "CampaignBudget"
#             resource_name = result.campaign_budget_result.resource_name
#         elif result._pb.HasField("campaign_result"):
#             resource_type = "Campaign"
#             resource_name = result.campaign_result.resource_name
#         elif result._pb.HasField("smart_campaign_setting_result"):
#             resource_type = "SmartCampaignSettingResult"
#             resource_name = result.smart_campaign_setting_result.resource_name
#         elif result._pb.HasField("campaign_criterion_result"):
#             resource_type = "CampaignCriterion"
#             resource_name = result.campaign_criterion_result.resource_name
#         elif result._pb.HasField("ad_group_result"):
#             resource_type = "AdGroup"
#             resource_name = result.ad_group_result.resource_name
#         elif result._pb.HasField("ad_group_ad_result"):
#             resource_type = "AdGroupAd"
#             resource_name = result.ad_group_ad_result.resource_name

#         print(
#             f"Edited campaign with resource_name: '{resource_name}' to new budget {new_budget} micros."
#         )



'''
Pause smart campaign - OK
Parameters needed: credentials, customer_id, campaign_id
'''
# customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14652304508)
# # get the current campaign name and status
# ga_service = client.get_service("GoogleAdsService")
# query = ('SELECT campaign.id, campaign.name, campaign.status '
# 'FROM campaign '
# 'WHERE campaign.id = '+ campaign_id + ' ')
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
#         campaign_name = row.campaign.name
#         current_campaign_status = row.campaign.status
#         print('campaign_name is:')
#         print(campaign_name)
#         print('current_campaign_status:')
#         print(current_campaign_status)    # you will show the name and current status to the user

# # start update mutate operation
# mutate_operation = client.get_type("MutateOperation")
# campaign = (
#     mutate_operation.campaign_operation.update
# )

# # get CampaignService for the campaign_id
# campaign_service = client.get_service("CampaignService")
# campaign.resource_name = campaign_service.campaign_path(
#     customer_id, campaign_id
# )

# # pause the campaign
# campaign.status = client.enums.CampaignStatusEnum.PAUSED

# # create field mask to update operation
# client.copy_from(
#     mutate_operation.campaign_operation.update_mask,
#     protobuf_helpers.field_mask(None, campaign._pb),
# )

# # send the mutate request
# response = ga_service.mutate(
#     customer_id=customer_id,
#     mutate_operations=[
#         mutate_operation,
#     ],
# )

# for result in response.mutate_operation_responses:
#         resource_type = "unrecognized"
#         resource_name = "not found"

#         if result._pb.HasField("campaign_budget_result"):
#             resource_type = "CampaignBudget"
#             resource_name = result.campaign_budget_result.resource_name
#         elif result._pb.HasField("campaign_result"):
#             resource_type = "Campaign"
#             resource_name = result.campaign_result.resource_name
#         elif result._pb.HasField("smart_campaign_setting_result"):
#             resource_type = "SmartCampaignSettingResult"
#             resource_name = result.smart_campaign_setting_result.resource_name
#         elif result._pb.HasField("campaign_criterion_result"):
#             resource_type = "CampaignCriterion"
#             resource_name = result.campaign_criterion_result.resource_name
#         elif result._pb.HasField("ad_group_result"):
#             resource_type = "AdGroup"
#             resource_name = result.ad_group_result.resource_name
#         elif result._pb.HasField("ad_group_ad_result"):
#             resource_type = "AdGroupAd"
#             resource_name = result.ad_group_ad_result.resource_name

#         print(
#             f"Paused campaign with resource_name: '{resource_name}'."
#         )

'''
Enable smart campaign - OK
Parameters needed: credentials, customer_id, campaign_id
'''
# customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14652304508)

# # get the current campaign name and status
# ga_service = client.get_service("GoogleAdsService")
# query = ('SELECT campaign.id, campaign.name, campaign.status '
# 'FROM campaign '
# 'WHERE campaign.id = '+ campaign_id + ' ')
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
#         campaign_name = row.campaign.name
#         current_campaign_status = row.campaign.status
#         print('campaign_name is:')
#         print(campaign_name)
#         print('current_campaign_status:')
#         print(current_campaign_status)    # you will show the name and current status to the user

# # start update mutate operation
# mutate_operation = client.get_type("MutateOperation")
# campaign = (
#     mutate_operation.campaign_operation.update
# )

# # get CampaignService for the campaign_id
# campaign_service = client.get_service("CampaignService")
# campaign.resource_name = campaign_service.campaign_path(
#     customer_id, campaign_id
# )

# # enable the campaign
# campaign.status = client.enums.CampaignStatusEnum.ENABLED

# # create field mask to update operation
# client.copy_from(
#     mutate_operation.campaign_operation.update_mask,
#     protobuf_helpers.field_mask(None, campaign._pb),
# )

# # send the mutate request
# response = ga_service.mutate(
#     customer_id=customer_id,
#     mutate_operations=[
#         mutate_operation,
#     ],
# )

# for result in response.mutate_operation_responses:
#         resource_type = "unrecognized"
#         resource_name = "not found"

#         if result._pb.HasField("campaign_budget_result"):
#             resource_type = "CampaignBudget"
#             resource_name = result.campaign_budget_result.resource_name
#         elif result._pb.HasField("campaign_result"):
#             resource_type = "Campaign"
#             resource_name = result.campaign_result.resource_name
#         elif result._pb.HasField("smart_campaign_setting_result"):
#             resource_type = "SmartCampaignSettingResult"
#             resource_name = result.smart_campaign_setting_result.resource_name
#         elif result._pb.HasField("campaign_criterion_result"):
#             resource_type = "CampaignCriterion"
#             resource_name = result.campaign_criterion_result.resource_name
#         elif result._pb.HasField("ad_group_result"):
#             resource_type = "AdGroup"
#             resource_name = result.ad_group_result.resource_name
#         elif result._pb.HasField("ad_group_ad_result"):
#             resource_type = "AdGroupAd"
#             resource_name = result.ad_group_ad_result.resource_name

#         print(
#             f"Enabled campaign with resource_name: '{resource_name}'."
#         )


'''
Remove campaign - OK
Parameters needed: credentials, customer_id, campaign_id
'''
# customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14652304508)

# # get the current campaign name and status
# ga_service = client.get_service("GoogleAdsService")
# query = ('SELECT campaign.id, campaign.name, campaign.status '
# 'FROM campaign '
# 'WHERE campaign.id = '+ campaign_id + ' ')
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
#         campaign_name = row.campaign.name
#         current_campaign_status = row.campaign.status
#         print('campaign_name is:')
#         print(campaign_name)
#         print('current_campaign_status:')
#         print(current_campaign_status)    # you will show the name and current status to the user

# campaign_service = client.get_service("CampaignService")
# campaign_operation = client.get_type("CampaignOperation")

# resource_name = campaign_service.campaign_path(customer_id, campaign_id)
# campaign_operation.remove = resource_name

# campaign_response = campaign_service.mutate_campaigns(
#     customer_id=customer_id, operations=[campaign_operation]
# )

# print(f"Removed campaign {campaign_response.results[0].resource_name}.")

'''
get ad_group_id and ad_id - OK
'''
# customer_id = str(2916870939) # billing set up      | account created via ui
# campaign_id = str(14652304508)

# ga_service = client.get_service("GoogleAdsService")


# query = ('SELECT ad_group.id '
# 'FROM ad_group '
# 'WHERE campaign.id = '+ campaign_id + ' ')

# # Issues a search request using streaming.
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
#         ad_group_id = row.ad_group.id
#         ad_id = row.ad_group_ad.ad.id
#         print('ad_group_id is:')
#         print(ad_group_id)

# query = ('SELECT ad_group_ad.ad.id '
# 'FROM ad_group_ad '
# 'WHERE campaign.id = '+ campaign_id + ' ')

# # Issues a search request using streaming.
# response = ga_service.search_stream(customer_id=customer_id, query=query)

# for batch in response:
#     for row in batch.results:
        
#         ad_id = row.ad_group_ad.ad.id
       
#         print('ad_id:')
#         print(ad_id)



'''
Check if customer id has set up billing - OK
'''

# # customer_id = str(4037974191) # billing set up    | account created via api
# # customer_id = str(4597538560) # no billing        | account created via api
# customer_id = str(2916870939) # billing set up      | account created via ui

# ga_service = client.get_service("GoogleAdsService")

# query = """
#     SELECT
#         billing_setup.id,
#         billing_setup.status,
#         billing_setup.payments_account,
#         billing_setup.payments_account_info.payments_account_id,
#         billing_setup.payments_account_info.payments_account_name,
#         billing_setup.payments_account_info.payments_profile_id,
#         billing_setup.payments_account_info.payments_profile_name,
#         billing_setup.payments_account_info.secondary_payments_profile_id
#     FROM billing_setup"""

# response = ga_service.search_stream(customer_id=customer_id, query=query)

# print("Found the following billing setup results:")
# for batch in response:
#     for row in batch.results:
#         billing_setup = row.billing_setup
#         pai = billing_setup.payments_account_info

#         if pai.secondary_payments_profile_id:
#             secondary_payments_profile_id = (
#                 pai.secondary_payments_profile_id
#             )
#         else:
#             secondary_payments_profile_id = "None"

#         print(
#             f"Billing setup with ID {billing_setup.id}, "
#             f'status "{billing_setup.status.name}", '
#             f'payments_account "{billing_setup.payments_account}" '
#             f"payments_account_id {pai.payments_account_id}, "
#             f'payments_account_name "{pai.payments_account_name}", '
#             f"payments_profile_id {pai.payments_profile_id}, "
#             f'payments_profile_name "{pai.payments_profile_name}", '
#             "secondary_payments_profile_id "
#             f"{secondary_payments_profile_id}."
#         )

# try:
#     billing_status = billing_setup.status.name
# except NameError:
#     billing_status = "no billing"

# print('billing_status:')
# print(billing_status)


'''
Link accounts - OK
'''
# # This example assumes that the same credentials will work for both
# # customers, but that may not be the case. If you need to use different
# # credentials for each customer, then you may either update the client
# # configuration or instantiate two clients, where at least one points to
# # a specific configuration file so that both clients don't read the same
# # file located in the $HOME dir.
# customer_client_link_service = client.get_service(
#     "CustomerClientLinkService"
# )

# # Extend an invitation to the client while authenticating as the manager.
# client_link_operation = client.get_type("CustomerClientLinkOperation")
# client_link = client_link_operation.create
# client_link.client_customer = customer_client_link_service.customer_path(customer_id)
# client_link.status = client.enums.ManagerLinkStatusEnum.PENDING

# response = customer_client_link_service.mutate_customer_client_link(
#     customer_id=GOOGLE_LOGIN_CUSTOMER_ID, operation=client_link_operation
# )
# resource_name = response.results[0].resource_name

# print(
#     f'Extended an invitation from customer "{GOOGLE_LOGIN_CUSTOMER_ID}" to '
#     f'customer "{customer_id}" with client link resource_name '
#     f'"{resource_name}"'
# )

# # Find the manager_link_id of the link we just created, so we can construct
# # the resource name for the link from the client side. Note that since we
# # are filtering by resource_name, a unique identifier, only one
# # customer_client_link resource will be returned in the response
# query = f'''
#     SELECT
#         customer_client_link.manager_link_id
#     FROM
#         customer_client_link
#     WHERE
#         customer_client_link.resource_name = "{resource_name}"'''

# ga_service = client.get_service("GoogleAdsService")

# try:
#     response = ga_service.search(
#         customer_id=GOOGLE_LOGIN_CUSTOMER_ID, query=query
#     )
#     # Since the googleads_service.search method returns an iterator we need
#     # to initialize an iteration in order to retrieve results, even though
#     # we know the query will only return a single row.
#     for row in response.result:
#         manager_link_id = row.customer_client_link.manager_link_id
# except GoogleAdsException as ex:
#     print(
#         f'Request with ID "{ex.request_id}" failed with status '
#         f'"{ex.error.code().name}" and includes the following errors:'
#     )
#     for error in ex.failure.errors:
#         print(f'\tError with message "{error.message}".')
#         if error.location:
#             for field_path_element in error.location.field_path_elements:
#                 print(f"\t\tOn field: {field_path_element.field_name}")
#     sys.exit(1)

# customer_manager_link_service = client.get_service(
#     "CustomerManagerLinkService"
# )
# manager_link_operation = client.get_type("CustomerManagerLinkOperation")
# manager_link = manager_link_operation.update
# manager_link.resource_name = (
#     customer_manager_link_service.customer_manager_link_path(
#         customer_id,
#         GOOGLE_LOGIN_CUSTOMER_ID,
#         manager_link_id,
#     )
# )

# manager_link.status = client.enums.ManagerLinkStatusEnum.ACTIVE
# client.copy_from(
#     manager_link_operation.update_mask,
#     protobuf_helpers.field_mask(None, manager_link._pb),
# )

# response = customer_manager_link_service.mutate_customer_manager_link(
#     customer_id=GOOGLE_LOGIN_CUSTOMER_ID, operations=[manager_link_operation]
# )
# print(
#     "Client accepted invitation with resource_name: "
#     f'"{response.results[0].resource_name}"'
# )