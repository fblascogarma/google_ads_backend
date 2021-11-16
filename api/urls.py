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
    pause_campaign, delete_campaign
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
    path('api/create-campaign/', create_smart_campaign),
    path('api/get-billing/', get_billing),
    path('api/get-campaign-settings/', get_sc_settings),
    path('api/sc-settings/enable/', enable_campaign),
    path('api/sc-settings/pause/', pause_campaign),
    path('api/sc-settings/delete/', delete_campaign),
]