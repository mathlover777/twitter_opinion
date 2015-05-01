from __future__ import unicode_literals
import requests
from requests_oauthlib import OAuth1
import time
import pause
import config
import math
from urlparse import parse_qs



def get_resetinfo_friends_list(oauth):
	url_call = config.BASE_URL+"/1.1/application/rate_limit_status.json?resources=friends"
	status_code = 429
	r = None
	while(status_code == 429):
		r = make_call(url_call,oauth)
		# print r
		status_code = r.status_code
		if int(status_code) != 429:
			break
		time.sleep(10)
	
	response_json = r.json()
	reset = response_json['resources']['friends']['/friends/ids']['reset']
	limit = response_json['resources']['friends']['/friends/ids']['limit']
	remaining = response_json['resources']['friends']['/friends/ids']['remaining']

	return (reset,limit,remaining)

def wait_for_friends_list_reset(oauth):
	(reset,limit,remaining) = get_resetinfo_friends_list(oauth)
	current_time = int(time.time())
	reset_time = int(reset)

	if(reset_time > current_time):
		print 'current time = ',current_time,'reset_time = ',reset_time
		pause.until(reset_time) # wait upto that time plus 1 minute

	return

def make_call(url_call,oauth):
	success = False
	waittime = 1
	while(not success):
		try:
			r = requests.get(url=url_call, auth=oauth)
			if (r.status_code == 200 or r.status_code == 429):
				success = True
			else:
				print ('unknown code ! = '+ r.starus_code)
		except Exception as e:
			print e
			print ('request timed out waiting for ' + str(waittime) + ' seconds...')
			time.sleep(waittime)
			waittime = waittime * 2
	return r

def get_temporary_friendlist(url_call,oauth):
	success = False
	friend_list_id = []
	next_cursor = -1
	while(not success):	
		r = make_call(url_call,oauth)
		# print r
		if (r.status_code == 200):
			# call request successful
			response_json = r.json()
			friend_list_id = response_json['ids']
			next_cursor = response_json['next_cursor']
			# print 'next cursor = ',next_cursor
			success = True
		elif (r.status_code == 429):
			print('rate limit exceeded waiting for reset')
			wait_for_friends_list_reset(oauth)
		else:
			# unknown status code
			print ('unknown status code ! = ' + str(r.status_code))
			wait_for_friends_list_reset(oauth)
	# print 'next cursor = here',next_cursor
	return (friend_list_id,next_cursor)



############################## To BE USED FROM OUTSIDE #####################################################
def get_friend_list(user_id,screen_name,oauth,maxFriend = 5000):
	# maxFriend is rounded upto the next 5000
	cursor = -1
	friend_list_id_complete = []
	maxCount = int(math.ceil(float(maxFriend)/float(5000)))
	count = 0
	while cursor != 0 and count <maxCount:
		url_call = config.BASE_URL + '/1.1/friends/ids.json?' + 'screen_name='+screen_name+'&'+'user_id='+user_id+'&cursor='+str(cursor)
		print url_call
		(friend_list_id,cursor) = get_temporary_friendlist(url_call,oauth)
		# print friend_list_id
		# print cursor
		friend_list_id_complete = friend_list_id_complete + friend_list_id
		print('making next call with cursor = ',str(cursor))
		count = count + 1
		# break
	return friend_list_id_complete

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

def get_oauth(CONSUMER_KEY,CONSUMER_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET):
	oauth = OAuth1(CONSUMER_KEY,client_secret=CONSUMER_SECRET,resource_owner_key=OAUTH_TOKEN,resource_owner_secret=OAUTH_TOKEN_SECRET)
	return oauth

#####################################################################################################

def tester(user_id,screen_name):
	oauth = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN,config.OAUTH_TOKEN_SECRET)

	friendlist = get_friend_list(user_id,screen_name,oauth,100000)

	# print ('user id = ' + user_id)
	# print ('screen_name = ' + screen_name)
	# print ('following list = ',friendlist)
	with open("output.txt","wb") as fp:
		for follow_id in friendlist:
			fp.write(str(follow_id) + '\n')

	return

# user_id = '359965206'
# screen_name = 'derinbadrasli'

# user_id = '545918705'
# screen_name = 'XL_ReTweeT'

# tester(user_id,screen_name)

