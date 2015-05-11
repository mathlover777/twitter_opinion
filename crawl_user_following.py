import requests
from requests_oauthlib import OAuth1
import time
import pause
import config
import math
from urlparse import parse_qs
import pprint
import csv
import operator
import json
import random

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
			if (r.status_code == 200 or r.status_code == 429 or r.status_code == 401):
				success = True
			else:
				print ('unknown code ! = '+ str(r.status_code))
		except Exception as e:
			print e
			print ('request timed out waiting for ' + str(waittime) + ' seconds...')
			time.sleep(waittime)
			waittime = waittime + 2
	return r

def reset_file(filename):
	with open(filename,'wb'):
		pass

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
		elif (r.status_code == 401):
			print('private user')
			friend_list_id = []
			next_cursor = 0
			success = True
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
		# print url_call
		(friend_list_id,cursor) = get_temporary_friendlist(url_call,oauth)
		# print friend_list_id
		# print cursor
		friend_list_id_complete = friend_list_id_complete + friend_list_id
		# print('making next call with cursor = ',str(cursor))
		count = count + 1
		# break
	return friend_list_id_complete

def get_oauth(CONSUMER_KEY,CONSUMER_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET):
	oauth = OAuth1(CONSUMER_KEY,client_secret=CONSUMER_SECRET,resource_owner_key=OAUTH_TOKEN,resource_owner_secret=OAUTH_TOKEN_SECRET)
	return oauth
def saveAsJson(A,filename):
	with open(filename,'wb') as fp:
		json.dump(A,fp,indent = 4)

def loadJsonObject(filename):
	with open(filename,'r') as fp:
		return json.loads(fp.read())

def get_follow_list():

	config.init_app_config()
	config.init_user_config()

	token_list = config.USER_TOKEN_LIST

	print 'trying to get oauth for ' + str(len(token_list)) + ' users'

	oauth_list = map(lambda x:get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,x[0],x[1]),token_list)

	# print map(lambda x:x.to_string(),oauth_list)

	print 'oauth successful !'
	

	reset_file('data/user_follow_graph_backup.txt')

	users_to_crawl = loadJsonObject('data/users_to_crawl.txt')
	user_follow_graph = {}
	trial = 0
	for user in users_to_crawl:
		user_id = user[0]
		screen_name = user[1]
		follow_list = get_friend_list(user_id,screen_name,oauth_list[trial],5000)
		# trial = (trial + 1)%len(oauth_list)
		trial = random.randint(0,len(oauth_list) - 1)
		user_follow_graph[user_id] = follow_list
		single_user_data = (user_id,follow_list)
		single_user_data_json = json.dumps(single_user_data)
		with open('data/user_follow_graph_backup.txt','ab') as fp:
			fp.write('*******************\n')
			fp.write(single_user_data_json)
			fp.write('\n')
	saveAsJson(user_follow_graph,'data/user_follow_graph.txt')

get_follow_list()