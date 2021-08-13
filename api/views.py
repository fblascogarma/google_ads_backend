from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import Article, AdWordsCredentials, RefreshToken
from .serializers import ArticleSerializer, UserSerializer, AdWordsCredentialsSerializer, AntiForgeryTokenSerializer, RefreshTokenSerializer, MyTokenSerializer, ReportingSerializer, KeywordThemesRecommendationsSerializer
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers, status

from .authenticate import connect, get_token
from .list_accessible_accounts import list_accounts
from .get_campaigns import campaign_info
from .create_smart_campaign import get_keyword_themes_suggestions


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
            serializer_credentials = AdWordsCredentialsSerializer(data={'mytoken': mytoken, 'google_access_code': google_access_code, 'refresh_token': refresh_token})
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

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Get info of the campaigns associated with the customer_id from the request
@api_view(['POST'])
def get_campaigns(request):
    if request.method == 'POST':
        serializer = ReportingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # get the refresh token
            refresh_token = serializer['refreshToken'].value

            # get the customer_id
            customer_id = serializer['customer_id'].value
            customer_id = str(customer_id)

            # get the date range
            date_range = serializer['date_range'].value
            # print(date_range)

            # call the function to get the campaigns
            get_campaign_info = campaign_info(refresh_token, customer_id, date_range)
            # print(get_campaign_info)

            # response = HttpResponse(list_of_accounts)
            response = JsonResponse(get_campaign_info, safe=False)
           
            return response
        return Response(data="bad request")


# Get keyword themes recommendations
@api_view(['POST'])
def get_keyword_themes_recommendations(request):
    if request.method == 'POST':
        serializer = KeywordThemesRecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            # get the refresh token
            refresh_token = serializer['refreshToken'].value

            # get the keyword text
            keyword_text = serializer['keyword_text'].value

            # get the country code
            country_code = serializer['country_code'].value

            # get the language code
            language_code = serializer['language_code'].value

            # call the function to get the recommendations
            get_recommendations = get_keyword_themes_suggestions(refresh_token, keyword_text, country_code, language_code)

            # response = HttpResponse(list_of_accounts)
            response = JsonResponse(get_recommendations, safe=False)
           
            return response
        return Response(data="bad request")