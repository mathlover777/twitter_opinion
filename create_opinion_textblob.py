import csv
import re
from textblob import TextBlob
import json


def saveAsJson(A,filename):
	with open(filename,'wb') as fp:
		json.dump(A,fp,indent = 4)

def loadJsonObject(filename):
	with open(filename,'r') as fp:
		return json.loads(fp.read())

def clean_tweet(tweet_text):
	# use this for all tweet cleaning
	tweet_text.replace('|',' ').replace('\n',' ').replace('#',' ')
	ascii_text = re.sub(r'[^\x00-\x7F]+',' ', tweet_text) # removal of non ascii characters
	url_removed_text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ascii_text)
	# inline urls removed
	stripped_text = re.sub(' +',' ',url_removed_text)

	if(len(stripped_text) <= 3):
		final_text = 'tweet'
	else:
		final_text = stripped_text

	return stripped_text

def get_sentiment_score_textblob(tweet_text):
	blob = TextBlob(tweet_text)
	return blob.sentiment.polarity


def create_opinion_file_using_textblob(tweet_file,output_file):
	with open(tweet_file,'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		with open(output_file,'wb') as fp:
			for tweet in csv_reader:
				user_id = tweet[0]
				timestamp = tweet[1]
				tweet_text = clean_tweet(tweet[2])

				sentiment_score = get_sentiment_score_textblob(tweet_text)

				fp.write(str(user_id) + ' ' + str(timestamp) + ' ' + str(sentiment_score) + '\n')
	return

create_opinion_file_using_textblob('data/filtered_opinion.csv','data/opinion.txt')

