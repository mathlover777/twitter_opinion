import config
import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs

def setup_oauth():
    """Authorize your app via identifier."""
    # Request token
    oauth = OAuth1(config.CONSUMER_KEY, client_secret=config.CONSUMER_SECRET)
    r = requests.post(url=config.REQUEST_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)

    resource_owner_key = credentials.get('oauth_token')[0]
    resource_owner_secret = credentials.get('oauth_token_secret')[0]

    # Authorize
    authorize_url = config.AUTHORIZE_URL + resource_owner_key
    print 'Please go here and authorize: ' + authorize_url

    verifier = raw_input('Please input the verifier: ')
    oauth = OAuth1(config.CONSUMER_KEY,
                   client_secret=config.CONSUMER_SECRET,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=verifier)

    # Finally, Obtain the Access Token
    r = requests.post(url=config.ACCESS_TOKEN_URL, auth=oauth)
    credentials = parse_qs(r.content)
    token = credentials.get('oauth_token')[0]
    secret = credentials.get('oauth_token_secret')[0]

    return token, secret

def authenticate():
	print 'authenticating started'
	config.init_app_config()
	token, secret = setup_oauth()
	print "OAUTH_TOKEN: " + token
	print "OAUTH_TOKEN_SECRET: " + secret

	with open(config.USER_INFO,'ab') as fp:
		fp.write(token + '\n')
		fp.write(secret + '\n')

	print 'these will be saved in userdata.txt'

	return

def display_user_data():
	config.init_user_config()
	user_count = 1
	for (token,secret) in config.USER_TOKEN_LIST:
		print 'user_'+str(user_count)+' info ****\n'
		print 'token = {' + token + '}'
		print 'secret = {' + secret + '}'
		user_count = user_count + 1
	return

def reset_file(filename):
	with open(filename,'wb'):
		pass

def clear_all_user_data():
	reset_file(config.USER_INFO)
	return

# display_user_data()
# clear_all_user_data()
authenticate()