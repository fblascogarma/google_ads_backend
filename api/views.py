from json.decoder import JSONDecoder
from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Article, AdWordsCredentials, RefreshToken, NewAccountCustomerID
from .serializers import ArticleSerializer, UserSerializer, AdWordsCredentialsSerializer, AntiForgeryTokenSerializer, RefreshTokenSerializer, MyTokenSerializer, ReportingSerializer, GetKeywordThemesRecommendationsSerializer, LocationRecommendationsSerializer, GoogleAdsAccountCreationSerializer, NewAccountCustomerIDSerializer, GetBudgetRecommendationsSerializer, CreateSmartCampaignSerializer
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
from .create_smart_campaign import create_smart


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

# Callback to get the refresh token and save it to our backend
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
            # get the token associated with that user
            mytoken = serializer['mytoken'].value

            # get the refresh token associated with that token.
            # if there is only one mytoken with that value in the database
            # first try this
            try:
                
                refresh_token = RefreshToken.objects.get(mytoken=mytoken)

                # send the refresh token to the frontend
                response = HttpResponse(refresh_token)
                return response

            # if there are more than one mytoken with that value in the database
            # you will get the MultipleObjectsReturned error
            # so then try this
            except RefreshToken.MultipleObjectsReturned:
                
                query_set = RefreshToken.objects.filter(mytoken=mytoken)
                # get the last one which is the most recent one
                most_recent = len(query_set) - 1
                print(most_recent)
                query_set = query_set.values()[most_recent]
        
                refresh_token = query_set['refreshToken']
            
                # send the refresh token to the frontend
                response = HttpResponse(refresh_token)
                return response

            # if user has no refresh token,
            # check if user has a customer_id from Google Ads
            # and send it to the frontend
            finally:
                try:
                    customer_id = NewAccountCustomerID.objects.get(mytoken=mytoken)

                    response2 = HttpResponse(customer_id)
                    return response2

                except NewAccountCustomerID.MultipleObjectsReturned:

                    query_set2 = NewAccountCustomerID.objects.filter(mytoken=mytoken)
                    most_recent2 = len(query_set2) - 1
                    query_set2 = query_set2.values()[most_recent2]

                    customer_id = query_set['customer_id']

                    response2 = HttpResponse(customer_id)
                    return response2

                except NewAccountCustomerID.DoesNotExist:
                    response2 = []
                    print(response2)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Get info of the campaigns associated with the customer_id from the request
@api_view(['POST'])
def get_campaigns(request):
    if request.method == 'POST':
        serializer = ReportingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            '''
            get the refresh token
            if there is no refresh token in the data sent via the ui
            then it means user doesn't have credentials
            and we are using our credentials to manage their linked account
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN

            # if there is a refresh token, it means an existing user wants
            # to create a new account and we should let them
            else: 
                refresh_token = serializer['refreshToken'].value

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the date range
            date_range = serializer['date_range'].value
            # print(date_range)

            # call the function to get the campaigns
            get_campaign_info = campaign_info(refresh_token, customer_id, date_range)
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
            get the refresh token
            if there is no refresh token in the data sent via the ui
            then it means user doesn't have credentials
            and we are using our credentials to manage their linked account
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN

            # if there is a refresh token, it means an existing user wants
            # to create a new account and we should let them
            else: 
                refresh_token = serializer['refreshToken'].value

            # get the keyword text
            keyword_text = serializer['keyword_text'].value

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # call the function to get the recommendations
            get_recommendations = get_keyword_themes_suggestions(refresh_token, keyword_text, country_code, language_code)
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
            get the refresh token
            if there is no refresh token in the data sent via the ui
            then it means user doesn't have credentials
            and we are using our credentials to manage their linked account
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN

            # if there is a refresh token, it means an existing user wants
            # to create a new account and we should let them
            else: 
                refresh_token = serializer['refreshToken'].value

            # get the location
            location = serializer['location'].value

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # call the function to get the recommendations
            get_recommendations = get_geo_location_recommendations(refresh_token, location, country_code, language_code)

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
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN
                mytoken = serializer['mytoken'].value
            # if there is a refresh token, it means an existing user wants
            # to create a new account and we should let them
            else: refresh_token = serializer['refreshToken'].value

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
            get the refresh token
            if there is no refresh token in the data sent via the ui
            then it means user doesn't have credentials
            and we are using our credentials to manage their linked account
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN

            # if there is a refresh token, it means an existing user wants
            # to create a new account and we should let them
            else: 
                refresh_token = serializer['refreshToken'].value

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

            # call the function to get the recommendations
            get_recommendations = get_budget_recommendation(
                refresh_token, customer_id, display_name, 
                landing_page, geo_target_names, language_code, 
                country_code)
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
            get the refresh token
            if there is no refresh token in the data sent via the ui
            then it means user doesn't have credentials
            and we are using our credentials to manage their linked account
            '''
            if serializer['refreshToken'].value == '':
                GOOGLE_REFRESH_TOKEN = os.environ.get("GOOGLE_REFRESH_TOKEN", None)
                refresh_token = GOOGLE_REFRESH_TOKEN

            # if there is a refresh token, it means an existing user wants
            # to create a new account and we should let them
            else: 
                refresh_token = serializer['refreshToken'].value

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
                phone_number, landing_page, business_name,
                headline_1_user, headline_2_user, headline_3_user,
                desc_1_user, desc_2_user, campaign_name)
            print(smart_campaign)
            
            response = JsonResponse(smart_campaign, safe=False)
           
            return response
        return Response(data="bad request")