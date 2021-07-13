from django.contrib.auth.models import User
from django.urls import path, include
from .views import ArticleViewSet, UserViewSet, AdWordsCredentialsViewSet, authenticate, callback, list_ads_accounts, search_token
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
]