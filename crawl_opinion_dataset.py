from TwitterSearch import *
import config
import csv
import calendar
import time

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
			# print tweet
			csvwriter.writerow(tweet)
selectUser = 1
def get_recent_tweets(keywords,since_id = None,max_id = None,until = None,max_tweet_count = None,file_to_store = None):
	global selectUser
	print 'keywords',keywords
	print 'since_id ',since_id
	print 'max_id ',max_id
	print 'until ',until
	print 'max_tweet_count ',max_tweet_count
	print 'file_to_store ',file_to_store
	max_id_retrieved = None
	tweets_retrieved = 0
	least_id_retrieved = None
	tweetresults = []
	last_id = None
	if(max_id is not None):
		last_id = max_id
	try:
		tso = TwitterSearchOrder() # create a TwitterSearchOrder object
		tso.set_keywords(keywords) # let's define all words we would like to have a look for
		# tso.set_language('de') # we want to see German tweets only
		tso.set_include_entities(False) # and don't give us all those entity information
		# it's about time to create a TwitterSearch object with our secret tokens
		if (since_id is not None):
			print 'setting since id ',since_id
			tso.set_since_id(long(since_id))
		if(max_id is not None):
			print 'setting max_id ',max_id
			tso.set_max_id(long(max_id))
		if(until is not None and max_id is None):
			print 'setting until ',until
			tso.set_until(until)
		# print 'Consumer KEY = ',config.CONSUMER_KEY
		# print 'Consumer Secret = ',config.CONSUMER_SECRET
		# print 'OAUTH_TOKEN = ',config.OAUTH_TOKEN
		# print 'OAUTH_TOKEN_SECRET = ',config.OAUTH_TOKEN_SECRET,
		if(selectUser == 1):
			ts = TwitterSearch(consumer_key = config.CONSUMER_KEY,consumer_secret = config.CONSUMER_SECRET ,access_token = config.OAUTH_TOKEN1,access_token_secret = config.OAUTH_TOKEN_SECRET1,proxy=config.PROXY)
		else:
			ts = TwitterSearch(consumer_key = config.CONSUMER_KEY,consumer_secret = config.CONSUMER_SECRET ,access_token = config.OAUTH_TOKEN,access_token_secret = config.OAUTH_TOKEN_SECRET,proxy=config.PROXY)
		# print 'here\n'
		# this is where the fun actually starts :)
		for tweet in ts.search_tweets_iterable(tso):
			if(max_tweet_count is not None):
				if (max_tweet_count == tweets_retrieved):
					break
			# print( '@%s %s tweeted: %s' % ( str(i), tweet['user']['screen_name'], tweet['text'].encode('ascii', 'ignore') ) )
			if(last_id == None):
				last_id = long(tweet['id']) + long(1)
				curr_id = long(tweet['id'])
			else:
				curr_id = long(tweet['id'])
				if(curr_id == last_id):
					continue
				if(curr_id > last_id):
					print 'repeation in single call'
					print 'curr id ',curr_id,'last_id ',last_id
					break
			if(max_id is not None):
				if(curr_id > max_id):
					break
			tweetresults = tweetresults + [[
				str(tweet['id']),
				str(tweet['created_at']),
				str(tweet['user']['id']),
				str(tweet['user']['screen_name']),
				str(clean_tweet_text(tweet['text'].encode('ascii', 'ignore')))	
			]]
			last_id = long(tweet['id'])
			# updating the max id
			if(max_id_retrieved is None):
				max_id_retrieved = long(tweet['id'])
			else:
				max_id_retrieved = max(max_id_retrieved,long(tweet['id']))
			# updating the min_id
			if(least_id_retrieved is None):
				least_id_retrieved = long(tweet['id'])
			else:
				least_id_retrieved = min(least_id_retrieved,long(tweet['id']))
			# updating the retrival counter
			tweets_retrieved = tweets_retrieved + 1
			# if 100 tweets retrieved dump them
			if(tweets_retrieved  % 100 == 0):
				# print ('tweets retrieved till now : ' + str(tweets_retrieved))
				if(max_id is not None):
					tweetresults = filter(lambda t:long(t[0]) < long(max_id),tweetresults)
				append_tweets_to_file(tweetresults,file_to_store)
				tweetresults = []
	except TwitterSearchException as e:
		print 'Twitter exception'
		print(e)
		if(e.code == 429):
			print 'too many requests waiting for 3 mins'
			time.sleep(180)
	except Exception as e:
		print 'other exception'
		print e
	# dump tweets if buffer is not empty
	if(tweets_retrieved == 0 and max_id is not None):
		print 'resetting .. did nothing in this loop !'
		max_id_retrieved = max_id -long(1)
		least_id_retrieved = max_id -long(1)
	if (len(tweetresults) > 0):
		if(max_id is not None):
			tweetresults = filter(lambda t:long(t[0]) < long(max_id),tweetresults)
		append_tweets_to_file(tweetresults,file_to_store)
		tweetresults = []
	return max_id_retrieved,least_id_retrieved,tweets_retrieved

def reset_tweetfile():
	reset_file(config.TWEET_STORAGE_SHEET)
	return

def reset_file(filename):
	with open(filename,'wb'):
		pass

def tester():
	reset_tweetfile()
	config.init_app_config()
	config.init_config()
	max_id,tweets_retrieved = get_recent_tweets(['ultron'],long(594202492830879700))

	print('total ' + str(tweets_retrieved) + ' tweets retrieved !')
	print('max_id =' + str(max_id))

	print('\n')

	with open(config.EXTRACT_INFO,'wb') as fp:
		fp.write(str(max_id) + '\n')

# tester()
# max_id Returns results with an ID less than (that is, older than) or equal to the specified ID.
# since_id Returns results with an ID greater than (that is, more recent than) the specified ID.

def get_tweets(keywords,start_date,end_date):
	global selectUser
	selectUser = 0
	reset_tweetfile()
	config.init_app_config()
	config.init_config()
	# YYYY-MM-DD --- format of untill
	# getting a tweet before the start date
	reset_file(config.TEMP_FILE)
	# get_recent_tweets(keywords,since_id = None,max_id = None,until = None,max_tweet_count = None,file_to_store = None)
	before_start_max_id,before_start_least_id,before_start_tweets_retrieved = get_recent_tweets(keywords,None,None,start_date,1,config.TEMP_FILE)

	print ('max Tweet ID before Start = (approx) ',before_start_max_id)

	least_id = None
	total_retrieved = 0
	trial_count = 1
	while(True):
		# get_recent_tweets(keywords,since_id = None,
		# max_id = None,until = None,max_tweet_count = None,file_to_store = None)
		max_id,least_id,retrieved = get_recent_tweets(keywords,before_start_max_id,
			least_id,end_date,None,config.TWEET_STORAGE_SHEET)
		selectUser = (selectUser + 1 )%2
		print 'least id returned ',least_id
		if(max_id is None or max_id == 0):
			print 'max_id return became 0 or None ',max_id
			quit()
		if(least_id is not None):
			least_id = least_id - long(1)
		total_retrieved = total_retrieved + retrieved
		print 'Trial ',trial_count,'Retrieved ',retrieved, 'Total_Retrieved ',total_retrieved
		print 'max_id ',max_id,'least_id ',least_id
		if(least_id <= before_start_max_id and least_id is not None):
			break
		trial_count = trial_count + 1
	print 'crawl finished'
	return
# get_tweets('2015-03-20','2015-03-30')
# get_tweets(['worldcup'],calendar.datetime.date(2015,4,30),calendar.datetime.date(2015,3,30))
get_tweets(['ultron'],calendar.datetime.date(2015,4,27),calendar.datetime.date(2015,5,3))