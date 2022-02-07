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

from django.contrib import admin
from .models import Article, AdWordsCredentials, AntiForgeryToken, RefreshToken, MyToken, CustomerID, Reporting, GetKeywordThemesRecommendations, KeywordThemesRecommendations, LocationRecommendations, GoogleAdsAccountCreation, NewAccountCustomerID, GetBudgetRecommendations, CreateSmartCampaign

# Register your models here.
@admin.register(Article)
class ArticleModel(admin.ModelAdmin):
    list_filter = ('title', 'description')          # add your filters
    list_display = ('title', 'description')


@admin.register(AdWordsCredentials)
class AdWordsCredentialsModel(admin.ModelAdmin):
    list_filter = ('mytoken', 'refresh_token')          # add your filters
    list_display = ('mytoken', 'google_access_code', 'refresh_token')


@admin.register(AntiForgeryToken)
class AntiForgeryTokenModel(admin.ModelAdmin):
    list_filter = ('mytoken', 'google_access_code')     
    list_display = ('mytoken', 'passthrough_val', 'google_access_code')

@admin.register(RefreshToken)
class RefreshTokenModel(admin.ModelAdmin):
    list_filter = ('mytoken', 'refreshToken')          # add your filters
    list_display = ('mytoken', 'refreshToken')

@admin.register(MyToken)
class MyTokenModel(admin.ModelAdmin):
    list_filter = ['mytoken']          # add your filters
    list_display = ['mytoken']

@admin.register(CustomerID)
class CustomerIDModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'customer_id')          # add your filters
    list_display = ('refreshToken', 'customer_id')

@admin.register(Reporting)
class ReportingModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'customer_id', 'date_range')          # add your filters
    list_display = ('refreshToken', 'customer_id', 'date_range')

@admin.register(GetKeywordThemesRecommendations)
class GetKeywordThemesRecommendationsModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'keyword_text', 'country_code', 'language_code')          # add your filters
    list_display = ('refreshToken', 'keyword_text', 'country_code', 'language_code')

@admin.register(KeywordThemesRecommendations)
class KeywordThemesRecommendationsModel(admin.ModelAdmin):
    list_filter = ('resource_name', 'display_name')          # add your filters
    list_display = ('resource_name', 'display_name')

@admin.register(LocationRecommendations)
class LocationRecommendationsModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'location', 'country_code', 'language_code')          # add your filters
    list_display = ('refreshToken', 'location', 'country_code', 'language_code')

@admin.register(GoogleAdsAccountCreation)
class GoogleAdsAccountCreationModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'mytoken', 'account_name', 'currency', 'time_zone', 'email_address')          # add your filters
    list_display = ('refreshToken', 'mytoken', 'account_name', 'currency', 'time_zone', 'email_address')

@admin.register(NewAccountCustomerID)
class NewAccountCustomerIDModel(admin.ModelAdmin):
    list_filter = ('mytoken', 'customer_id')          # add your filters
    list_display = ('mytoken', 'customer_id')

@admin.register(GetBudgetRecommendations)
class GetBudgetRecommendationsModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'customer_id', 'display_name', 'language_code', 'country_code', 'landing_page', 'geo_target_names')          # add your filters
    list_display = ('refreshToken', 'customer_id', 'display_name', 'language_code', 'country_code', 'landing_page', 'geo_target_names')

@admin.register(CreateSmartCampaign)
class CreateSmartCampaignModel(admin.ModelAdmin):
    list_filter = (
        'refreshToken', 'customer_id', 'display_name', 'language_code', 'country_code', 'landing_page', 'geo_target_names', 
        'selected_budget', 'phone_number', 'business_name', 'headline_1_user', 'headline_2_user', 'headline_3_user',
        'desc_1_user', 'desc_2_user', 'campaign_name')          
    list_display = (
        'refreshToken', 'customer_id', 'display_name', 'language_code', 'country_code', 'landing_page', 'geo_target_names', 
        'selected_budget', 'phone_number', 'business_name', 'headline_1_user', 'headline_2_user', 'headline_3_user',
        'desc_1_user', 'desc_2_user', 'campaign_name')