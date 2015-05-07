import csv
import re


def create_liwc_input(tweet_file,liwc_file):
	with open(tweet_file,'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		count = 0
		with open(liwc_file,'wb') as fp:
			for tweet in csv_reader:
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
				count = count + 1
				fp.write(url_removed_text + '\n\n\n')
		




create_liwc_input('filtered_opinion.csv','liwc_input.txt')
