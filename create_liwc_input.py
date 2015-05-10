import csv
import re
def tweet_count(tweet_file):
	with open(tweet_file,'rb') as fp:
		print 'line count = ',len(fp.readlines())

def create_liwc_input(tweet_file,liwc_file):
	with open(tweet_file,'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		count = 0
		with open(liwc_file,'wb') as fp:
			for tweet in csv_reader:
				count = count + 1
				# print tweet
				tweet_text = tweet[2]
				ascii_text = re.sub(r'[^\x00-\x7F]+',' ', tweet_text)
				# url_removed_text = re.sub(r'^https?:\/\/.*[\r\n]*', '', ascii_text, flags=re.MULTILINE)
				# url_removed_text = re.sub(r'^http?:\/\/.*[\r\n]*', '', url_removed_text, flags=re.MULTILINE)
				url_removed_text = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', ascii_text)
				# print tweet_text

				url_removed_text = re.sub(' +',' ',url_removed_text)
				if(len(url_removed_text) == 1):
					url_removed_text = 'tweet'
				if(len(url_removed_text) == 0):
					url_removed_text = 'tweet'
				fp.write(url_removed_text + '\n\n\n')
		print 'count : ',count

def create_opinion_file(tweet_file,liwc_value_file,outputfile):
	count = 0
	with open(tweet_file,'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		with open(liwc_value_file,'rb') as liwc_reader:
			with open(outputfile,'wb') as output_pointer:
				for tweet in csv_reader:
					user_id = tweet[0]
					timestamp = tweet[1]
					sentiment = float(liwc_reader.readline())

					line = str(user_id) + ' ' + str(timestamp) + ' ' + str(sentiment)

					output_pointer.write(line + '\n')
			
					count = count + 1
	print 'total ' + str(count) + ' tweets managed'

create_opinion_file('filtered_opinion.csv','sent.txt','opinion.txt')

# tweet_count('filtered_opinion.csv')
# create_liwc_input('filtered_opinion.csv','liwc_input.txt')
