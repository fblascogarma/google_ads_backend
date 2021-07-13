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