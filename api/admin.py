from django.contrib import admin
from .models import Article, AdWordsCredentials, AntiForgeryToken, RefreshToken, MyToken, CustomerID, Reporting, KeywordThemesRecommendations, LocationRecommendations

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

@admin.register(KeywordThemesRecommendations)
class KeywordThemesRecommendationsModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'keyword_text', 'country_code', 'language_code')          # add your filters
    list_display = ('refreshToken', 'keyword_text', 'country_code', 'language_code')

@admin.register(LocationRecommendations)
class LocationRecommendationsModel(admin.ModelAdmin):
    list_filter = ('refreshToken', 'location', 'country_code', 'language_code')          # add your filters
    list_display = ('refreshToken', 'location', 'country_code', 'language_code')