# INPUT the tweet file in the following format
# tweet_id | twitter_time_stamp (in twitter format)| user_id | user_screen_name | tweet
# next line again similar
# while fetching \n and | is removed from tweet text if found
# so no worry
# and none of them will contain the '|'



import json
import csv
import operator
import sys

def saveAsJson(A,filename):
	with open(filename,'wb') as fp:
		json.dump(A,fp,indent = 4)

def loadJsonObject(filename):
	with open(filename,'r') as fp:
		return json.loads(fp.read())

def get_count_statistics(tweet_count):
	tweet_count_to_user_count = {} # number of tweets --> # number of users
	# not cumulative .. absotlute count
	for user in tweet_count:
		if(tweet_count[user] in tweet_count_to_user_count):
			tweet_count_to_user_count[tweet_count[user]] = tweet_count_to_user_count[tweet_count[user]] + 1
		else:
			tweet_count_to_user_count[tweet_count[user]] = 1
	sorted_list = sorted(tweet_count_to_user_count.items(), key=operator.itemgetter(0),reverse = True)
	# sorted list has <tweet_count,user_count> sorted by tweet_count large to small
	cum_sorted_list = []
	already_counted = 0
	for pair in sorted_list:
		count = pair[0]
		number_of_users = pair[1]
		already_counted = already_counted + number_of_users
		cum_sorted_list = cum_sorted_list + [[count,already_counted]]

	saveAsJson(sorted_list,'sorted_stat.txt') # sorted list has <tweet_count,user_count> sorted by tweet_count large to small
	saveAsJson(cum_sorted_list,'cum_sorted_stat.txt') # the sorted list in cumulative manner

def get_user_distribution(filename):
	# print 'here'
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
	saveAsJson(user_id_screen_name_mapping,'user_id_screen_name_mapping.txt') # <user_id,tweet_count>
	user_id_screen_name_mapping = None
	print 'total uniquie users = ',len(tweet_count),' out of total ',num_of_tweets,' tweets !'
	sorted_tweet_count = sorted(tweet_count.items(), key=operator.itemgetter(1),reverse=True)
	saveAsJson(sorted_tweet_count,'sorted_tweet_count.txt') # <user_id,tweet_count> sorted by tweet_count
	sorted_tweet_count = []
	get_count_statistics(tweet_count)

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

def analyze(tweet_file,min_tweet_count):
	# get_user_distribution(config.TWEET_STORAGE_SHEET)
	print 'tweet file = ',tweet_file
	print 'min tweet count = ',min_tweet_count
	get_user_distribution(tweet_file)
	get_users_to_crawl(min_tweet_count)

analyze(sys.argv[1],int(sys.argv[2]))