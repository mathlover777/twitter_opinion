from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

CONSUMER_KEY = "oWCZitIqv3MGC5ezWqzU1ExFw"
CONSUMER_SECRET = "hSzBWJ4UOKP0zVfsL0wjgN5W3O0smIQ06ameGgCCJhecew7wPH"

OAUTH_TOKEN = "125927111-mwuiiFNhB6kVlMewcxvqYsipVHL3Ge7Xbr6JvgKB"
OAUTH_TOKEN_SECRET = "8NLcysoH2lHurV9aIUUCB0y6CycDBs9nzWtGU2c5c9OGQ"



def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(CONSUMER_KEY, client_secret=CONSUMER_SECRET)
    r = requests.post(url=REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(CONSUMER_KEY,
                   client_secret=CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret


def get_oauth():
    oauth = OAuth1(CONSUMER_KEY,
                client_secret=CONSUMER_SECRET,
                resource_owner_key=OAUTH_TOKEN,
                resource_owner_secret=OAUTH_TOKEN_SECRET)
    return oauth

if __name__ == "__main__":
    if not OAUTH_TOKEN:
        token, secret = setup_oauth()
        print "OAUTH_TOKEN: " + token
        print "OAUTH_TOKEN_SECRET: " + secret
        print
    else:
        oauth = get_oauth()
        r = requests.get(url="https://api.twitter.com/1.1/friends/ids.json?screen_name=derinbadrasli&user_id=359965206", auth=oauth)
        print r.json()
        print r.status_code
        r = requests.get(url="https://api.twitter.com/1.1/application/rate_limit_status.json?resources=friends",auth=oauth)
        s = r.json()
        print r.status_code
        print s
        print('**************************')
        print s['resources']['friends']['/friends/ids']['reset']
        print s['resources']['friends']['/friends/ids']['limit']
        print s['resources']['friends']['/friends/ids']['remaining'] 
        print('\n')

# 'resources': {u'friends': {u'/friends/list': {u'reset': 1430474011, u'limit': 15, u'remaining': 15}