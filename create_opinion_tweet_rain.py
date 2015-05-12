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

def get_sentiment_score_tweet_rain(vocab_dict,tweet_text):
	# print dict
	blob = TextBlob(tweet_text)
	word_list = [word for word in blob.words]

	# print words

	pScore = 0.0
	nScore = 0.0
	count = 0
	for word in word_list:
		if word in vocab_dict:
			count = count + 1
			scores = vocab_dict[word]
			pScore = pScore + float(scores[0])
			nScore = nScore + float(scores[1])
			# print word
	if (count == 0):
		return None
	return (pScore - nScore) / (pScore + nScore)
	


def create_opinion_file_using_tweet_rain(tweet_file,output_file):
	vocab_dict = loadJsonObject('token_sentiment_dict.json')
	total_count = 0
	bad_count = 0
	with open(tweet_file,'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		with open(output_file,'wb') as fp:
			for tweet in csv_reader:
				total_count = total_count + 1
				user_id = tweet[0]
				timestamp = tweet[1]
				tweet_text = clean_tweet(tweet[2])

				sentiment_score = get_sentiment_score_tweet_rain(vocab_dict,tweet_text)
				if sentiment_score is None:
					bad_count = bad_count + 1
					continue
				fp.write(str(user_id) + ' ' + str(timestamp) + ' ' + str(sentiment_score) + '\n')
	print 'bad tweets :',float(bad_count)/float(total_count) * 100.0
	return

create_opinion_file_using_tweet_rain('data/filtered_opinion.csv','data/opinion.txt')

