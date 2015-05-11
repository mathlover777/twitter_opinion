# app specific key
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
######################

# user specific key
OAUTH_TOKEN = ''
OAUTH_TOKEN_SECRET = ''
OAUTH_TOKEN1 = ''
OAUTH_TOKEN_SECRET1 = ''
#####################

########### info for set of users #######
USER_TOKEN_LIST = []
# of the format (OAUTH_TOKEN,OAUTH_TOKEN_SECRET)
#########################################

############# api constants #############################
BASE_URL = 'https://api.twitter.com'
REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHORIZE_URL = "https://api.twitter.com/oauth/authorize?oauth_token="
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"
PROXY = 'http://10.3.100.207:8080'
########################################################

########### networking constants #######################
TWEET_STORAGE_SHEET = 'data/tweets.csv'
USER_INFO = 'config_data/userdata.txt'
APP_INFO = 'config_data/appinfo.txt'
########################################################

def init_app_config():
	global CONSUMER_KEY
	global CONSUMER_SECRET
	with open(APP_INFO,'rb') as fp:
		data = fp.readlines()
		print data
		CONSUMER_KEY = data[0].rstrip('\n')
		CONSUMER_SECRET = data[1].rstrip('\n')

def init_user_config():
	global USER_TOKEN_LIST
	with open(USER_INFO) as fp:
		lines = fp.readlines()
		for i in xrange(0,len(lines),2):
			token = lines[i].rstrip('\n')
			secret = lines[i + 1].rstrip('\n')
			USER_TOKEN_LIST = USER_TOKEN_LIST + [(token,secret)]
	return
