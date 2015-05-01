from TwitterSearch import *
import config
import csv

def clean_tweet_text(tweettext):
	return tweettext.replace('|',' ').replace('\n',' ')

def append_tweets_to_file(tweet_list):
	with open(config.TWEET_STORAGE_SHEET, 'ab') as csvfile:
		csvwriter = csv.writer(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		for tweet in tweet_list:
			# print tweet
			csvwriter.writerow(tweet)

def get_recent_tweets(keywords,since_id = None):
	max_id = 0
	tweets_retrieved = 0
	tweetresults = []
	try:
		tso = TwitterSearchOrder() # create a TwitterSearchOrder object
		tso.set_keywords(['ultron']) # let's define all words we would like to have a look for
		# tso.set_language('de') # we want to see German tweets only
		tso.set_include_entities(False) # and don't give us all those entity information
		# it's about time to create a TwitterSearch object with our secret tokens
		if (since_id is not None):
			tso.set_since_id(long(since_id))

		print 'Consumer KEY = ',config.CONSUMER_KEY
		print 'Consumer Secret = ',config.CONSUMER_SECRET
		print 'OAUTH_TOKEN = ',config.OAUTH_TOKEN
		print 'OAUTH_TOKEN_SECRET = ',config.OAUTH_TOKEN_SECRET,
		
		ts = TwitterSearch(consumer_key = config.CONSUMER_KEY,consumer_secret = config.CONSUMER_SECRET ,access_token = config.OAUTH_TOKEN,access_token_secret = config.OAUTH_TOKEN_SECRET,proxy=config.PROXY)
		print 'here\n'
		# this is where the fun actually starts :)
		for tweet in ts.search_tweets_iterable(tso):
			# print( '@%s %s tweeted: %s' % ( str(i), tweet['user']['screen_name'], tweet['text'].encode('ascii', 'ignore') ) )
			tweetresults = tweetresults + [[	
				str(tweet['id']),
				str(tweet['created_at']),
				str(tweet['user']['id']),
				str(tweet['user']['screen_name']),
				str(clean_tweet_text(tweet['text'].encode('ascii', 'ignore')))	
			]]
			max_id = max(max_id,int(tweet['id']))
			tweets_retrieved = tweets_retrieved + 1
			if(tweets_retrieved  % 100 == 0):
				print ('tweets retrieved till now : ' + str(tweets_retrieved))
				append_tweets_to_file(tweetresults)
				tweetresults = []
	except TwitterSearchException as e:
		print(e)
	except Exception as e:
		print e
	return max_id,tweets_retrieved

def reset_tweetfile():
	with open(config.TWEET_STORAGE_SHEET,'wb'):
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

tester()