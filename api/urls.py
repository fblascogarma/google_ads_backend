from django.contrib.auth.models import User
from django.urls import path, include
from .views import ArticleViewSet, UserViewSet, AdWordsCredentialsViewSet, authenticate, callback, list_ads_accounts, search_token, get_campaigns, get_keyword_themes_recommendations, get_location_recommendations, create_google_ads_account
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
]