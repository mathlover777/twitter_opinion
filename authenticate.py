import twitter_helper

def authenticate():
	token, secret = setup_oauth()
	print "OAUTH_TOKEN: " + token
	print "OAUTH_TOKEN_SECRET: " + secret

	with open('userdata.txt','wb') as fp:
		data.write(token + '\n')
		data.write(secret + '\n')

	print 'these will be saved in userdata.txt and will be used in init_config'

	return

authenticate()