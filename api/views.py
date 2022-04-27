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
    EditGeoTargetsSerializer
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
    edit_geo_targets
    )
from .get_search_terms_report import search_terms_report
from .get_gmb import business_profile


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

# Get the authorization URL so user can give consent
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

# Callback to get the refresh token and save it to our backend
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

            # need to save the refresh token in my AdWordsCredentials model
            serializer_credentials = AdWordsCredentialsSerializer(data={
                'mytoken': mytoken, 
                'google_access_code': google_access_code, 
                'refresh_token': refresh_token
                })
            if serializer_credentials.is_valid():
                serializer_credentials.save()

            # send the refresh token as the response
            response = HttpResponse(refresh_token)
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get list of accounts associated with the Google account the user used to authenticate
@api_view(['POST'])
def list_ads_accounts(request):
    if request.method == 'POST':
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # get the refresh token
            refresh_token = serializer['refreshToken'].value

            # call the function to get the list of accounts
            list_of_accounts = list_accounts(refresh_token)

            # response = HttpResponse(list_of_accounts)
            response = JsonResponse(list_of_accounts, safe=False)
           
            return response
        return Response(data="bad request")

# Lookup for the refresh token when user signs in
@api_view(['POST'])
def search_token(request):
    if request.method == 'POST':
        serializer = MyTokenSerializer(data=request.data)
        if serializer.is_valid():
            print('serializer is valid')
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            # get the refresh token associated with that token.
            # if there is only one mytoken with that value in the database
            # first try this
            try:
                print('trying to get refresh token...')
                refresh_token = RefreshToken.objects.get(mytoken=mytoken)

                # send the refresh token to the frontend
                response = HttpResponse(refresh_token)
                return response

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
            
                # send the refresh token to the frontend
                response = HttpResponse(refresh_token)
                return response
            
            # if user has no refresh token,
            # check if user has a customer_id from Google Ads
            # and send it to the frontend
            except RefreshToken.DoesNotExist:
                print('user has no refresh token')
                try:
                    print('trying to get customer id if exists...')
                    customer_id = NewAccountCustomerID.objects.get(mytoken=mytoken)

                    response2 = HttpResponse(customer_id)
                    return response2

                except NewAccountCustomerID.MultipleObjectsReturned:
                    print('more than one customer id found so getting most recen one')
                    query_set2 = NewAccountCustomerID.objects.filter(mytoken=mytoken)
                    most_recent2 = len(query_set2) - 1
                    query_set2 = query_set2.values()[most_recent2]

                    customer_id = query_set2['customer_id']

                    response2 = HttpResponse(customer_id)
                    return response2

                # new app user that doesn't have refresh token, nor customer id
                except NewAccountCustomerID.DoesNotExist:
                    print('no refresh token nor customer id found')
                    return Response('', status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Get info of the campaigns associated with the customer_id from the request
@api_view(['POST'])
def get_campaigns(request):
    if request.method == 'POST':
        serializer = ReportingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
                print('no refresh token so using the app')
            else: 
                refresh_token = serializer['refreshToken'].value
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
@api_view(['POST'])
def get_keyword_themes_recommendations(request):
    if request.method == 'POST':
        serializer = GetKeywordThemesRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def get_location_recommendations(request):
    if request.method == 'POST':
        serializer = LocationRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

            # get the location
            location = serializer['location'].value

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # call the function to get the recommendations
            get_recommendations = get_geo_location_recommendations(
                refresh_token, 
                location, 
                country_code, 
                language_code)

            response = JsonResponse(get_recommendations, safe=False)
           
            return response
        return Response(data="bad request")

# Create Google Ads account
@api_view(['POST'])
def create_google_ads_account(request):
    if request.method == 'POST':
        serializer = GoogleAdsAccountCreationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            '''
            get the refresh token
            if there is no refresh token in the data sent via the ui
            then it means user doesn't have credentials
            so we can create an account on their behalf
            using our refresh token
            '''
            # if there is no refresh token, use the App's refresh token
            if not serializer['refreshToken'].value:
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                mytoken = serializer['mytoken'].value
            
            # if there is a refresh token, it means an existing user wants
            # to create a new account and we should let them
            else: refresh_token = serializer['refreshToken'].value

            print("refresh_token:")
            print(refresh_token)

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
@api_view(['POST'])
def get_budget(request):
    if request.method == 'POST':
        serializer = GetBudgetRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def get_ad_creatives(request):
    if request.method == 'POST':
        serializer = GetBudgetRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def create_smart_campaign(request):
    if request.method == 'POST':
        serializer = CreateSmartCampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
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
        return Response(data="bad request")

# Get campaign settings for the campaign_id from the request
@api_view(['POST'])
def get_sc_settings(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def enable_campaign(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def pause_campaign(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def delete_campaign(request):
    if request.method == 'POST':
        serializer = CampaignSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def edit_campaign_name(request):
    if request.method == 'POST':
        serializer = CampaignNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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

# Edit budget of Smart Campaign
@api_view(['POST'])
def edit_campaign_budget(request):
    if request.method == 'POST':
        serializer = EditCampaignBudgetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def get_search_terms_report(request):
    if request.method == 'POST':
        serializer = SearchTermsReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def edit_ad_creative(request):
    if request.method == 'POST':
        serializer = EditAdCreativeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def edit_keywords(request):
    if request.method == 'POST':
        serializer = EditKeywordThemesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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
@api_view(['POST'])
def get_business_info(request):
    if request.method == 'POST':
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # get the refresh token
            if serializer['refreshToken'].value != '':
                refresh_token = serializer['refreshToken'].value
                print("refresh_token:")
                print(refresh_token)

                # call the function to get the business info
                gmb_info = business_profile(refresh_token)

                response = JsonResponse(gmb_info, safe=False)
            
                return response
            # if no refresh token, don't try to get GMB info
            else:
                return Response(data="")
   
        return Response(data="bad request")

# Edit geo target locations of smart campaign
@api_view(['POST'])
def edit_geo_target(request):
    if request.method == 'POST':
        serializer = EditGeoTargetsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            '''
            Get the refresh token.
            If there is no refresh token
            it means it is a user that we created the Ads account for them.
            Therefore, use login_customer_id in the headers of API calls,
            and use the app's refresh token.
            If there is a refresh token, use it.
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                use_login_id = True
            else: 
                refresh_token = serializer['refreshToken'].value
                use_login_id = False

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