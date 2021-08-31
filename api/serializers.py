from rest_framework import serializers
from .models import Article, AdWordsCredentials, AntiForgeryToken, RefreshToken, MyToken, CustomerID, Reporting, KeywordThemesRecommendations, LocationRecommendations, GoogleAdsAccountCreation, NewAccountCustomerID
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
        fields = ['refreshToken', 'customer_id', 'date_range']

# Serializer for keyword themes recommendations
class KeywordThemesRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordThemesRecommendations
        fields = ['refreshToken', 'keyword_text', 'country_code', 'language_code']

# Serializer for location recommendations
class LocationRecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationRecommendations
        fields = ['refreshToken', 'location', 'country_code', 'language_code']

# Serializer for Google Ads account creation
class GoogleAdsAccountCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleAdsAccountCreation
        fields = ['refreshToken', 'mytoken', 'account_name', 'currency', 'time_zone', 'email_address']

# Serializer for the customer id of the Google Ads account created
class NewAccountCustomerIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewAccountCustomerID
        fields = ['mytoken', 'customer_id']