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

def get_oauth(CONSUMER_KEY,CONSUMER_SECRET,OAUTH_TOKEN,OAUTH_TOKEN_SECRET):
	oauth = OAuth1(CONSUMER_KEY,client_secret=CONSUMER_SECRET,resource_owner_key=OAUTH_TOKEN,resource_owner_secret=OAUTH_TOKEN_SECRET)
	return oauth

def clean_tweet_text(tweettext):
	return tweettext.replace('|',' ').replace('\n',' ').replace('\r',' ')

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
	return

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
	config.init_app_config()
	config.init_user_config()
	token_list = config.USER_TOKEN_LIST

	print 'trying to get oauth for ' + str(len(token_list)) + ' users'

	oauth_list = map(lambda x:get_oauth(config.CONSUMER_KEY,config.CONSUMER_SECRET,x[0],x[1]),token_list)

	print 'oauth successful !'

	reset_file(config.TWEET_STORAGE_SHEET)
	get_all_tweets('MayweatherPacquiao','2015-04-29','2015-05-08',oauth_list,config.TWEET_STORAGE_SHEET)
	# tweets will come from 2015-04-27(incl) to exactly before 2015-05-03 
	# please maintain the format 

test_get_all_tweets()