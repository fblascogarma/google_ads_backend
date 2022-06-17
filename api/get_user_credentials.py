from .models import RefreshToken


def get_refresh_token(mytoken):
    print('start trying to get user credentials...')

    # get the refresh token associated with that token.
    # if there is only one mytoken with that value in the database
    # first try this
    try:
        print('trying to get refresh token...')
        refresh_token = RefreshToken.objects.get(mytoken=mytoken)
        print('refresh token found')
        print(refresh_token)

        return refresh_token

    # if there are more than one mytoken with that value in the database
    # you will get the MultipleObjectsReturned error
    # so then try this
    except RefreshToken.MultipleObjectsReturned:
        print('more than one mytoken found so getting most recent refresh token')
        query_set = RefreshToken.objects.filter(mytoken=mytoken)
        # get the last one which is the most recent one
        most_recent = len(query_set) - 1
        print(most_recent)
        query_set = query_set.values()[most_recent]

        refresh_token = query_set['refreshToken']
        print("most recent refresh_token found")
        print(refresh_token)
    
        return refresh_token
    
    # if user has no refresh token
    except RefreshToken.DoesNotExist:
        print('no refresh token found')
        return None