import argparse
import hashlib
import os
import re
import socket
import sys

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
        'https://www.googleapis.com/auth/adwords',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid']
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

    # Retrieves an authorization code by opening a socket to receive the
    # redirect request and parsing the query parameters set in the URL.
    # code = _get_authorization_code(passthrough_val)

    # # Pass the code back into the OAuth module to get a refresh token.
    # flow.fetch_token(code=code)
    # refresh_token = flow.credentials.refresh_token

    return authorization_url, passthrough_val


def get_token(google_access_code):

    # Use the env variable that has the path to the client_secret.json file
    GOOGLE_CLIENT_SECRET_PATH = os.environ.get("GOOGLE_CLIENT_SECRET_PATH", None)
    client_secrets_path = GOOGLE_CLIENT_SECRET_PATH
    # And also add the scopes (info) you want to retrieve from your users
    scopes = [
        'https://www.googleapis.com/auth/adwords',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid']
    flow = Flow.from_client_secrets_file(client_secrets_path, scopes=scopes)
    # Specify again the redirect_uri because it's required by Flow
    flow.redirect_uri = _REDIRECT_URI

    # Pass the code back into the OAuth module to get a refresh token.
    flow.fetch_token(code=google_access_code)
    refresh_token = flow.credentials.refresh_token

    return refresh_token

def _get_authorization_code(passthrough_val):
    """Opens a socket to handle a single HTTP request containing auth tokens.
    Args:
        passthrough_val: an anti-forgery token used to verify the request
            received by the socket.
    Returns:
        a str access token from the Google Auth service.
    """
    # Open a socket at localhost:PORT and listen for a request
    sock = socket.socket()
    # sock.bind(('localhost', _PORT))
    sock.bind(('localhost', 3030))
    sock.listen(1)
    connection, address = sock.accept()
    data = connection.recv(1024)
    # Parse the raw request to retrieve the URL query parameters.
    params = _parse_raw_query_params(data)

    try:
        if not params.get("code"):
            # If no code is present in the query params then there will be an
            # error message with more details.
            error = params.get("error")
            message = f"Failed to retrieve authorization code. Error: {error}"
            raise ValueError(message)
        elif params.get("state") != passthrough_val:
            message = "State token does not match the expected state."
            raise ValueError(message)
        else:
            message = "Authorization code was successfully retrieved."
    except ValueError as error:
        print(error)
        sys.exit(1)
    finally:
        response = (
            "HTTP/1.1 200 OK\n"
            "Content-Type: text/html\n\n"
            f"<b>{message}</b>"
            "<p>Please check the console output.</p>\n"
        )

        connection.sendall(response.encode())
        connection.close()

    return params.get("code")


def _parse_raw_query_params(data):
    """Parses a raw HTTP request to extract its query params as a dict.
    Note that this logic is likely irrelevant if you're building OAuth logic
    into a complete web application, where response parsing is handled by a
    framework.
    Args:
        data: raw request data as bytes.
    Returns:
        a dict of query parameter key value pairs.
    """
    # Decode the request into a utf-8 encoded string
    decoded = data.decode("utf-8")
    # Use a regular expression to extract the URL query parameters string
    match = re.search("GET\s\/\?(.*) ", decoded)
    params = match.group(1)
    # Split the parameters to isolate the key/value pairs
    pairs = [ pair.split("=") for pair in params.split("&") ]
    # Convert pairs to a dict to make it easy to access the values
    return { key: val for key, val in pairs }

