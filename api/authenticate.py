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

import hashlib
import os

from google_auth_oauthlib.flow import Flow


_SCOPE = "https://www.googleapis.com/auth/adwords"
# _PORT = 8080
# _REDIRECT_URI = f"http://localhost:{_PORT}"
_REDIRECT_URI = f"http://localhost:3000/"


def connect():
    """The main method, starts a basic server and initializes an auth request.
    Args:
        client_secrets_path: a path to where the client secrets JSON file is
            located on the machine running this example.
        scopes: a list of API scopes to include in the auth request, see:
            https://developers.google.com/identity/protocols/oauth2/scopes
    """
    # Use the env variable that has the path to the client_secret.json file
    GOOGLE_CLIENT_SECRET_PATH = os.environ.get("GOOGLE_CLIENT_SECRET_PATH", None)
    client_secrets_path = GOOGLE_CLIENT_SECRET_PATH
    # And also add the scopes (info) you want to retrieve from your users
    scopes = [
        'https://www.googleapis.com/auth/adwords',              # for Google Ads
        'https://www.googleapis.com/auth/business.manage']      # for Google My Business
    flow = Flow.from_client_secrets_file(client_secrets_path, scopes=scopes)
    flow.redirect_uri = _REDIRECT_URI

    # Create an anti-forgery state token as described here:
    # https://developers.google.com/identity/protocols/OpenIDConnect#createxsrftoken
    passthrough_val = hashlib.sha256(os.urandom(1024)).hexdigest()

    authorization_url, state = flow.authorization_url(
        # return a refresh token and an access token the first time that your app 
        # exchanges an authorization code for tokens
        access_type='offline',
        # increase your assurance that an incoming connection is the result of 
        # an authentication request
        state=passthrough_val,
        # the new access token will also cover any scopes to which the user 
        # previously granted the application access
        include_granted_scopes='true',
        # forces the authorization flow even if the user already did that 
        # (helpful for testing in dev)
        approval_prompt='force'
    )

    return authorization_url, passthrough_val


def get_token(google_access_code):

    # Use the env variable that has the path to the client_secret.json file
    GOOGLE_CLIENT_SECRET_PATH = os.environ.get("GOOGLE_CLIENT_SECRET_PATH", None)
    client_secrets_path = GOOGLE_CLIENT_SECRET_PATH
    # And also add the scopes (info) you want to retrieve from your users
    scopes = [
        'https://www.googleapis.com/auth/adwords',              # for Google Ads
        'https://www.googleapis.com/auth/business.manage']      # for Google My Business
    flow = Flow.from_client_secrets_file(client_secrets_path, scopes=scopes)
    # Specify again the redirect_uri because it's required by Flow
    flow.redirect_uri = _REDIRECT_URI

    # Pass the code back into the OAuth module to get a refresh token.
    flow.fetch_token(code=google_access_code)
    refresh_token = flow.credentials.refresh_token

    return refresh_token