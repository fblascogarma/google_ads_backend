# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.db import models

# Create your models here.
class Article(models.Model):                    # you will create a table called Article
    title = models.CharField(max_length=100)    # ids are created automatically so you don't have to create an id
    description = models.TextField()

    def __str__(self): 
        return self.title

# Model to store the access code and refresh token of users to handle their Google Ads via the API
class AdWordsCredentials(models.Model):                   
    mytoken = models.CharField(max_length=500)
    google_access_code = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)

    def __str__(self): 
        return self.mytoken, self.google_access_code, self.refresh_token

# Model to store the access code that Google services provide to get the refresh token
class AntiForgeryToken(models.Model):                   
    mytoken = models.CharField(max_length=600)
    google_access_code = models.CharField(max_length=600)
    passthrough_val = models.CharField(max_length=600)
    

    def __str__(self): 
        return self.mytoken, self.google_access_code, self.passthrough_val

# Model for the refresh token
class RefreshToken(models.Model):                   
    mytoken = models.CharField(max_length=500)
    refreshToken = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken

# Model to store mytoken
class MyToken(models.Model):                   
    mytoken = models.CharField(max_length=500)

    def __str__(self): 
        return self.mytoken

# Model to store refresh token and customer id
class CustomerID(models.Model):                   
    refreshToken = models.CharField(max_length=500)
    customer_id = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.customer_id

# Model to store frontend data to get info of campaigns
class Reporting(models.Model):                   
    # we make the refreshToken optional in case user created account via Fran Ads
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    date_range = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.customer_id, self.date_range

# Model to get keyword themes recommendations
class GetKeywordThemesRecommendations(models.Model):                   
    refreshToken = models.CharField(max_length=500, blank=True)
    keyword_text = models.CharField(max_length=500, blank=True)
    country_code = models.CharField(max_length=500)
    language_code = models.CharField(max_length=500)
    customer_id = models.CharField(max_length=500, blank=True)
    final_url = models.CharField(max_length=500, blank=True)
    business_name = models.CharField(max_length=500, blank=True)
    business_location_id = models.CharField(max_length=500, blank=True)
    geo_target_names = models.TextField(blank=True)



    def __str__(self): 
        return (
            self.refreshToken, 
            self.keyword_text, 
            self.country_code, 
            self.language_code,
            self.customer_id,
            self.final_url,
            self.business_name,
            self.business_location_id,
            self.geo_target_names,
            )

# Model to store the keyword themes recommendations
class KeywordThemesRecommendations(models.Model):                   
    resource_name = models.CharField(max_length=500)
    display_name = models.CharField(max_length=500)

    def __str__(self): 
        return self.resource_name

# Model to get geo location recommendations
class LocationRecommendations(models.Model):                   
    refreshToken = models.CharField(max_length=500, blank=True)
    language_code = models.CharField(max_length=500)
    country_code = models.CharField(max_length=500)
    location = models.CharField(max_length=500)

    def __str__(self): 
        return (
            self.refreshToken, 
            self.location, 
            self.country_code, 
            self.language_code
            )

# Model to create Google Ads account
class GoogleAdsAccountCreation(models.Model):  
    '''make the refresh token optional so if there is no value
    it means we are going to use the app's refresh token because
    user hasn't authenticated with an existing Google Ads account'''                 
    refreshToken = models.CharField(max_length=500, blank=True)
    mytoken = models.CharField(max_length=500, blank=True)
    account_name = models.CharField(max_length=500)
    currency = models.CharField(max_length=10)
    time_zone = models.CharField(max_length=100)
    email_address = models.CharField(max_length=500)

    def __str__(self): 
        return (
            self.refreshToken, 
            self.mytoken, 
            self.time_zone, 
            self.currency, 
            self.account_name, 
            self.email_address
            )

# Model for the customer id of the newly created Google Ads account
# for users who had zero accounts created before
class NewAccountCustomerID(models.Model):                   
    mytoken = models.CharField(max_length=500)
    customer_id = models.CharField(max_length=500)

    def __str__(self): 
        return self.customer_id

# Model to get budget recommendations
# and ad creative recommendations (headlines and descriptions)
# because input is the same so simplifying models
class GetBudgetRecommendations(models.Model):                   
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    display_name = models.TextField()
    language_code = models.CharField(max_length=500)
    country_code = models.CharField(max_length=500)
    landing_page = models.CharField(max_length=500)
    geo_target_names = models.TextField()
    business_location_id = models.CharField(max_length=500, blank=True)
    business_name = models.CharField(max_length=500, blank=True)


    def __str__(self): 
        return (
            self.refreshToken, 
            self.customer_id, 
            self.display_name, 
            self.language_code, 
            self.country_code, 
            self.landing_page, 
            self.geo_target_names,
            self.business_location_id,
            self.business_name,
            )

# Model to create smart campaign
class CreateSmartCampaign(models.Model):                   
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    display_name = models.TextField()
    language_code = models.CharField(max_length=500)
    country_code = models.CharField(max_length=500)
    landing_page = models.CharField(max_length=500)
    geo_target_names = models.TextField()
    selected_budget = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=500)
    business_name = models.CharField(max_length=500)
    business_location_id = models.CharField(max_length=500, blank=True)
    headline_1_user = models.CharField(max_length=500)
    headline_2_user = models.CharField(max_length=500)
    headline_3_user = models.CharField(max_length=500)
    desc_1_user = models.CharField(max_length=500)
    desc_2_user = models.CharField(max_length=500)
    campaign_name = models.CharField(max_length=500)



    def __str__(self): 
        return (
            self.refreshToken, self.customer_id, self.display_name, 
            self.language_code, self.country_code, self.landing_page, 
            self.geo_target_names, self.selected_budget, self.phone_number,
            self.business_name, self.business_location_id, 
            self.headline_1_user, self.headline_2_user,
            self.headline_3_user, self.desc_1_user, self.desc_2_user, 
            self.campaign_name
            )

# Model to store frontend data to get campaign settings
class CampaignSettings(models.Model):                   
    # we make the refreshToken optional in case user created account via Fran Ads
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    campaign_id = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.customer_id, self.campaign_id

# Model to store frontend data to change campaign name
class CampaignName(models.Model):                   
    # we make the refreshToken optional in case user created account via Fran Ads
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    campaign_id = models.CharField(max_length=500)
    campaign_name = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.customer_id, self.campaign_id, self.campaign_name

# Model to edit campaign budget
class EditCampaignBudget(models.Model):                   
    # we make the refreshToken optional in case user created account via Fran Ads
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    campaign_id = models.CharField(max_length=500)
    new_budget = models.CharField(max_length=500)
    budget_id = models.CharField(max_length=500)

    def __str__(self): 
        return (
            self.refreshToken, 
            self.customer_id, 
            self.campaign_id, 
            self.new_budget, 
            self.budget_id
            )

# Model to get search terms report
class SearchTermsReport(models.Model):                   
    # we make the refreshToken optional in case user created account via Fran Ads
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    campaign_id = models.CharField(max_length=500)
    date_range = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.customer_id, self.campaign_id, self.date_range

# Model to edit ad creative of Smart Campaign
# (headlines and descriptions)
class EditAdCreative(models.Model):                   
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    campaign_id = models.CharField(max_length=500)
    new_headline_1 = models.CharField(max_length=30, blank=True)
    new_headline_2 = models.CharField(max_length=30, blank=True)
    new_headline_3 = models.CharField(max_length=30, blank=True)
    new_desc_1 = models.CharField(max_length=90, blank=True)
    new_desc_2 = models.CharField(max_length=90, blank=True)


    def __str__(self): 
        return (
            self.refreshToken, 
            self.customer_id, 
            self.new_headline_1, 
            self.new_headline_2, 
            self.new_headline_3, 
            self.new_desc_1,
            self.new_desc_2,
            )

# Model to edit keyword themes
class EditKeywordThemes(models.Model):                   
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    campaign_id = models.CharField(max_length=500)
    display_name = models.TextField()

    def __str__(self): 
        return (
            self.refreshToken, 
            self.customer_id, 
            self.campaign_id, 
            self.display_name, 
            )

# Model to edit campaign geo target
class EditGeoTargets(models.Model):                   
    # we make the refreshToken optional in case user created account via Fran Ads
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    campaign_id = models.CharField(max_length=500)
    new_geo_target_names = models.TextField()
    country_code = models.CharField(max_length=500)
    language_code = models.CharField(max_length=500)

    def __str__(self): 
        return (
            self.refreshToken, 
            self.customer_id, 
            self.campaign_id, 
            self.new_geo_target_names, 
            self.country_code,
            self.language_code,
            )