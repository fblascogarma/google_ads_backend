# Build a web app that is integrated with Google Ads

This project will teach you how to **build a backend for your web app** that integrates with Google Ads using Google Ads API. To see the project for the frontend, go [here](https://github.com/fblascogarma/google_ads_frontend).

See [here](https://youtu.be/yVFZvJpLVxk) a 15-minute demo of the product you can have by cloning this repo and following the instructions.

The main goal of this project is to **smooth and accelerate the integration process, while decreasing the cost of implementation & integration**. 

Companies can use my open-source app and the [technical guide](https://docs.google.com/document/d/10WyzDUNZTVHhenWgCopf3YyaRDsyoavc7aHuOAMJF6Y/edit?usp=sharing) I wrote as the **entry point to elements within the Google Ads API**. 

They can learn about what they can do with Google Ads API and **get a clear idea of how a finished solution could look like**.  

If this project helped you, please **give it a star**, and if you have suggestions, they are more than welcome. 

Thank you!

# Assumptions & Prerequisites

1. You already have a Google account. If you haven’t, go [here](https://accounts.google.com/signin).

1. You already have a Google Ads Manager account. If you haven’t, go [here](https://ads.google.com/home/tools/manager-accounts/).

1. You already have a basic/standard developer token access. If you haven’t, go [here](https://developers.google.com/google-ads/api/docs/first-call/dev-token). I have the basic access that gives me 15,000 operations / day (15k resources/day) and 1,000 requests / day, which is more than enough for this tutorial.

1. You know Python, JavaScript, full-stack web development, and APIs.

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

![app architecture](https://user-images.githubusercontent.com/62343770/151630725-253d241a-6239-405f-9355-cf5dbfd381f9.png)


# Installation

See [here](https://youtu.be/WvP3vtc_o7Q) a video tutorial on how to set up this web app.

Clone this repo and the repo for the [frontend](https://github.com/fblascogarma/google_ads_frontend). To install the packages needed for the frontend, follow the instructions in the README file of that repo.

Here are the instructions for the backend.

1. Install of dependencies.

> pip install -r requirements.txt

2. Get a new secret key for the app.
    1. Go to [MiniWebTool](http://www.miniwebtool.com/django-secret-key-generator/) to generate a secret key for the backend app.
    2. Go to the settings.py file inside the backend folder.
    3. Replace the secret key value in line #37 for the secret key generated using the web tool.

3. Make the necessary migrations.

> python manage.py migrate

4. Create a super user to manage the backend.

> python manage.py createsuperuser

5. Start the backend server.

> python manage.py runserver

6. Open the backend app in your browser.

> localhost:8000/admin/

7. You are all set!

# Steps

You have to create a Google Cloud project and get the necessary credentials to consume Google's APIs.

## Step 1 - Create a Google Cloud project

You need to register your app as a client of Google Ads. You will receive unique client credentials that you will use to authenticate that the one making the calls to the API is your app. 

Sign into your [Google Cloud Platform](https://cloud.google.com/) console, and go to your project. If you haven’t created one, do it by following the steps outlined there. 

When you have your OAuth credentials, download the JSON file and save it to your backend folder. That will be the file that stores your client credentials that authenticates your app to Google’s services. 
That file contains information to link your app with your GCP project. 
Very important are the client id and client secret that tells Google which app project you are using.

You can use a YAML file to load your credentials, or you can use a dictionary to use it like I did. I recommend you store the values of client secret, client id, developer token, and login customer id in environment variables like I did.

Also, enable the APIs you are going to use. To enable APIs for the project, you need to go to APIs & Services > Dashboard, in your GCP project and click on ‘ENABLE APIS AND SERVICES’. Use the search bar to enable the Google Ads API.

### Google My Business

If your users have [Google My Business](https://developers.google.com/my-business/ref_overview) (now called Google Business Profile), it makes sense to also integrate those APIs to your app. To do so, you will need:
1. Get your project approved for GMB. This is a different approval process that you went through when getting a developer token for the Google Ads API.
1. Fill out [this form](https://docs.google.com/forms/d/1XTQc-QEjsE7YrgstyJxbFDnwmhUhBFFvpNJBw3VzuuE/viewform). Find more information about this [here](https://developers.google.com/my-business/content/prereqs). **Important**: You will get it approved for a specific project, so if you requested access to the GMB API for one project, and then you want to use it on another project, you need to request access to that one too.  
1. Go to the project on GCP and enable these two APIs like you did with the Google Ads API:
    1. My Business Business Information API
    1. My Business Account Management API
1. You are going to be able to use those APIs after you get approval from Google. 

Those two API for Google My Business are needed to get the business location id that you can use when creating a Smart Campaign. Check the Campaign Creation section for more information on this.

### Verify your Google Cloud project

In parallel, you will need to verify your app. See [here](https://support.google.com/cloud/answer/7454865#verification) and [here](https://support.google.com/cloud/answer/9110914?hl=en) for helpful documentation. You can start this now or later on. It can take several weeks. The Cloud team will send you emails and you should try to answer quickly so they don’t block the process.

## Step 2 - Credentials configuration

Create environment variables to store all the credentials. Create the following environment variables.

1. GOOGLE_CLIENT_ID to store the client_id of the Google Cloud project.

1. GOOGLE_CLIENT_SECRET to store the client_secret of the Google Cloud project.

1. GOOGLE_DEVELOPER_TOKEN to store your developer token.

1. GOOGLE_CLIENT_SECRET_PATH to store the pack to the client_secret.json file you downloaded in the previous step.

More info about each of these below.

### Client secret, client ID, and login customer id

The client secret and client ID are in your client_secret.json file you downloaded from your GCP panel after creating the OAuth credentials for your app. And the login customer id is the customer id of your manager account on google ads (you have to put it without hyphens).

### Developer token

To copy paste your developer token, sign in your Manager account on Google Ads, go to Tools & Settings > Settings > API center. There you will see your developer token. 

### Refresh token

For the refresh token (see steps [here](https://developers.google.com/identity/protocols/oauth2#5.-refresh-the-access-token,-if-necessary.)), you need to know that the authorization sequence begins when your application redirects a browser to a Google URL; the URL includes query parameters that indicate the type of access being requested. 

Google handles the user authentication, session selection, and user consent. The result is an authorization code, which the application can exchange for an access token and a refresh token.

The application should store the refresh token for future use and use the access token to access a Google API. Once the access token expires, the application uses the refresh token to obtain a new one.

![oauth flow](https://user-images.githubusercontent.com/62343770/151631414-53d70b03-14db-4dfa-bde4-81b559ad6b43.png)


To learn more about the expiration of refresh tokens, go [here](https://developers.google.com/identity/protocols/oauth2#expiration).

To generate the refresh token, create a temporary [authenticate_in_web_application.py](https://github.com/googleads/google-ads-python/blob/master/examples/authentication/authenticate_in_web_application.py) file and make sure that the redirect URI is one that you have authorized in your GCP project. 

Make sure that the URL you are using in your code to redirect users is included in the authorized redirect URIs section in the GCP project. See image below.

<img width="880" alt="authorized_redirect_uris" src="https://user-images.githubusercontent.com/62343770/151631292-3aadfd3a-1a71-446a-9776-36e5b4ed6a80.png">


Also, make sure that you include the gmail account in the list of authorized test users in your GCP project. See image below.

<img width="706" alt="Authorize_test_users" src="https://user-images.githubusercontent.com/62343770/151631839-6c6e4605-84b9-4c21-8a50-4599d57897ac.png">

# Deploy to production

Although deploying to production is out of the scope of this project, I wanted to provide guidance on important things to consider, and deployment alternatives.

This section has two sub-sections (backend and frontend) that explains what you need to do to deploy Fran Ads to production. These changes are needed for the app to work correctly.

This section doesn't cover load balancers, queue systems, nor scaling architectures. That's on you to define how and what to use.

## Backend

There are three things to consider when thinking of deploying the backend to production.

1. The first thing you should do is turn off the debug mode. You don't want it running when your app is in production. Go to the [settings.py](https://github.com/fblascogarma/google_ads_backend/blob/main/backend/settings.py#L40) file, and change the 

> DEBUG = True 

to 

> DEBUG = False 

in line 40.

2. Set up error email alerts so you know when an exception has been raised. This is important to fix those issues that can appear. Include all email addresses that you want by adding the ADMINS setting in the [settings.py](https://github.com/fblascogarma/google_ads_backend/blob/main/backend/settings.py) file. Below an example.
> ADMINS = [
>     ('John', 'john@example.com'), 
>     ('Mary', 'mary@example.com')
> ]

3. Enable your server to send emails so you get the error email alerts. Depending on your arragement complexity, you need to add to the [settings.py](https://github.com/fblascogarma/google_ads_backend/blob/main/backend/settings.py) file all of these below.

> [EMAIL_HOST](https://docs.djangoproject.com/en/4.0/ref/settings/#:~:text=store%20output%20files.-,EMAIL_HOST,-%C2%B6)
> 
> [EMAIL_HOST_PASSWORD](https://docs.djangoproject.com/en/4.0/ref/settings/#:~:text=See%20also%20EMAIL_PORT.-,EMAIL_HOST_PASSWORD,-%C2%B6)
>
> [EMAIL_HOST_USER](https://docs.djangoproject.com/en/4.0/ref/settings/#:~:text=See%20also%20EMAIL_HOST_USER.-,EMAIL_HOST_USER,-%C2%B6)
>
> [EMAIL_PORT](https://docs.djangoproject.com/en/4.0/ref/settings/#:~:text=See%20also%20EMAIL_HOST_PASSWORD.-,EMAIL_PORT,-%C2%B6)
>
> [EMAIL_USE_TLS](https://docs.djangoproject.com/en/4.0/ref/settings/#:~:text=in%20UTC%20(False).-,EMAIL_USE_TLS,-%C2%B6)

[Here](https://django-book.readthedocs.io/en/latest/chapter12.html#using-different-settings-for-production) you will learn different ways to set up your settings files to keep your dev environment isolated from your prod environment.

## Frontend

First, you need to create a production build by running

> npm run build

This will create a **build** directory with a production build of your app. Inside the build/static directory will be your JavaScript and CSS files. Each filename inside of build/static will contain a unique hash of the file contents. This hash in the file name enables [long term caching techniques](https://create-react-app.dev/docs/production-build#static-file-caching).

The frontend is completely platform-agnostic, so you can use any server software of your choice. See [here](https://create-react-app.dev/docs/deployment/#serving-apps-with-client-side-routing) how to serve the index.html for any unkown paths.

Finally, you can override where your app is hosted by adding the field homepage in your [package.json](https://github.com/fblascogarma/google_ads_frontend/blob/main/package.json) file. See example below.

> "homepage": "http://mywebsite.com/relativepath"

Check out the links provided below for each Cloud provider.

1. [Google Cloud](https://cloud.google.com/community/tutorials/deploy-react-nginx-cloud-run)
2. [AWS Amplify](https://create-react-app.dev/docs/deployment/#aws-amplify)
3. [Azure](https://create-react-app.dev/docs/deployment/#azure)
4. [Firebase](https://create-react-app.dev/docs/deployment/#firebase)
5. [Heroku](https://create-react-app.dev/docs/deployment/#heroku)
6. [Netlify](https://create-react-app.dev/docs/deployment/#netlify)
7. [Vercel](https://create-react-app.dev/docs/deployment/#vercel)

# Final remarks

This is just to get you started so you can learn about making API calls to Google Ads API and Google My Business API. 

By cloning this project and the frontend that is in a separate repo in my GitHub profile, you are ready to start exploring what you can do with Google Ads API.

#### **Happy hacking!**