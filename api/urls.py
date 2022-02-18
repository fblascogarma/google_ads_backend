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

from django.contrib.auth.models import User
from django.urls import path, include
from .views import (
    ArticleViewSet, 
    UserViewSet, 
    AdWordsCredentialsViewSet, 
    authenticate, 
    callback,
    delete_campaign, 
    list_ads_accounts, 
    search_token, 
    get_campaigns, 
    get_keyword_themes_recommendations, 
    get_location_recommendations, 
    create_google_ads_account, 
    get_budget, create_smart_campaign, 
    get_billing, get_sc_settings, enable_campaign,
    pause_campaign, delete_campaign,
    edit_campaign_name,
    edit_campaign_budget,
    get_search_terms_report,
    get_ad_creatives,
    edit_ad_creative,
    edit_keywords,
    get_business_info,
    edit_geo_target
    )
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='articles')
router.register('users', UserViewSet)
router.register('credentials', AdWordsCredentialsViewSet, basename='credentials')


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/connect/', authenticate),
    path('api/get-token/', callback),
    path('api/get-accounts/', list_ads_accounts),
    path('api/lookup-refreshtoken/', search_token),
    path('api/get-campaigns/', get_campaigns),
    path('api/keywords-recommendations/', get_keyword_themes_recommendations),
    path('api/location-recommendations/', get_location_recommendations),
    path('api/create-account/', create_google_ads_account),
    path('api/get-budget-recommendation/', get_budget),
    path('api/get-ad-recommendation/', get_ad_creatives),
    path('api/create-campaign/', create_smart_campaign),
    path('api/get-billing/', get_billing),
    path('api/get-campaign-settings/', get_sc_settings),
    path('api/sc-settings/enable/', enable_campaign),
    path('api/sc-settings/pause/', pause_campaign),
    path('api/sc-settings/delete/', delete_campaign),
    path('api/sc-settings/edit-name/', edit_campaign_name),
    path('api/sc-settings/edit-budget/', edit_campaign_budget),
    path('api/get-search-terms-report/', get_search_terms_report),
    path('api/sc-settings/edit-ad-creative/', edit_ad_creative),
    path('api/sc-settings/edit-keywords/', edit_keywords),
    path('api/get-business-info/', get_business_info),
    path('api/sc-settings/edit-geo-targets/', edit_geo_target),
]