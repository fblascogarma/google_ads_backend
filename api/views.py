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

from contextlib import nullcontext
from json.decoder import JSONDecoder
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Article, AdWordsCredentials, RefreshToken, NewAccountCustomerID
from .serializers import (
    ArticleSerializer, 
    UserSerializer, 
    AdWordsCredentialsSerializer, 
    AntiForgeryTokenSerializer, 
    RefreshTokenSerializer, 
    MyTokenSerializer, ReportingSerializer, 
    GetKeywordThemesRecommendationsSerializer, 
    LocationRecommendationsSerializer, 
    GoogleAdsAccountCreationSerializer, 
    NewAccountCustomerIDSerializer, 
    GetBudgetRecommendationsSerializer, 
    CreateSmartCampaignSerializer, 
    CampaignSettingsSerializer,
    CampaignNameSerializer,
    EditCampaignBudgetSerializer,
    SearchTermsReportSerializer,
    EditAdCreativeSerializer,
    EditKeywordThemesSerializer,
    EditGeoTargetsSerializer,
    EditAdScheduleSerializer,
    LinkToManagerSerializer
    )
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers, status
import os

from .authenticate import connect, get_token
from .get_user_credentials import get_refresh_token
from .list_accessible_accounts import list_accounts
from .get_campaigns import campaign_info
from .keyword_themes import get_keyword_themes_suggestions
from .geo_location import get_geo_location_recommendations
from .create_customer import create_client_customer
from .budget import get_budget_recommendation
from .ad_recommendation import get_ad_recommendation
from .create_smart_campaign import create_smart
from .get_billing_info import billing_info
from .edit_sc import (
    delete_sc, sc_settings, enable_sc, 
    pause_sc, delete_sc, edit_name_sc,
    edit_budget, edit_ad, edit_keyword_themes,
    edit_geo_targets, edit_ad_schedule
    )
from .get_search_terms_report import search_terms_report
from .get_gmb import business_profile
from .link_client_to_manager import link_to_manager
from .negative_keywords import (
    get_negative_keywords,
    edit_negative_keywords
    )


# Create your views here.
class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, )

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# AdWords credentials
class AdWordsCredentialsViewSet(viewsets.ModelViewSet):
    queryset = AdWordsCredentials.objects.all()
    serializer_class = AdWordsCredentialsSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, )

class RefreshTokenViewSet(viewsets.ModelViewSet):
    queryset = RefreshToken.objects.all()
    serializer_class = RefreshTokenSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication, )

# Get the authorization URL so user can give consent.
# API endpoint 'api/connect/'
@api_view(['GET'])
def authenticate(request):
    if request.method == 'GET':

        # get the url to redirect the user so they can authenticate and authorize your app
        authorization_url = connect()[0]


        passthrough_val = connect()[1]
        
        response = HttpResponse(authorization_url)
        response.headers['url'] = authorization_url
        response.headers['passthrough_val'] = passthrough_val

        # return the authorization_url that will be used on the FE to redirect user
        # and user will authenticate themselves and authorize your app permissions
        return response

# Callback to get the refresh token and save it to our backend.
# API endpoint 'api/get-token/'
@api_view(['POST'])
def callback(request):
    if request.method == 'POST':
        serializer = AntiForgeryTokenSerializer(data=request.data)
        if serializer.is_valid():
            # save the data into the AntiForgeryToken model
            serializer.save()
            # get the access code
            google_access_code = serializer['google_access_code'].value
        
            # get the mytoken
            mytoken = serializer['mytoken'].value

            # call the function get_token from the authenticate.py file
            refresh_token = get_token(google_access_code)
            print("refresh_token after using the access token:")
            print(refresh_token)
            print("refresh_token data type:")
            print(type(refresh_token))

            # need to save the refresh token in my RefreshToken model
            serializer_credentials = RefreshTokenSerializer(data={
                'mytoken': mytoken, 
                'refreshToken': refresh_token
                })
        
            if serializer_credentials.is_valid():
                print('serializer valid so saving refresh token to RefreshToken model')
                serializer_credentials.save()
            if not serializer_credentials.is_valid():
                print('serializer is not valid and refresh token was not saved')

            user_data = {
                    'refresh_token': 1,
                    'customer_id': 0
                }

            # send to the frontend that user has a refresh token
            return JsonResponse(user_data, safe=False)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get list of accounts associated with the Google account the user used to authenticate.
# This view is only available to users who linked existing account.
# API endpoint 'api/get-accounts/'
@api_view(['POST'])
def list_ads_accounts(request):
    if request.method == 'POST':
        serializer = MyTokenSerializer(data=request.data)
        if serializer.is_valid():
            print('serializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value
            # get the refresh token
            refresh_token = get_refresh_token(mytoken)

            # call the function to get the list of accounts
            if refresh_token is not None:
                list_of_accounts = list_accounts(refresh_token)

            # response = HttpResponse(list_of_accounts)
            response = JsonResponse(list_of_accounts, safe=False)
           
            return response
        return Response(data="bad request")


# Lookup for the refresh token when user signs in.
# API endpoint 'api/lookup-refreshtoken/'
@api_view(['POST'])
def search_token(request):
    if request.method == 'POST':
        serializer = MyTokenSerializer(data=request.data)
        if serializer.is_valid():
            print('MyTokenSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            # get the refresh token associated with that token.
            # if there is only one mytoken with that value in the database
            # first try this
            try:
                print('trying to get refresh token...')
                refresh_token = RefreshToken.objects.get(mytoken=mytoken)
                print('got this refresh_token:')
                print(refresh_token)
                user_data = {
                    'refresh_token': 1,
                    'customer_id': 0
                }

                # send to the frontend that user has a refresh token
                return JsonResponse(user_data, safe=False)

            # if there are more than one mytoken with that value in the database
            # you will get the MultipleObjectsReturned error
            # so then try this
            except RefreshToken.MultipleObjectsReturned:
                print('more than one mytoken found so getting most recent one')
                query_set = RefreshToken.objects.filter(mytoken=mytoken)
                # get the last one which is the most recent one
                most_recent = len(query_set) - 1
                print(most_recent)
                query_set = query_set.values()[most_recent]
        
                refresh_token = query_set['refreshToken']
                print("refresh_token:")
                print(refresh_token)
                user_data = {
                    'refresh_token': 1,
                    'customer_id': 0
                }

                # send to the frontend that user has a refresh token
                return JsonResponse(user_data, safe=False)
            
            # if user has no refresh token,
            # check if user has a customer_id from Google Ads
            # and send it to the frontend
            except RefreshToken.DoesNotExist:
                print('user has no refresh token')
                try:
                    print('trying to get customer id if exists...')
                    customer_id = NewAccountCustomerID.objects.get(mytoken=mytoken).customer_id
                    print("customer_id:")
                    print(customer_id)
                    print('customer_id data type:')
                    print(type(customer_id))

                    # send to the frontend that user has a Google Ads account
                    user_data = {
                        'refresh_token': 0,
                        'customer_id': customer_id
                    }

                    return JsonResponse(user_data, safe=False)

                # Fran Ads is designed so users that don't have a Google Ads account
                # can create one in the app, but just one. Therefore, the error
                # below will never happen as each user will only have one Ads account.
                # However, we left it just in case you want to change that logic.
                except NewAccountCustomerID.MultipleObjectsReturned:
                    print('more than one customer id found so getting most recen one')
                    query_set2 = NewAccountCustomerID.objects.filter(mytoken=mytoken)
                    most_recent2 = len(query_set2) - 1
                    query_set2 = query_set2.values()[most_recent2]

                    customer_id = query_set2['customer_id']
                    # send to the frontend that user has a Google Ads account
                    user_data = {
                        'refresh_token': 0,
                        'customer_id': customer_id
                    }

                    return JsonResponse(user_data, safe=False)

                # new app user that doesn't have refresh token, nor customer id
                except NewAccountCustomerID.DoesNotExist:
                    print('no refresh token nor customer id found')
                    user_data = {
                        'refresh_token': 0,
                        'customer_id': 0
                    }
                    return JsonResponse(user_data, safe=False)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
# Get info of the campaigns associated with the customer_id from the request.
# API endpoint 'api/get-campaigns/'
@api_view(['POST'])
def get_campaigns(request):
    if request.method == 'POST':
        serializer = ReportingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print('ReportingSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')
            
            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the date range
            date_range = serializer['date_range'].value
            # print(date_range)

            # call the function to get the campaigns
            get_campaign_info = campaign_info(
                refresh_token, 
                customer_id, 
                date_range,
                use_login_id)
            print(get_campaign_info)

            response = JsonResponse(get_campaign_info, safe=False)
           
            return response
        return Response(data="bad request")


# Get keyword themes recommendations
# API endpoint 'api/keywords-recommendations/'
@api_view(['POST'])
def get_keyword_themes_recommendations(request):
    if request.method == 'POST':
        serializer = GetKeywordThemesRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            print('GetKeywordThemesRecommendationsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the keyword text
            keyword_text = serializer['keyword_text'].value

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # get the customer_id
            customer_id = serializer['customer_id'].value

            # get the final_url
            final_url = serializer['final_url'].value

            # get the business_name
            business_name = serializer['business_name'].value

            # get the business_location_id
            business_location_id = serializer['business_location_id'].value

            # get the geo_target_names
            geo_target_names = serializer['geo_target_names'].value
            # transform string into a list
            geo_target_names = geo_target_names.replace('"','').replace('[','').replace(']','').split(",")

            # call the function to get the recommendations
            get_recommendations = get_keyword_themes_suggestions(
                refresh_token, 
                keyword_text, 
                country_code, 
                language_code,
                customer_id,
                final_url,
                business_name,
                business_location_id,
                geo_target_names,
                use_login_id
                )
            print(get_recommendations)
            
            response = JsonResponse(get_recommendations, safe=False)
           
            return response
        return Response(data="bad request")

# Get location recommendations
# API endpoint 'api/location-recommendations/'
@api_view(['POST'])
def get_location_recommendations(request):
    if request.method == 'POST':
        serializer = LocationRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            print('LocationRecommendationsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)
            
            # get the location
            location = serializer['location'].value

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # call the function to get the recommendations
            get_recommendations = get_geo_location_recommendations(
                refresh_token, 
                customer_id,
                location, 
                country_code, 
                language_code,
                use_login_id)

            response = JsonResponse(get_recommendations, safe=False)
           
            return response
        return Response(data="bad request")

# Create Google Ads account
# API endpoint 'api/create-account/'
@api_view(['POST'])
def create_google_ads_account(request):
    if request.method == 'POST':
        serializer = GoogleAdsAccountCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print('GoogleAdsAccountCreationSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                # use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                # use_login_id = False
                print('found a refresh token')

            print("refresh_token:")
            print(refresh_token)

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the account_name
            account_name = serializer['account_name'].value

            # get the currency
            currency = serializer['currency'].value

            # get the time_zone
            time_zone = serializer['time_zone'].value

            # get the email_address
            email_address = serializer['email_address'].value

            # call the function to create account
            customer_id = create_client_customer(
                refresh_token,
                customer_id, 
                account_name, 
                currency, 
                time_zone, 
                email_address)

            # store the customer id created and the mytoken value for future reference
            if serializer['refreshToken'].value == '':
                cust_id_data = {
                    'mytoken': mytoken,
                    'customer_id': customer_id
                }
                serializer2 = NewAccountCustomerIDSerializer(data=cust_id_data)
                if serializer2.is_valid():
                    serializer2.save()


            response = JsonResponse(customer_id, safe=False)
           
            return response
        
        else:
            print(serializer.errors)
        return Response(data="bad request")

# Get budget recommendations
# API endpoint 'api/get-budget-recommendation/'
@api_view(['POST'])
def get_budget(request):
    if request.method == 'POST':
        serializer = GetBudgetRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            print('GetBudgetRecommendationsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value

            # get the display_name
            display_name = serializer['display_name'].value
            # transform string into a list
            display_name = display_name.replace('"','').replace('[','').replace(']','').split(",")

            # get the geo_target_names
            geo_target_names = serializer['geo_target_names'].value
            # transform string into a list
            geo_target_names = geo_target_names.replace('"','').replace('[','').replace(']','').split(",")

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # get the landing_page
            landing_page = serializer['landing_page'].value

            # get the business_name
            business_name = serializer['business_name'].value

            # get the business_location_id
            business_location_id = serializer['business_location_id'].value

            # call the function to get the recommendations
            get_recommendations = get_budget_recommendation(
                refresh_token, 
                customer_id, 
                display_name, 
                landing_page, 
                geo_target_names, 
                language_code, 
                country_code,
                business_location_id,
                business_name,
                use_login_id)
            print(get_recommendations)
            
            response = JsonResponse(get_recommendations, safe=False)
           
            return response
        return Response(data="bad request")

# Get ad creatives recommendations
# API endpoint 'api/get-ad-recommendation/'
@api_view(['POST'])
def get_ad_creatives(request):
    if request.method == 'POST':
        serializer = GetBudgetRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            print('GetBudgetRecommendationsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value

            # get the display_name
            display_name = serializer['display_name'].value
            # transform string into a list
            display_name = display_name.replace('"','').replace('[','').replace(']','').split(",")

            # get the geo_target_names
            geo_target_names = serializer['geo_target_names'].value
            # transform string into a list
            geo_target_names = geo_target_names.replace('"','').replace('[','').replace(']','').split(",")

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # get the landing_page
            landing_page = serializer['landing_page'].value

            # get the business_name
            business_name = serializer['business_name'].value

            # get the business_location_id
            business_location_id = serializer['business_location_id'].value

            # call the function to get the recommendations
            get_recommendations = get_ad_recommendation(
                refresh_token, 
                customer_id, 
                display_name, 
                landing_page, 
                geo_target_names, 
                language_code, 
                country_code,
                business_location_id,
                business_name,
                use_login_id)
            
            print('get_recommendations:')
            print(get_recommendations)
            
            response = JsonResponse(get_recommendations, safe=False)
           
            return response
        return Response(data="bad request")

# Create Smart Campaign
# API endpoint 'api/create-campaign/'
@api_view(['POST'])
def create_smart_campaign(request):
    if request.method == 'POST':
        serializer = CreateSmartCampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print('CreateSmartCampaignSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value

            # get the display_name
            display_name = serializer['display_name'].value
            # transform string into a list
            display_name = display_name.replace('"','').replace('[','').replace(']','').split(",")

            # get the geo_target_names
            geo_target_names = serializer['geo_target_names'].value
            # transform string into a list
            geo_target_names = geo_target_names.replace('"','').replace('[','').replace(']','').split(",")

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # get the landing_page
            landing_page = serializer['landing_page'].value

            # get the selected_budget
            selected_budget = serializer['selected_budget'].value

            # get the phone_number
            phone_number = serializer['phone_number'].value

            # get the business_name
            business_name = serializer['business_name'].value

            # get the business_location_id
            business_location_id = serializer['business_location_id'].value
            print("business_location_id:")
            print(business_location_id)

            # get the headline_1_user
            headline_1_user = serializer['headline_1_user'].value

            # get the headline_2_user
            headline_2_user = serializer['headline_2_user'].value

            # get the headline_3_user
            headline_3_user = serializer['headline_3_user'].value

            # get the desc_1_user
            desc_1_user = serializer['desc_1_user'].value

            # get the desc_2_user
            desc_2_user = serializer['desc_2_user'].value

            # get the campaign_name
            campaign_name = serializer['campaign_name'].value

            # call the function to get the recommendations
            smart_campaign = create_smart(
                refresh_token, customer_id, display_name, geo_target_names,
                language_code, country_code, selected_budget,
                phone_number, landing_page, 
                business_name, business_location_id,
                headline_1_user, headline_2_user, headline_3_user,
                desc_1_user, desc_2_user, campaign_name,
                use_login_id)
            print(smart_campaign)
            
            response = JsonResponse(smart_campaign, safe=False)
           
            return response
        return Response(data="bad request")

# Get billing info of the customer_id from the request
@api_view(['POST'])
def get_billing(request):
    if request.method == 'POST':
        serializer = ReportingSerializer(data=request.data)
        if serializer.is_valid():
            print('ReportingSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            
            if user_credential is None:
                print('using the app refresh token')
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                print('using user refresh token...')
                refresh_token = user_credential
                use_login_id = False

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # call the function to get the campaigns
            get_billing_info = billing_info(
                refresh_token, 
                customer_id,
                use_login_id)
            print(get_billing_info)

            response = JsonResponse(get_billing_info, safe=False)
           
            return response
        return Response(data="bad request for billing")

# Get campaign settings for the campaign_id from the request
# API endpoint 'api/get-campaign-settings/'
@api_view(['POST'])
def get_sc_settings(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            print('CampaignSettingsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # call the function to get the campaign settings
            sc_settings_info = sc_settings(
                refresh_token, 
                customer_id, 
                campaign_id,
                use_login_id)
            print(sc_settings_info)

            response = JsonResponse(sc_settings_info, safe=False)
           
            return response
        return Response(data="bad request")

# Enable a Smart Campaign
# API endpoint 'api/sc-settings/enable/'
@api_view(['POST'])
def enable_campaign(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            print('CampaignSettingsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # call the function to enable the smart campaign
            new_status = enable_sc(
                refresh_token, 
                customer_id, 
                campaign_id,
                use_login_id)
            print(new_status)

            response = JsonResponse(new_status, safe=False)
           
            return response
        return Response(data="bad request")

# Pause a Smart Campaign
# API endpoint 'api/sc-settings/pause/'
@api_view(['POST'])
def pause_campaign(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            print('CampaignSettingsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # call the function to pause the smart campaign
            new_status = pause_sc(
                refresh_token, 
                customer_id, 
                campaign_id,
                use_login_id)
            print(new_status)

            response = JsonResponse(new_status, safe=False)
           
            return response
        return Response(data="bad request")

# Delete a Smart Campaign
# API endpoint 'api/sc-settings/delete/'
@api_view(['POST'])
def delete_campaign(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            print('CampaignSettingsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # call the function to delete the smart campaign
            new_status = delete_sc(
                refresh_token, 
                customer_id, 
                campaign_id,
                use_login_id)
            print(new_status)

            response = JsonResponse(new_status, safe=False)
           
            return response
        return Response(data="bad request")

# Edit name of Smart Campaign
# API endpoint 'api/sc-settings/edit-name/'
@api_view(['POST'])
def edit_campaign_name(request):
    if request.method == 'POST':
        serializer = CampaignNameSerializer(data=request.data)
        if serializer.is_valid():
            print('CampaignSettingsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # get the campaign_name
            new_campaign_name = serializer['campaign_name'].value

            # call the function to edit the smart campaign name
            new_name = edit_name_sc(
                refresh_token, 
                customer_id, 
                campaign_id, 
                new_campaign_name,
                use_login_id
                )
            print(new_name)

            response = JsonResponse(new_name, safe=False)
           
            return response
        return Response(data="bad request")

# Edit campaign budget.
# API endpoint 'api/sc-settings/edit-budget/'
@api_view(['POST'])
def edit_campaign_budget(request):
    if request.method == 'POST':
        serializer = EditCampaignBudgetSerializer(data=request.data)
        if serializer.is_valid():
            print('EditCampaignBudgetSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # get the new_budget
            new_budget = serializer['new_budget'].value
            new_budget = int(new_budget)

            # get the budget_id
            budget_id = serializer['budget_id'].value

            # call the function to edit the smart campaign budget
            new_campaign_budget = edit_budget(
                refresh_token, 
                customer_id, 
                campaign_id, 
                new_budget,
                budget_id,
                use_login_id
                )
            print(new_campaign_budget)

            response = JsonResponse(new_campaign_budget, safe=False)
           
            return response
        return Response(data="bad request")

# Get search terms report for smart campaign
# API endpoint 'api/get-search-terms-report/'
@api_view(['POST'])
def get_search_terms_report(request):
    if request.method == 'POST':
        serializer = SearchTermsReportSerializer(data=request.data)
        if serializer.is_valid():
            print('SearchTermsReportSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # get the date range
            date_range = serializer['date_range'].value
            # print(date_range)

            # call the function to get the search terms report
            get_search_terms_info = search_terms_report(
                refresh_token, 
                customer_id, 
                campaign_id, 
                date_range,
                use_login_id)
            print(get_search_terms_info)

            response = JsonResponse(get_search_terms_info, safe=False)
           
            return response
        return Response(data="bad request")

# Edit ad creative of Smart Campaign
# API endpoint 'api/sc-settings/edit-ad-creative/'
@api_view(['POST'])
def edit_ad_creative(request):
    if request.method == 'POST':
        serializer = EditAdCreativeSerializer(data=request.data)
        if serializer.is_valid():
            print('EditAdCreativeSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            
            # get the creatives for the modified headlines and desc
            new_headline_1 = serializer['new_headline_1'].value
            new_headline_2 = serializer['new_headline_2'].value
            new_headline_3 = serializer['new_headline_3'].value
            new_desc_1 = serializer['new_desc_1'].value
            new_desc_2 = serializer['new_desc_2'].value

            # call the function to edit the smart campaign budget
            new_ad_creative = edit_ad(
                refresh_token, 
                customer_id, 
                campaign_id, 
                new_headline_1, 
                new_headline_2, 
                new_headline_3, 
                new_desc_1,
                new_desc_2,
                use_login_id
                )
            print(new_ad_creative)

            response = JsonResponse(new_ad_creative, safe=False)
           
            return response
        return Response(data="bad request")

# Edit keyword themes of smart campaign
# API endpoint 'api/sc-settings/edit-keywords/'
@api_view(['POST'])
def edit_keywords(request):
    if request.method == 'POST':
        serializer = EditKeywordThemesSerializer(data=request.data)
        if serializer.is_valid():
            print('EditKeywordThemesSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # get the display_name
            display_name = serializer['display_name'].value
            # transform string into a list
            display_name = display_name.replace('"','').replace('[','').replace(']','').split(",")

            # call the function to edit keyword themes
            updated_keywords = edit_keyword_themes(
                refresh_token, 
                customer_id, 
                campaign_id, 
                display_name,
                use_login_id
                )
            print("updated_keywords:")
            print(updated_keywords)

            response = JsonResponse(updated_keywords, safe=False)
           
            return response
        return Response(data="bad request")

# Get Business Information from Google My Business
# API endpoint 'api/get-business-info/'
@api_view(['POST'])
def get_business_info(request):
    if request.method == 'POST':
        serializer = MyTokenSerializer(data=request.data)
        if serializer.is_valid():
            # get the refresh token
            print('MyTokenSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                # In this case we do not want to use the app refresh token
                # because if we do we will get the business info of our
                # Manager account. This behavior is different than all other functions.
                # GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                # refresh_token = GOOGLE_REFRESH_TOKEN
                # use_login_id = True
                # print('no refresh token so using the app')
                print('no refresh token so do not get data')
            else: 
                refresh_token = user_credential
                # use_login_id = False
                print('found a refresh token')

                # call the function to get the business info
                gmb_info = business_profile(refresh_token)

                response = JsonResponse(gmb_info, safe=False)
            
                return response
   
        return Response(data="bad request")

# Edit geo target locations of smart campaign
# API endpoint 'api/sc-settings/edit-geo-targets/'
@api_view(['POST'])
def edit_geo_target(request):
    if request.method == 'POST':
        serializer = EditGeoTargetsSerializer(data=request.data)
        if serializer.is_valid():
            print('EditGeoTargetsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # get the new_geo_target_names
            new_geo_target_names = serializer['new_geo_target_names'].value
            # transform string into a list
            new_geo_target_names = new_geo_target_names.replace('"','').replace('[','').replace(']','').split(",")

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            print(refresh_token)
            print(customer_id)
            print(campaign_id)
            print(new_geo_target_names)
            print(language_code)
            print(country_code)

            # call the function to edit geo targets
            updated_geo_targets = edit_geo_targets(
                refresh_token, 
                customer_id, 
                campaign_id, 
                new_geo_target_names,
                language_code,
                country_code,
                use_login_id
                )
            print("updated_geo_targets:")
            print(updated_geo_targets)

            response = JsonResponse(updated_geo_targets, safe=False)
           
            return response
        return Response(data="bad request")

# Edit smart campaign ad schedule
# API endpoint 'api/sc-settings/edit-ad-schedule/'
@api_view(['POST'])
def edit_ad_schedule_campaign(request):
    if request.method == 'POST':
        serializer = EditAdScheduleSerializer(data=request.data)
        if serializer.is_valid():
            print('EditAdScheduleSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # get the new ad schedules
            if serializer['mon_start'].value is None:
                mon_start = -1
            else:
                mon_start = int(serializer['mon_start'].value)
            if serializer['mon_end'].value is None:
                mon_end = -1
            else:
                mon_end = int(serializer['mon_end'].value)
            if serializer['tue_start'].value is None:
                tue_start = -1
            else:
                tue_start = int(serializer['tue_start'].value)
            if serializer['tue_end'].value is None:
                tue_end = -1
            else:
                tue_end = int(serializer['tue_end'].value)
            if serializer['wed_start'].value is None:
                wed_start = -1
            else:
                wed_start = int(serializer['wed_start'].value)
            if serializer['wed_end'].value is None:
                wed_end = -1
            else:
                wed_end = int(serializer['wed_end'].value)
            if serializer['thu_start'].value is None:
                thu_start = -1
            else:
                thu_start = int(serializer['thu_start'].value)
            if serializer['thu_end'].value is None:
                thu_end = -1
            else:
                thu_end = int(serializer['thu_end'].value)
            if serializer['fri_start'].value is None:
                fri_start = -1
            else:
                fri_start = int(serializer['fri_start'].value)
            if serializer['fri_end'].value is None:
                fri_end = -1
            else:
                fri_end = int(serializer['fri_end'].value)
            if serializer['sat_start'].value is None:
                sat_start = -1
            else:
                sat_start = int(serializer['sat_start'].value)
            if serializer['sat_end'].value is None:
                sat_end = -1
            else:
                sat_end = int(serializer['sat_end'].value)
            if serializer['sun_start'].value is None:
                sun_start = -1
            else:
                sun_start = int(serializer['sun_start'].value)
            if serializer['sun_end'].value is None:
                sun_end = -1
            else:
                sun_end = int(serializer['sun_end'].value)

            # call the function to edit ad schedule
            updated_ad_schedule = edit_ad_schedule(
                refresh_token, customer_id, campaign_id, 
                mon_start, mon_end, tue_start, tue_end,
                wed_start, wed_end, thu_start, thu_end,
                fri_start, fri_end, sat_start, sat_end,
                sun_start, sun_end, use_login_id
                )
            print("updated_ad_schedule:")
            print(updated_ad_schedule)

            response = JsonResponse(updated_ad_schedule, safe=False)
           
            return response
        return Response(data="bad request")

# Link client account to Manager account for existing accounts
@api_view(['POST'])
def link_accounts(request):
    if request.method == 'POST':
        serializer = LinkToManagerSerializer(data=request.data)
        if serializer.is_valid():
            print('LinkToManagerSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            
            if user_credential is None:
                print('using the app refresh token')
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                print('using user refresh token...')
                refresh_token = user_credential
                use_login_id = False
            # serializer.save()
            # get the refresh token
            # refresh_token = serializer['refreshToken'].value

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # call the function to link accounts
            linked_accounts = link_to_manager(
                refresh_token,
                customer_id)

            response = JsonResponse(linked_accounts, safe=False)
           
            return response
        return Response(data="bad request")

# Get negative keyword themes for smart campaign
# API endpoint 'api/get-negative-keywords/'
@api_view(['POST'])
def get_negative_keyword_themes(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            print('CampaignSettingsSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # call the function to get the negative keyword themes
            negative_keyword_themes = get_negative_keywords(
                refresh_token, 
                customer_id, 
                campaign_id, 
                use_login_id)
            print(negative_keyword_themes)

            response = JsonResponse(negative_keyword_themes, safe=False)
           
            return response
        return Response(data="bad request")

# Edit negative keyword themes for smart campaign
# API endpoint 'api/edit-negative-keywords/'
@api_view(['POST'])
def edit_negative_keyword_themes(request):
    if request.method == 'POST':
        serializer = EditKeywordThemesSerializer(data=request.data)
        if serializer.is_valid():
            print('EditKeywordThemesSerializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            user_credential = get_refresh_token(mytoken)
            print("user_credential:")
            print(user_credential)
            
            if user_credential is None:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = user_credential
                use_login_id = False
                print('found a refresh token')

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the campaign_id
            campaign_id = serializer['campaign_id'].value
            campaign_id = str(campaign_id)

            # get the negative keywords list
            new_kt_negative_list = serializer['display_name'].value
            # transform string into a list
            new_kt_negative_list = new_kt_negative_list.replace('"','').replace('[','').replace(']','').split(",")

            # call the function to edit the negative keyword themes
            updated_negative_keyword_themes = edit_negative_keywords(
                refresh_token, 
                customer_id, 
                campaign_id, 
                new_kt_negative_list,
                use_login_id)
            print(updated_negative_keyword_themes)

            response = JsonResponse(updated_negative_keyword_themes, safe=False)
           
            return response
        return Response(data="bad request")
