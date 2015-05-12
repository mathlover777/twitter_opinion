import numpy
# import matplotlib.mlab as mlab
# import matplotlib.pyplot as plt

def create_histogram(opinion_values,num_bins):
	histogram = numpy.histogram(opinion_values,num_bins,)
	
	count_list = histogram[0]
	bucket_list = histogram[1]



	return zip(bucket_list,count_list)


def create_opinion_sentiment_value_list(filename):
	sentiment_list = []
	with open(filename,'rb') as fp:
		for line in fp:
			sentiment_value = float(line.split()[2])
			sentiment_list = sentiment_list + [sentiment_value]
	return sentiment_list

sentiment_list = create_opinion_sentiment_value_list('data/opinion.txt')
histogram = create_histogram(sentiment_list,20)
print histogram