import twitter_helper
import config

def authenticate():
	config.init_app_config()
	token, secret = twitter_helper.setup_oauth()
	print "OAUTH_TOKEN: " + token
	print "OAUTH_TOKEN_SECRET: " + secret

	with open(config.USER_INFO,'wb') as fp:
		fp.write(token + '\n')
		fp.write(secret + '\n')

	print 'these will be saved in userdata.txt and will be used in init_config'

	return

authenticate()