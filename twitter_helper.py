# from __future__ import unicode_literals
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

def clean_tweet_text(tweettext):
	return tweettext.replace('|',' ').replace('\n',' ')

def append_tweets_to_file(tweet_list,file_to_store = None):
	filename = ''
	if(file_to_store is None):
		filename = config.TWEET_STORAGE_SHEET
	else:
		filename = file_to_store
	with open(filename, 'ab') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		for tweet in tweet_list:
			string_tweet = map(lambda x:str(x),tweet)
			# print tweet
			csvwriter.writerow(string_tweet)
def reset_file(filename):
	with open(filename,'wb'):
		pass

def get100TweetsbeforethisTweetID(keyword,since_id,max_id,oauth):
	url_call = config.BASE_URL + "/1.1/search/tweets.json?q=" + keyword + "&count=100&since_id="+str(since_id) + "&max_id="+str(max_id)
	# print url_call
	try:
		r = make_call(url_call,oauth)
	except Exception as e:
		print(e)
		# unable do nothing
		return ([],max_id,1)
	if (r.status_code == 429):
		print 'rate limited'
		return ([],max_id,2)
	response = r.json()
	tweet_list = []
	# print 'count = ',len(response['statuses'])
	for tweet in response['statuses']:
		tweet_id = tweet['id']
		tweet_created_at = tweet['created_at']
		tweet_text = clean_tweet_text(tweet['text'].encode('ascii', 'ignore'))
		tweet_user_id = tweet['user']['id']
		tweet_user_screen_name = tweet['user']['screen_name']
		tweet_list = tweet_list + [[tweet_id,tweet_created_at,tweet_user_id,tweet_user_screen_name,tweet_text]]
	# pprint.pprint (tweet_list)
	min_id = 0
	# print map(lambda x:x[0],tweet_list)
	if (len (tweet_list) == 0):
		return [],min_id,3
	min_id = min(map(lambda x:x[0],tweet_list))
	# print type(min_id)
	# print min_id
	return tweet_list,min_id,3

def get_all_tweets_by_id(keyword,since_id,max_id,oauth_list,filename):
	trial = 0
	user_count = len(oauth_list)
	while(True):
		tweet_list,min_retrieved,flag = get100TweetsbeforethisTweetID(keyword,since_id,max_id,oauth_list[trial])
		trial = (trial + 1)%user_count
		if (min_retrieved == 0):
			break
		if (len(tweet_list) > 0 and flag == 3): 
			append_tweets_to_file(tweet_list,filename)
			max_id = min_retrieved - 1
			continue
		if (flag == 2):
			# rate limited do whatever
			print 'waiting for 5 minutes'
			time.sleep(300)
			continue
		# nothing to do if flag 1
		pass
	return
def get_tweet_before_date(keyword,date,oauth):
	# this will never fail, if required wait
	# "/1.1/search/tweets.json?q=ultron&until=2015-04-28"
	url_call = config.BASE_URL + "/1.1/search/tweets.json?q=ultron&until=" + date
	while(True):
		try:
			r = make_call(url_call,oauth)
			if(r.status_code == 429):
				continue
			response = r.json()
			count = len(response['statuses'])
			print str(count) + ' statuses found before the date ',date
			if (count == 0):
				return 0
			tweet = response['statuses'][0]
			tweet_id = tweet['id']
			return tweet_id
		except:
			print 'got exception while doing get_tweet_before_date trying again'
			pass



def get_all_tweets(keyword,start_date,end_date,oauth_list,filename):
	# start date is the old date
	# end date is the new date
	last_tweet = get_tweet_before_date(keyword,start_date,oauth_list[0]) # this will be the since_id
	first_tweet = get_tweet_before_date(keyword,end_date,oauth_list[0]) # this will be the max_id

	print 'start_date(old) = ',start_date,' tweet_id = ',last_tweet
	print 'end_date(new) = ',end_date,' tweet_id = ',first_tweet
	
	if(last_tweet == 0 or first_tweet == 0):
		print 'cant do job for the given dates'
		return

	get_all_tweets_by_id(keyword,last_tweet,first_tweet,oauth_list,filename)

	return

def test_get_all_tweets():
	config.init_config()
	config.init_app_config()
	oauth1 = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN,config.OAUTH_TOKEN_SECRET)
	oauth2 = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN1,config.OAUTH_TOKEN_SECRET1)

	oauth_list = [oauth1,oauth2]

	reset_file(config.TWEET_STORAGE_SHEET)
	get_all_tweets('ultron','2015-04-28','2015-05-03',oauth_list,config.TWEET_STORAGE_SHEET)
	# tweets will come from 2015-04-27(incl) to exactly before 2015-05-03 
	# please maintain the format 

# test_get_all_tweets()
#####################################################################################################
def saveAsJson(A,filename):
	with open(filename,'wb') as fp:
		json.dump(A,fp,indent = 4)

def loadJsonObject(filename):
	with open(filename,'r') as fp:
		return json.loads(fp.read())

def get_count_statistics(tweet_count):
	tweet_count_to_user_count = {}
	for user in tweet_count:
		if(tweet_count[user] in tweet_count_to_user_count):
			tweet_count_to_user_count[tweet_count[user]] = tweet_count_to_user_count[tweet_count[user]] + 1
		else:
			tweet_count_to_user_count[tweet_count[user]] = 1
	sorted_list = sorted(tweet_count_to_user_count.items(), key=operator.itemgetter(0),reverse = True)
	cum_sorted_list = []
	already_counted = 0
	for pair in sorted_list:
		count = pair[0]
		number_of_users = pair[1]
		already_counted = already_counted + pair[1]
		cum_sorted_list = cum_sorted_list + [[pair[0],already_counted]]

	saveAsJson(sorted_list,'sorted_stat.txt')
	saveAsJson(cum_sorted_list,'cum_sorted_stat.txt')

def get_user_distribution(filename):
	tweet_count = {}
	user_id_screen_name_mapping = {}
	num_of_tweets = 0
	with open(filename, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		for tweet in csv_reader:
			tweet_user_id = tweet[2]
			tweet_user_screen_name = tweet[3]
			num_of_tweets = num_of_tweets + 1
			if(tweet_user_id in tweet_count):
				tweet_count[tweet_user_id] = tweet_count[tweet_user_id] + 1
			else:
				tweet_count[tweet_user_id] = 1
			if(tweet_user_id in user_id_screen_name_mapping):
				pass
			else:
				user_id_screen_name_mapping[tweet_user_id] = tweet_user_screen_name
	saveAsJson(user_id_screen_name_mapping,'user_id_screen_name_mapping.txt')
	user_id_screen_name_mapping = {}
	print('total uniquie users = ',len(tweet_count),' out of total ',num_of_tweets,' tweets !')
	sorted_tweet_count = sorted(tweet_count.items(), key=operator.itemgetter(1),reverse=True)
	saveAsJson(sorted_tweet_count,'sorted_tweet_count.txt')
	sorted_tweet_count = []
	get_count_statistics(tweet_count)

def test_get_user_distribution():
	# get_user_distribution(config.TWEET_STORAGE_SHEET)
	get_user_distribution('tweets_ultron.csv')


def get_users_to_crawl(min_tweet_count):
	sorted_tweet_count = loadJsonObject('sorted_tweet_count.txt')
	user_id_screen_name_mapping = loadJsonObject('user_id_screen_name_mapping.txt')
	users_to_crawl = []
	for user in sorted_tweet_count:
		user_id = user[0]
		user_tweet_count = user[1]

		if(user_tweet_count < min_tweet_count):
			# as list is already sorted in reverse does not need to go further
			break
		users_to_crawl = users_to_crawl + [(user_id,user_id_screen_name_mapping[user_id],user_tweet_count)]
	saveAsJson(users_to_crawl,'users_to_crawl.txt')
	print 'total '+str(len(users_to_crawl)) + ' users to crawl'
	return users_to_crawl

def get_follow_list():
	config.init_config()
	config.init_app_config()
	oauth1 = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN,config.OAUTH_TOKEN_SECRET)
	oauth2 = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN1,config.OAUTH_TOKEN_SECRET1)

	oauth_list = [oauth1,oauth2]
	

	users_to_crawl = loadJsonObject('users_to_crawl.txt')
	user_follow_graph = {}
	trial = 0
	for user in users_to_crawl:
		user_id = user[0]
		screen_name = user[1]
		follow_list = get_friend_list(user_id,screen_name,oauth_list[trial],5000)
		trial = (trial + 1)%len(oauth_list)
		user_follow_graph[user_id] = follow_list
		single_user_data = (user_id,follow_list)
		single_user_data_json = json.dumps(single_user_data)
		with open('user_follow_graph_backup.txt','ab') as fp:
			fp.write('*******************\n')
			fp.write(single_user_data_json)
			fp.write('\n')
	saveAsJson(user_follow_graph,'user_follow_graph.txt')

# need to be called together after crawling tweets ##################
# test_get_user_distribution()
# get_users_to_crawl(11)
#####################################################################
# get_users_to_crawl(600)
#################### actual follow crawler ##########################
get_follow_list()
#####################################################################

def tweet_tester():
	config.init_config()
	config.init_app_config()
	oauth1 = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN,config.OAUTH_TOKEN_SECRET)
	oauth2 = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN1,config.OAUTH_TOKEN_SECRET1)

	# get100TweetsbeforethisTweetID('ultron',592478218063638528,594616538205802497,oauth)

	max_id = 594652545894764544
	since_id = 592478218063638528
	reset_file(config.TWEET_STORAGE_SHEET)
	get_all_tweets_by_id('ultron',since_id,max_id,[oauth1,oauth2],config.TWEET_STORAGE_SHEET)

# tweet_tester()

# def tester(user_id,screen_name):
# 	oauth = get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,config.OAUTH_TOKEN,config.OAUTH_TOKEN_SECRET)

# 	friendlist = get_friend_list(user_id,screen_name,oauth,100000)

# 	# print ('user id = ' + user_id)
# 	# print ('screen_name = ' + screen_name)
# 	# print ('following list = ',friendlist)
# 	with open("output.txt","wb") as fp:
# 		for follow_id in friendlist:
# 			fp.write(str(follow_id) + '\n')

# 	return

# user_id = '359965206'
# screen_name = 'derinbadrasli'

# user_id = '545918705'
# screen_name = 'XL_ReTweeT'

# tester(user_id,screen_name)

