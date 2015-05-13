import json
import tarjan
import time
import csv
import networkx as nx

def saveAsJson(A,filename):
	with open(filename,'wb') as fp:
		json.dump(A,fp,indent = 4)

def loadJsonObject(filename):
	with open(filename,'r') as fp:
		return json.loads(fp.read())

def get_graph_raw(filename):
	raw_graph = {}
	crawled_nodes = []
	with open(filename,'rb') as fp:
		for line in fp:
			if('*' in line):
				continue
			node_adjacency = json.loads(line)
			user_id = node_adjacency[0]
			follow_list = node_adjacency[1]
			user_id_long = int(user_id)
			follow_list_long = map(lambda x:int(x),follow_list)
			crawled_nodes = crawled_nodes + [user_id_long]
			# print follow_list_long
			# print user_id_long
			if user_id_long in raw_graph:
				print 'repeating nodes in backup graph'
			raw_graph[user_id_long] = follow_list_long

	saveAsJson(raw_graph,'data/raw_graph.json') # this is the graph that we have got by parsing the 
	# user_follow backup file with original twitter ids
	# saveAsJson(crawled_nodes,'crawled_nodes.json')
	return raw_graph

def get_graph_id_to_good_id_mapping(raw_graph):
	# this code takes graph with ids as any integrs and retuns a mapping with new ids in range [1,#nodes]
	# old_id_to_good_id is <old_id = orinial tweeter user id, new normalized id>
	# good_id_to_old_id <new id,old original id>	
	i = 1
	old_id_to_good_id = {}
	good_id_to_old_id = {}
	# for node in raw_graph:
	# 	if (node not in old_id_to_good_id):
	# 		old_id_to_good_id[node] = i
	# 		good_id_to_old_id[i] = node
	# 		i = i + 1
	# print 'here'
	print len(raw_graph)
	for node in raw_graph:
		follow_list = raw_graph[node]
		for graph_node in [node] + follow_list:
			if graph_node not in raw_graph :
				print 'error'
				quit()
			if (graph_node not in old_id_to_good_id):
				old_id_to_good_id[graph_node] = i
				good_id_to_old_id[i] = graph_node
				i = i + 1

	return (old_id_to_good_id,good_id_to_old_id)

def transform_graph(graph,id_mapping):
	# id_mapping is of the form <id (in graph), new id>
	# id_mapping is a dictionary with key = ids used in graph and single value to new id
	# so can be used both ways
	new_graph = {}
	for node in graph:
		follow_list = graph[node]
		new_graph[id_mapping[node]] = map(lambda x:id_mapping[x],follow_list)
	return new_graph

def verify_filter(graph):
	# test code
	for node in graph:
		for followed_node in graph[node]:
			if followed_node not in graph:
				print 'error here' 
				quit()

def filter_useless_nodes(graph):
	# test code
	new_graph = {}
	for node in graph:
		new_graph[node] = filter(lambda followed_node:followed_node in graph,graph[node])
	return new_graph

def get_scc_graph(graph,scc):
	# creates the scc given the nodes in the scc
	scc_graph = {}
	for node in scc:
		scc_graph[node] = filter(lambda followed_node:followed_node in scc,graph[node])
	return scc_graph

def save_edge_list(graph,filename):
	# save the graph as edge_list <node, followed node> note its a flat list
	with open(filename,'wb') as fp:
		for node in graph:
			for followed_node in graph[node]:
				fp.write(str(node) + ' ' + str(followed_node) + '\n')
	return

def save_node_list(graph,filename):
	# the flat list of node ids
	with open(filename,'wb') as fp:
		for node in graph:
			fp.write(str(node) + '\n')

def clean_tweet_text(tweettext):
	# do all tweet text clearing here
	return tweettext.replace('|',' ').replace('\n',' ').replace('#',' ').replace('\r',' ')

def append_tweets_to_file(tweet_list,file_to_store = None):
	# code to append tweet to file
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

def get_scc_tweets(filename,scc_graph_true_id):
	# get the extract tweets for users in scc
	filtered_tweets = []
	with open(filename, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		
		for tweet in csv_reader:
			# time.mktime(time.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y")) # taken from net of SO user with 10k+ rep
			user_id = tweet[2]
			if(int(user_id) not in scc_graph_true_id):
				continue
			timestamp = int(time.mktime(time.strptime(tweet[1],"%a %b %d %H:%M:%S +0000 %Y")))
			tweet_text = clean_tweet_text(tweet[4])

			filtered_tweets = filtered_tweets + [[user_id,timestamp,tweet_text]]

	print ('total useful tweets :',len(filtered_tweets))
	reset_file('data/filtered_opinion.csv') # tweets for users in scc
	# format same as tweets.csv file
	append_tweets_to_file(filtered_tweets,'data/filtered_opinion.csv')

def test_using_shortest_path(graph):
	# test code
	print 'nx test begins'
	G = nx.DiGraph()
	for node in graph:
		G.add_node(node)
	for node in graph:
		for followed_node in graph[node]:
			G.add_edge(node,followed_node)

	# test part
	for x in G:
		for y in G:
			if not nx.has_path(G,x,y):
				print 'not scc ',x,' ', y
				return

	print 'test with networks successful'
	return

def is_subgraph_test(graph,max_scc_graph):
	# test code
	print 'size of graph ',len(graph)
	print 'size of max scc',len(max_scc_graph)

	for node in max_scc_graph:
		actual_set = set(graph[node])
		for followed_node in max_scc_graph[node]:
			if followed_node not in actual_set:
				print 'not subgraph ',node,' ',followed_node
				return
	print 'subgraph test successful'
	return

def test_strongly_connected(graph,actual_graph):
	# test code
	verify_filter(graph)
	old_id_to_good_id,good_id_to_old_id = get_graph_id_to_good_id_mapping(graph)
	new_graph = transform_graph(graph,old_id_to_good_id)

	scc_list = tarjan.tarjan(new_graph)
	print 'scclist size in graph :',len(scc_list)

	test_using_shortest_path(new_graph)

	is_subgraph_test(actual_graph,graph)
	return

def get_graph(filename,tweet_file):
	# get everything given the user_follow backup file and the original tweet file

	raw_graph = get_graph_raw(filename)
	# verify_filter(raw_graph)
	filtered_graph = filter_useless_nodes(raw_graph)
	# verify_filter(filtered_graph)
	print 'number of nodes :',len(filtered_graph)

	saveAsJson(filtered_graph,'data/filtered_graph.json') # the graph with removed user ids
	# raw_graph = None
	old_id_to_good_id,good_id_to_old_id = get_graph_id_to_good_id_mapping(filtered_graph)

	# test_strongly_connected(new_graph,new_graph)

	saveAsJson(old_id_to_good_id,'data/old_id_to_good_id.json') # the mapping original id --> good id
	saveAsJson(good_id_to_old_id,'data/good_id_to_old_id.json') # the mapping good id --> original id

	new_graph = transform_graph(filtered_graph,old_id_to_good_id)
	saveAsJson(new_graph,'data/new_graph.json') # the filtered graph according to the new good id

	# filtered_graph = None

	scc_list = tarjan.tarjan(new_graph) # using tarjan's algorithm to do the scc partition

	scc_list.sort(key = lambda x:len(x),reverse = True)

	saveAsJson(scc_list,'data/scc_list.txt') # the scc list according the good id

	max_scc = max(scc_list,key = lambda x:len(x))

	print ('max_scc size ',len(max_scc))

	saveAsJson(max_scc,'data/max_scc.json') # max scc according to good id

	scc_graph = get_scc_graph(new_graph,max_scc) 

	saveAsJson(scc_graph,'data/scc_graph.json') # the max extracted scc graph [good id]
	scc_graph_true_id = transform_graph(scc_graph,good_id_to_old_id)
	saveAsJson(scc_graph_true_id,'data/scc_graph_true_id.json') # the max scc graph with original id
	print 'size of max scc graph : ',len(scc_graph_true_id)

	save_node_list(scc_graph_true_id,'data/nodelist.txt') # nodelist of scc original id
	save_edge_list(scc_graph_true_id,'data/edgelist.txt') # edge list of scc original id

	filtered_graph = None
	scc_graph = None
	new_graph = None
	old_id_to_good_id = None
	good_id_to_old_id = None

	get_scc_tweets(tweet_file,scc_graph_true_id) # saving the extracted tweets in 
	# 'data/filtered_opinion.csv'

	test_strongly_connected(scc_graph_true_id,raw_graph) # the test code ... may be disabled if required

get_graph('data/user_follow_graph_backup.txt','data/tweets.csv')
