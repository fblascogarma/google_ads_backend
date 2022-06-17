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

from rest_framework import serializers
from .models import (
    Article, AdWordsCredentials, AntiForgeryToken, 
    RefreshToken, MyToken, CustomerID, Reporting, 
    GetKeywordThemesRecommendations, 
    KeywordThemesRecommendations, 
    LocationRecommendations, GoogleAdsAccountCreation, 
    NewAccountCustomerID, GetBudgetRecommendations, 
    CreateSmartCampaign, CampaignSettings,
    CampaignName, EditCampaignBudget,
    SearchTermsReport, EditAdCreative,
    EditKeywordThemes, EditGeoTargets,
    EditAdSchedule, LinkToManager
    )
from django.contrib.auth.models import User
from rest_framework.authtoken.views import Token


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'title', 'description']        # fields you want to retrieve from the api

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']

        extra_kwargs = {'password':{
            'write_only': True,
            'required': True
        }}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

# Serializer for AdWords credentials
class AdWordsCredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdWordsCredentials
        fields = ['id', 'mytoken', 'google_access_code', 'refresh_token']        # fields you want to retrieve from the api


class AntiForgeryTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AntiForgeryToken
        fields = ['id', 'mytoken', 'google_access_code', 'passthrough_val'] 

# Serializer for refresh token
class RefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshToken
        fields = ['id', 'mytoken', 'refreshToken']

# Serializer for mytoken
class MyTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyToken
        fields = ['id', 'mytoken']

# Serializer for customer_id
class CustomerIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerID
        fields = ['refreshToken', 'customer_id']

# Serializer for reporting
class ReportingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporting
        fields = ['mytoken', 'refreshToken', 'customer_id', 'date_range']

# Serializer for getting keyword themes recommendations
class GetKeywordThemesRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetKeywordThemesRecommendations
        fields = [
            'mytoken',
            'refreshToken', 
            'keyword_text', 
            'country_code', 
            'language_code', 
            'customer_id',
            'final_url',
            'business_name',
            'business_location_id',
            'geo_target_names'
            ]

# Serializer to store keyword themes recommendations
class KeywordThemesRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordThemesRecommendations
        fields = ['resource_name', 'display_name']

# Serializer for location recommendations
class LocationRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationRecommendations
        fields = [
            'mytoken', 
            'refreshToken', 
            'customer_id',
            'location', 
            'country_code', 
            'language_code']

# Serializer for Google Ads account creation
class GoogleAdsAccountCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleAdsAccountCreation
        fields = [
            'refreshToken', 
            'mytoken', 
            'customer_id',
            'account_name', 
            'currency', 
            'time_zone', 
            'email_address']

# Serializer for the customer id of the Google Ads account created
class NewAccountCustomerIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewAccountCustomerID
        fields = ['mytoken', 'customer_id']

# Serializer to get budget recommendations and ad creative recomm.
class GetBudgetRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GetBudgetRecommendations
        fields = [
            'mytoken',
            'refreshToken', 
            'customer_id', 
            'display_name', 
            'language_code', 
            'country_code', 
            'landing_page', 
            'geo_target_names',
            'business_location_id',
            'business_name'
            ]

# Serializer to create smart campaign
class CreateSmartCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateSmartCampaign
        fields = [
            'mytoken', 'refreshToken', 'customer_id', 'display_name', 
            'language_code', 'country_code', 'landing_page', 'geo_target_names', 
            'selected_budget', 'phone_number', 'business_name', 'business_location_id', 
            'headline_1_user', 'headline_2_user', 'headline_3_user',
            'desc_1_user', 'desc_2_user', 'campaign_name']

# Serializer for getting campaign settings
class CampaignSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignSettings
        fields = [
            'mytoken', 'refreshToken', 'customer_id', 'campaign_id']

# Serializer for changing campaign name
class CampaignNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignName
        fields = [
            'mytoken', 'refreshToken', 'customer_id', 'campaign_id', 
            'campaign_name']

# Serializer for changing campaign budget
class EditCampaignBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditCampaignBudget
        fields = [
            'mytoken', 'refreshToken', 'customer_id', 'campaign_id', 
            'new_budget', 'budget_id']

# Serializer for search terms reporting
class SearchTermsReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchTermsReport
        fields = [
            'mytoken', 'refreshToken', 'customer_id', 
            'campaign_id', 'date_range'
            ]

# Serializer for changing campaign ad creative (headlines and descriptions)
class EditAdCreativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditAdCreative
        fields = [
            'mytoken',
            'refreshToken', 
            'customer_id', 
            'campaign_id', 
            'new_headline_1', 
            'new_headline_2', 
            'new_headline_3', 
            'new_desc_1', 
            'new_desc_2'
            ]

# Serializer for editing keywords
class EditKeywordThemesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditKeywordThemes
        fields = [
            'mytoken',
            'refreshToken', 
            'customer_id', 
            'campaign_id', 
            'display_name']

# Serializer for editing geo targets
class EditGeoTargetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditGeoTargets
        fields = [
            'mytoken',
            'refreshToken', 
            'customer_id', 
            'campaign_id', 
            'new_geo_target_names',
            'country_code',
            'language_code',
            ]

# Serializer for editing ad schedule
class EditAdScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditAdSchedule
        fields = [
            'mytoken',
            'refreshToken', 
            'customer_id', 
            'campaign_id', 
            'mon_start', 
            'mon_end', 
            'tue_start', 
            'tue_end', 
            'wed_start', 
            'wed_end', 
            'thu_start', 
            'thu_end', 
            'fri_start', 
            'fri_end', 
            'sat_start', 
            'sat_end', 
            'sun_start', 
            'sun_end', 
            ]

# Serializer for linking client account to Manager account
class LinkToManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkToManager
        fields = [
            'mytoken',
            'refreshToken', 
            'customer_id'
            ]

