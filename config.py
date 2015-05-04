# app specific key
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
######################

# user specific key
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''
#####################

BASE_URL = 'https://api.twitter.com'
TWEET_STORAGE_SHEET = 'tweets.csv'
EXTRACT_INFO = 'extractinfo.txt'
USER_INFO = 'userdata.txt'
APP_INFO = 'appinfo.txt'
TEMP_FILE = 'tempfile.txt'

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"

PROXY = 'http://10.3.100.207:8080'

def init_app_config():
	global CONSUMER_KEY
	global CONSUMER_SECRET
	with open(APP_INFO,'rb') as fp:
		data = fp.readlines()
		print data
		CONSUMER_KEY = data[0].rstrip('\n')
		CONSUMER_SECRET = data[1].rstrip('\n')

def init_config():
	global OAUTH_TOKEN
	global OAUTH_TOKEN_SECRET
	with open(USER_INFO,'rb') as fp:
		data = fp.readlines()
		print data
		OAUTH_TOKEN = data[0].rstrip('\n')
		OAUTH_TOKEN_SECRET = data[1].rstrip('\n')
	return