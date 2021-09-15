import os
import sys
from uuid import uuid4

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

from google.api_core import protobuf_helpers

from .models import KeywordThemesRecommendations

'''
Parameter values used in the function to create sc.
These values were selected on the frontend by a user (except refresh_token and manager id)
'''
customer_id = str(2916870939)   # successfully created sc via api
customer_id = str(4037974191)   # failed creating sc via api
customer_id = str(4597538560)   # failed creating sc via api
GOOGLE_LOGIN_CUSTOMER_ID = "4642579541" # this is the manager account that is linked to those 3 client accounts
refresh_token = 'YOUR_REFRESH_TOKEN'
display_name = ["ropa para embarazadas","corpiños para embarazadas","ropa formal para embarazadas","ropa de fiesta para embarazadas","ropa para embarazadas barata"]
geo_target_names = ["buenos aires","martinez","san isidro","olivos"]
language_code = 'es'
country_code = 'AR'
selected_budget = '1190000'
phone_number = '1156574910'
landing_page = 'https://www.enjoymommyhood.com.ar/'
business_name = 'Enjoy Mommyhood'
headline_1_user = 'head test 1'
headline_2_user = 'head test 2'
headline_3_user = 'head test 3'
desc_1_user = 'desc test 1'
desc_2_user = 'desc test 2'
campaign_name = 'whatever'+str(uuid4())

'''
Function to create sc
'''

def create_smart(
    refresh_token, customer_id, display_name, geo_target_names,
    language_code, country_code, selected_budget,
    phone_number, landing_page, business_name,
    headline_1_user, headline_2_user, headline_3_user,
    desc_1_user, desc_2_user, campaign_name):
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
        "login_customer_id": GOOGLE_LOGIN_CUSTOMER_ID}

        client = GoogleAdsClient.load_from_dict(credentials)

        # Additional configuration to maintain all mutate operations tied together
        _BUDGET_TEMPORARY_ID = "-1"
        _SMART_CAMPAIGN_TEMPORARY_ID = "-2"
        _AD_GROUP_TEMPORARY_ID = "-3"

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

        # Step 2: get location targets with the name format the api needs to create campaign

        # Setp 2.1: get geo target constants for the geo target names selected by user
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

        # Setp 2.2: get the LocationInfo type to set location targets as the api needs
        location_targets = []
        for location in geo_targets:
            # Construct location information using the given geo target constant.
            location_info = client.get_type("LocationInfo")
            location_info.geo_target_constant = location
            location_targets.append(location_info)

        print('location_targets:')
        print(location_targets)


        # Step 3: create budget operation for the campaign to be created
        """Creates a MutateOperation that creates a new CampaignBudget.
        A temporary ID will be assigned to this campaign budget so that it can be
        referenced by other objects being created in the same Mutate request.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
            suggested_budget_amount: a numeric daily budget amount in micros.
        Returns:
            a MutateOperation that creates a CampaignBudget.
        """
        mutate_operation = client.get_type("MutateOperation")
        campaign_budget_operation = mutate_operation.campaign_budget_operation
        campaign_budget = campaign_budget_operation.create
        campaign_budget.name = campaign_name+' This name will not appear in your ad '+str(uuid4())
        # A budget used for Smart campaigns must have the type SMART_CAMPAIGN.
        # Note that the field name "type_" is an implementation detail in Python,
        # the field's actual name is "type".
        campaign_budget.type_ = client.enums.BudgetTypeEnum.SMART_CAMPAIGN
        # The suggested budget amount from the SmartCampaignSuggestService is
        # a daily budget. We don't need to specify that here, because the budget
        # period already defaults to DAILY.
        campaign_budget.amount_micros = int(selected_budget)
        # Set a temporary ID in the budget's resource name so it can be referenced
        # by the campaign in later steps.
        campaign_budget.resource_name = client.get_service(
            "CampaignBudgetService"
        ).campaign_budget_path(customer_id, _BUDGET_TEMPORARY_ID)

        campaign_budget_operation = mutate_operation
        print('campaign_budget_operation')
        print(campaign_budget_operation)

        # Step 4: create SC operation
        """Creates a MutateOperation that creates a new Smart campaign.
        A temporary ID will be assigned to this campaign so that it can
        be referenced by other objects being created in the same Mutate request.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        Returns:
            a MutateOperation that creates a campaign.
        """
        mutate_operation = client.get_type("MutateOperation")
        campaign = mutate_operation.campaign_operation.create
        campaign.name = campaign_name+' -Created using Fran Ads. This name will not appear in your ad- '+str(uuid4())
        # Set the campaign status as PAUSED. The campaign is the only entity in
        # the mutate request that should have its' status set.
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        # Campaign.AdvertisingChannelType is required to be SMART.
        campaign.advertising_channel_type = (
            client.enums.AdvertisingChannelTypeEnum.SMART
        )
        # Campaign.AdvertisingChannelSubType is required to be SMART_CAMPAIGN.
        campaign.advertising_channel_sub_type = (
            client.enums.AdvertisingChannelSubTypeEnum.SMART_CAMPAIGN
        )
        # Assign the resource name with a temporary ID.
        campaign_service = client.get_service("CampaignService")
        campaign.resource_name = campaign_service.campaign_path(
            customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
        )
        # Set the budget using the given budget resource name.
        campaign.campaign_budget = campaign_service.campaign_budget_path(
            customer_id, _BUDGET_TEMPORARY_ID
        )


        smart_campaign_operation = mutate_operation
        print('smart_campaign_operation:')
        print(smart_campaign_operation)

        # Step 5: create SC setting operation
        """Creates a MutateOperation to create a new SmartCampaignSetting.
        SmartCampaignSettings are unique in that they only support UPDATE
        operations, which are used to update and create them. Below we will
        use a temporary ID in the resource name to associate it with the
        campaign created in the previous step.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
            business_location_id: the ID of a Google My Business location.
            business_name: the name of a Google My Business.
        Returns:
            a MutateOperation that creates a SmartCampaignSetting.
        """
        mutate_operation = client.get_type("MutateOperation")
        smart_campaign_setting = (
            mutate_operation.smart_campaign_setting_operation.update
        )
        # Set a temporary ID in the campaign setting's resource name to associate it
        # with the campaign created in the previous step.
        smart_campaign_setting.resource_name = client.get_service(
            "SmartCampaignSettingService"
        ).smart_campaign_setting_path(customer_id, _SMART_CAMPAIGN_TEMPORARY_ID)

        # Below we configure the SmartCampaignSetting using many of the same
        # details used to generate a budget suggestion.
        smart_campaign_setting.phone_number.country_code = country_code
        smart_campaign_setting.phone_number.phone_number = phone_number
        smart_campaign_setting.final_url = landing_page
        smart_campaign_setting.advertising_language_code = language_code

        # It's required that either a business location ID or a business name is
        # added to the SmartCampaignSetting.
        # if business_location_id:
        #     smart_campaign_setting.business_location_id = business_location_id
        # else:
        #     smart_campaign_setting.business_name = business_name
        smart_campaign_setting.business_name = business_name

        # Set the update mask on the operation. This is required since the smart
        # campaign setting is created in an UPDATE operation. Here the update
        # mask will be a list of all the fields that were set on the
        # SmartCampaignSetting.
        client.copy_from(
            mutate_operation.smart_campaign_setting_operation.update_mask,
            protobuf_helpers.field_mask(None, smart_campaign_setting._pb),
        )

        smart_campaign_setting_operation = mutate_operation

        print('smart_campaign_setting_operation:')
        print(smart_campaign_setting_operation)

        # Step 6: create campaign criterion operation

        """Creates a list of MutateOperations that create new campaign criteria.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
            keyword_theme_infos: a list of KeywordThemeInfos.
        Returns:
            a list of MutateOperations that create new campaign criteria.
        """
        campaign_service = client.get_service("CampaignService")

        operations = []
        for info in infos:
            mutate_operation = client.get_type("MutateOperation")
            campaign_criterion = (
                mutate_operation.campaign_criterion_operation.create
            )
            # Set the campaign ID to a temporary ID.
            campaign_criterion.campaign = campaign_service.campaign_path(
                customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
            )
            # Set the criterion type to KEYWORD_THEME.
            campaign_criterion.type_ = client.enums.CriterionTypeEnum.KEYWORD_THEME
            # Set the keyword theme to the given KeywordThemeInfo.
            campaign_criterion.keyword_theme = info
            # Add the mutate operation to the list of other operations.
            operations.append(mutate_operation)

        # create location criterion to add locations the user wants to target
        for i in location_targets:
            mutate_operation = client.get_type("MutateOperation")
            campaign_criterion = (
                mutate_operation.campaign_criterion_operation.create
            )
            # Set the campaign ID to a temporary ID.
            campaign_criterion.campaign = campaign_service.campaign_path(
                customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
            )
            # Set the criterion type to LOCATION.
            campaign_criterion.type_ = client.enums.CriterionTypeEnum.LOCATION
            # Set the location to the given location.
            campaign_criterion.location = i
            # Add the mutate operation to the list of other operations.
            operations.append(mutate_operation)

        campaign_criterion_operations = operations

        print('campaign_criterion_operations:')
        print(campaign_criterion_operations)

        # Step 7: create ad group operation
        """Creates a MutateOperation that creates a new ad group.
        A temporary ID will be used in the campaign resource name for this
        ad group to associate it with the Smart campaign created in earlier steps.
        A temporary ID will also be used for its own resource name so that we can
        associate an ad group ad with it later in the process.
        Only one ad group can be created for a given Smart campaign.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        Returns:
            a MutateOperation that creates a new ad group.
        """
        mutate_operation = client.get_type("MutateOperation")
        ad_group = mutate_operation.ad_group_operation.create
        # Set the ad group ID to a temporary ID.
        ad_group.resource_name = client.get_service("AdGroupService").ad_group_path(
            customer_id, _AD_GROUP_TEMPORARY_ID
        )
        ad_group.name = campaign_name+'This name will not appear in your ad '+str(uuid4())
        # Set the campaign ID to a temporary ID.
        ad_group.campaign = client.get_service("CampaignService").campaign_path(
            customer_id, _SMART_CAMPAIGN_TEMPORARY_ID
        )
        # The ad group type must be set to SMART_CAMPAIGN_ADS.
        ad_group.type_ = client.enums.AdGroupTypeEnum.SMART_CAMPAIGN_ADS

        ad_group_operation = mutate_operation

        print('ad_group_operation:')
        print(ad_group_operation)

        # step 8: create ad group ad operation
        """Creates a MutateOperation that creates a new ad group ad.
        A temporary ID will be used in the ad group resource name for this
        ad group ad to associate it with the ad group created in earlier steps.
        Args:
            client: an initialized GoogleAdsClient instance.
            customer_id: a client customer ID.
        Returns:
            a MutateOperation that creates a new ad group ad.
        """
        mutate_operation = client.get_type("MutateOperation")
        ad_group_ad = mutate_operation.ad_group_ad_operation.create
        # Set the ad group ID to a temporary ID.
        ad_group_ad.ad_group = client.get_service("AdGroupService").ad_group_path(
            customer_id, _AD_GROUP_TEMPORARY_ID
        )
        # Set the type to SMART_CAMPAIGN_AD.
        ad_group_ad.ad.type_ = client.enums.AdTypeEnum.SMART_CAMPAIGN_AD
        ad = ad_group_ad.ad.smart_campaign_ad
        # At most, three headlines can be specified for a Smart campaign ad.
        headline_1 = client.get_type("AdTextAsset")
        headline_1.text = headline_1_user
        headline_2 = client.get_type("AdTextAsset")
        headline_2.text = headline_2_user
        headline_3 = client.get_type("AdTextAsset")
        headline_3.text = headline_3_user
        ad.headlines.extend([headline_1, headline_2, headline_3])
        # At most, two descriptions can be specified for a Smart campaign ad.
        description_1 = client.get_type("AdTextAsset")
        description_1.text = desc_1_user
        description_2 = client.get_type("AdTextAsset")
        description_2.text = desc_2_user
        ad.descriptions.extend([description_1, description_2])

        ad_group_ad_operation = mutate_operation

        print('ad_group_ad_operation:')
        print(ad_group_ad_operation)

        # step 9: create smart campaign
        googleads_service = client.get_service("GoogleAdsService")

        # Send the operations into a single Mutate request.
        response = googleads_service.mutate(
            customer_id=customer_id,
            mutate_operations=[
                # It's important to create these entities in this order because
                # they depend on each other, for example the SmartCampaignSetting
                # and ad group depend on the campaign, and the ad group ad depends
                # on the ad group.
                campaign_budget_operation,
                smart_campaign_operation,
                smart_campaign_setting_operation,
                # Expand the list of campaign criterion operations into the list of
                # other mutate operations
                *campaign_criterion_operations,
                ad_group_operation,
                ad_group_ad_operation,
            ],
        )

        """Prints the details of a MutateGoogleAdsResponse.
        Parses the "response" oneof field name and uses it to extract the new
        entity's name and resource name.
        Args:
            response: a MutateGoogleAdsResponse object.
        """
        # Parse the Mutate response to print details about the entities that
        # were created by the request.
        for result in response.mutate_operation_responses:
            resource_type = "unrecognized"
            resource_name = "not found"

            if result._pb.HasField("campaign_budget_result"):
                resource_type = "CampaignBudget"
                resource_name = result.campaign_budget_result.resource_name
            elif result._pb.HasField("campaign_result"):
                resource_type = "Campaign"
                resource_name = result.campaign_result.resource_name
            elif result._pb.HasField("smart_campaign_setting_result"):
                resource_type = "SmartCampaignSettingResult"
                resource_name = result.smart_campaign_setting_result.resource_name
            elif result._pb.HasField("campaign_criterion_result"):
                resource_type = "CampaignCriterion"
                resource_name = result.campaign_criterion_result.resource_name
            elif result._pb.HasField("ad_group_result"):
                resource_type = "AdGroup"
                resource_name = result.ad_group_result.resource_name
            elif result._pb.HasField("ad_group_ad_result"):
                resource_type = "AdGroupAd"
                resource_name = result.ad_group_ad_result.resource_name

            print(
                f"Created a(n) {resource_type} with "
                f"resource_name: '{resource_name}'."
            )

        print('smart campaign created!!')
        response = 'smart campaign created'
        return response

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