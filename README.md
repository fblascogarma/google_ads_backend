# Build a web app that is integrated with Google Ads (this is the backend)

This project will teach you how to build a backend for your web app that integrates with Google Ads using Google Ads API. To see the project for the frontend, go [here](https://github.com/fblascogarma/google_ads_frontend).

See [here](https://youtu.be/yVFZvJpLVxk) a 15-minute demo of the product you can have by cloning this repo and following the instructions.

The main goal of this project is to **smooth and accelerate the integration process, while decreasing the cost of implementation & integration**. 
Companies can use my open-source app and the [technical guide](https://docs.google.com/document/d/1Tz0NRHokAFjd-6A0KM9KeLnEvt9XFM4l1PfI9MCE6v8/edit?usp=sharing) I wrote as the **entry point to elements within the Google Ads API**. They can learn about what they can do with Google Ads API and **get a clear idea of how a finished solution could look like**.  

If this project helped you, please give it a star, and if you have suggestions, they are more than welcome. Thank you!

# Assumptions & Prerequisites

1) You already have a Google account. If you haven’t, go [here](https://accounts.google.com/signin).

2) You already have a Google Ads Manager account. If you haven’t, go [here](https://ads.google.com/home/tools/manager-accounts/).

3) You already have a basic/standard developer token access. If you haven’t, go [here](https://developers.google.com/google-ads/api/docs/first-call/dev-token). I have the basic access that gives me 15,000 operations / day (15k resources/day) and 1,000 requests / day, which is more than enough for this tutorial.

4) You already have a web app functioning where you can develop this Google Ads solution. If you haven't, use my [backend starter](https://github.com/fblascogarma/backend_starter) and my [frontend starter](https://github.com/fblascogarma/frontend_starter).

5) You know Python, JavaScript, full-stack web development, and APIs.

I’ll use Django (Python framework) for the backend, React (JavaScript framework/library) for the frontend, and Bootstrap for CSS.

Also, I will use environment variables for privacy concerns and ignore the client_secret.json file from my Google Cloud Platform project.

# Structure of project

In the main directory, there are two important folders called **api** and **backend**, plus the README.md file and the manage.py file. The manage.py file is to use it in the command line (if you are not familiar with Django, read about it). 

The backend folder has the settings.py file of the backend app, and the api folder has the files of the api I built for the project, which also includes the files to make API calls to Google Ads.

Important files in the **api** folder:

1. urls.py has the API endpoints for my frontend to communicate with my backend.
1. views.py has the functions that will make the API calls to Google.

There are two files that are ignored so you will not see them here, but I have them in my local machine. One  is client_secret.json that contains the secret keys of my Google Cloud Platform project. The other one is the db.sqlite3 which is the database file that contains information of my models.

# App Architecture

# Installation

Clone this repo and the repo for the [frontend](https://github.com/fblascogarma/google_ads_frontend). To install the packages needed for the frontend, follow the instructions in the README file of that repo.

Here are the instructions for the backend.

Run

> pip install -r requirements.txt

to install all the libraries you need for the backend to work properly.

# Steps

Check out the [technical guide](https://docs.google.com/document/d/1Tz0NRHokAFjd-6A0KM9KeLnEvt9XFM4l1PfI9MCE6v8/edit?usp=sharing) I wrote that explains every step you need to take. You will see three sections.

Section 1 - Before Starting

Section 2 - Configuration & Installation

Section 3 - Build the Web App

Here I will go over Section 2 - Configuration & Installation.

## Step 1 - Create a Google Cloud project

You need to register your app as a client of Google Ads. You will receive unique client credentials that you will use to authenticate that the one making the calls to the API is your app. 

Sign into your [Google Cloud Platform](https://cloud.google.com/) console, and go to your project. If you haven’t created one, do it by following the steps outlined there. 

When you have your OAuth credentials, download the JSON file and save it to your backend folder. That will be the file that stores your client credentials that authenticates your app to Google’s services. 
That file contains information to link your app with your GCP project. 
Very important are the client id and client secret that tells Google which app project you are using.

You can use a YAML file to load your credentials, or you can use a dictionary to use it. First, I use a YAML file to test the API, but when I started building for the app, I used a dictionary. I recommend you store the values of client secret, client id, developer token, and login customer id in environment variables like I did.

In parallel, you will need to verify your app. See [here](https://support.google.com/cloud/answer/7454865#verification) and [here](https://support.google.com/cloud/answer/9110914?hl=en) for helpful documentation. You can start this now or later on. It can take several weeks. The Cloud team will send you emails and you should try to answer quickly so they don’t block the process.

## Step 2 - Install client library

Install the client library in your preferred language and set up the configurations. In my case, I love Python so I’m going to install Python’s client library.

If you already installed the packages in requirements.txt, you can skip this step and go to Step 3. 

If you didn't installed the packages in the requirements.txt file, then you will have to install these packages for the backend to work properly. I'm specifying the versions that I use in my app in case there were some new updates that could break things.

Django:

> python -m pip install Django==3.2.4

Django Cors Headers:

> python -m pip install django-cors-headers==3.7.0

Django Rest Framework:

> python -m pip install djangorestframework==3.12.4

Google Ads:

> python -m pip install google-ads==14.1.0

I’m using the 14.1.0 version. If you already have a previous version installed and you want to upgrade it to the newest version, just type

> pip install google-ads --upgrade

OAuth Library:

> python -m pip install oauthlib==3.1.1

## Step 3 - Credentials configuration

When the installation is complete, you need to create the YAML file we talked about that contains the necessary authentication information needed to make requests. This will help you to create your first API call or if you regularly use just one set of credentials, but for your app you will probably do the authentication without using a YAML file with the LoadFromStorage method because you will have many users. 

[This example](https://github.com/googleads/googleads-python-lib/blob/master/examples/ad_manager/authentication/create_ad_manager_client_with_refresh_token.py) shows you how to create an OAuth2 client and a AdManagerClient without relying on a yaml file. My app follows this methodology, so you don't need to worry about that, but if you want to check it out, you can do so on Section 3.4 where I cover Authenticatio & Authorization.

The easiest way to generate this yaml file is to copy the [google-ads.yaml](https://github.com/googleads/google-ads-python/blob/master/google-ads.yaml) example from the GitHub repository and modify it to include your credentials, including your developer token, refresh token, client ID, client secret, and login_customer_id. 
[Here](https://developers.google.com/google-ads/api/docs/client-libs/python/configuration#configuration_using_yaml_file) are the steps to configure your YAML file.

## Step 3.1 - Client secret, client ID, and login customer id

The client secret and client ID are in your client_secret.json file you downloaded from your GCP panel after creating the OAuth credentials for your app. And the login customer id is the customer id of your manager account on google ads (you have to put it without hyphens).

Store these in environment variables. You need to include client_secret.json and db.sqlite3 files in .gitignore in case you don’t want others to access sensitive information about your app.

## Step 3.2 - Developer token

To copy paste your developer token, sign in your Manager account on Google Ads, go to Tools & Settings > Settings > API center. There you will see your developer token. 

Store this in an environment variable.

## Step 3.3 - Refresh token

For the refresh token (see steps [here](https://developers.google.com/identity/protocols/oauth2#5.-refresh-the-access-token,-if-necessary.)), you need to know that the authorization sequence begins when your application redirects a browser to a Google URL; the URL includes query parameters that indicate the type of access being requested. 

Google handles the user authentication, session selection, and user consent. The result is an authorization code, which the application can exchange for an access token and a refresh token.

The application should store the refresh token for future use and use the access token to access a Google API. Once the access token expires, the application uses the refresh token to obtain a new one.

To learn more about the expiration of refresh tokens, go [here](https://developers.google.com/identity/protocols/oauth2#expiration).

To generate the refresh token, create a temporary [authenticate_in_web_application.py](https://github.com/googleads/google-ads-python/blob/master/examples/authentication/authenticate_in_web_application.py) file and make sure that the redirect URI is one that you have authorized in your GCP project. 

Make sure that the URL you are using in your code to redirect users is included in the authorized redirect URIs section in the GCP project. See image below.

Also, make sure that you include the gmail account in the list of authorized test users in your GCP project. See image below.

Go to the folder where you have that authenticate_in_web_application.py file and type

> python authenticate_in_web_application.py --client_secrets_path=*/path/to/secrets.json*

In my case,

> python authenticate_in_web_application.py --client_secrets_path=client_secret.json

Because I have the client_secret.json file in the same folder as the authenticate_in_web_application.py file.

You will see in your terminal this:

> Paste this URL into your browser:

Paste that link to your browser, and this will trigger the OAuth flow where users will authenticate themseleves with a Google account (example@gmail.com) and accept the permissions that your app wants to access (manage Google Ads account on behalf of user).

If successful, you will see that the window in the browser changes to white and only says

> Authorization code was successfully retrieved. Please check the console output.

Go to your terminal and you will see the refresh token. Here is an example of an old, inactive refresh token:

> Your refresh token is: 1//0fCEKBDhWM7EDCgYIARAAGA8SNwF-L9IrNZoRYo4oPNBSw-lsArm3SchWbNOTcueEq6XoU3MH4FaYUc2caP6V-OQE5M79JmUqglI

Add your refresh token to your client library configuration as described [here](https://developers.google.com/google-ads/api/docs/client-libs/python/configuration). This means you need to paste it in your YAML file.

## Step 3.4 - Make first API call!

Now you will do your first API call. The recommended one to start is [get_campaigns.py](https://github.com/googleads/google-ads-python/blob/master/examples/basic_operations/get_campaigns.py). I saved that file in a folder called operations inside google_ads folder. I added a variable to store the path of my yaml file and I passed it as an argument in the GoogleAdsClient service.

Get the client id of your new client, in my case Enjoy has the campaigns and the id without dashes is 2916870939. 

When I run

> python get_campaigns.py --client_id=2916870939

Or

> python get_campaigns.py -c=2916870939

I got

> Campaign with ID 9364799724 and name "LupusArte01" was found.
>
> Campaign with ID 9364937164 and name "Querés verte linda?" was found.
> 
> Campaign with ID 10045433888 and name "Shopping (manual)" was found.
>
> Campaign with ID 10053234624 and name "Website traffic-Search-1" was found.
>
> Campaign with ID 10053620565 and name "Sales-Search-3-test" was found.
> 
> Campaign with ID 10054607172 and name "Vestidos para embarazadas" was found.
>
> Campaign with ID 10119892291 and name "test1" was found.
>
> Campaign with ID 10124224557 and name "Sales-Search-4" was found.
>
> Campaign with ID 10169844221 and name "Test Margio" was found.
>
> Campaign with ID 10178566950 and name "Mejores aceites de San Juan" was found.
> 
> Campaign with ID 10564904122 and name "ENJOY MOMMYHOOD" was found.

Here you get the campaign.id and campaign.name of all the campaigns that client 2916870939 has.

This is just to get you started so you can learn about making API calls to Google Ads API. 

By cloning this project and the frontend that is in a separate repo in my GitHub profile, you are ready to exploring what you can do with Google Ads API.