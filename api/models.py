from django.db import models

# Create your models here.
class Article(models.Model):                    # you will create a table called Article
    title = models.CharField(max_length=100)    # ids are created automatically so you don't have to create an id
    description = models.TextField()

    def __str__(self): 
        return self.title

# Model to store the access code and refresh token of users to handle their Google Ads via the API
class AdWordsCredentials(models.Model):                   
    mytoken = models.CharField(max_length=500)
    google_access_code = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)

    def __str__(self): 
        return self.mytoken, self.google_access_code, self.refresh_token

# Model to store the access code that Google services provide to get the refresh token
class AntiForgeryToken(models.Model):                   
    mytoken = models.CharField(max_length=600)
    google_access_code = models.CharField(max_length=600)
    passthrough_val = models.CharField(max_length=600)
    

    def __str__(self): 
        return self.mytoken, self.google_access_code, self.passthrough_val

# Model for the refresh token
class RefreshToken(models.Model):                   
    mytoken = models.CharField(max_length=500)
    refreshToken = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken

# Model to serializer mytoken
class MyToken(models.Model):                   
    mytoken = models.CharField(max_length=500)

    def __str__(self): 
        return self.mytoken

# Model to serializer refresh token and customer id
class CustomerID(models.Model):                   
    refreshToken = models.CharField(max_length=500)
    customer_id = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.customer_id

# Model to serializer frontend data to get info of campaigns
class Reporting(models.Model):                   
    # we make the refreshToken optional in case user created account via Fran Ads
    refreshToken = models.CharField(max_length=500, blank=True)
    customer_id = models.CharField(max_length=500)
    date_range = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.customer_id, self.date_range

# Model to get keyword themes recommendations
class KeywordThemesRecommendations(models.Model):                   
    refreshToken = models.CharField(max_length=500)
    keyword_text = models.CharField(max_length=500)
    country_code = models.CharField(max_length=500)
    language_code = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.keyword_text, self.country_code, self.language_code

# Model to get geo location recommendations
class LocationRecommendations(models.Model):                   
    refreshToken = models.CharField(max_length=500)
    language_code = models.CharField(max_length=500)
    country_code = models.CharField(max_length=500)
    location = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.location, self.country_code, self.language_code

# Model to create Google Ads account
class GoogleAdsAccountCreation(models.Model):  
    '''make the refresh token optional so if there is no value
    it means we are going to use the app's refresh token because
    user hasn't authenticated with an existing Google Ads account'''                 
    refreshToken = models.CharField(max_length=500, blank=True)
    mytoken = models.CharField(max_length=500, blank=True)
    account_name = models.CharField(max_length=500)
    currency = models.CharField(max_length=10)
    time_zone = models.CharField(max_length=100)
    email_address = models.CharField(max_length=500)

    def __str__(self): 
        return self.refreshToken, self.mytoken, self.time_zone, self.currency, self.account_name, self.email_address

# Model for the customer id of the newly created Google Ads account
# for users who had zero accounts created before
class NewAccountCustomerID(models.Model):                   
    mytoken = models.CharField(max_length=500)
    customer_id = models.CharField(max_length=500)

    def __str__(self): 
        return self.customer_id