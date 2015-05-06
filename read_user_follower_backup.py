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

	saveAsJson(raw_graph,'raw_graph.json')
	saveAsJson(crawled_nodes,'crawled_nodes.json')
	return raw_graph

def get_graph_id_to_good_id_mapping(raw_graph):
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
	# id_mapping is a dictionary with key = ids used in graph and single value to new id
	# so can be used both ways
	new_graph = {}
	for node in graph:
		follow_list = graph[node]
		new_graph[id_mapping[node]] = map(lambda x:id_mapping[x],follow_list)
	return new_graph

def verify_filter(graph):
	for node in graph:
		for followed_node in graph[node]:
			if followed_node not in graph:
				print 'error here' 
				quit()

def filter_useless_nodes(graph):
	new_graph = {}
	for node in graph:
		new_graph[node] = filter(lambda followed_node:followed_node in graph,graph[node])
	return new_graph

def get_scc_graph(graph,scc):
	scc_graph = {}
	for node in scc:
		scc_graph[node] = filter(lambda followed_node:followed_node in scc,graph[node])
	return scc_graph

def save_edge_list(graph,filename):
	with open(filename,'wb') as fp:
		for node in graph:
			for followed_node in graph[node]:
				fp.write(str(node) + ' ' + str(followed_node) + '\n')
	return

def save_node_list(graph,filename):
	with open(filename,'wb') as fp:
		for node in graph:
			fp.write(str(node) + '\n')

def clean_tweet_text(tweettext):
	return tweettext.replace('|',' ').replace('\n',' ').replace('#',' ')

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

def reset_file(filename):
	with open(filename,'wb'):
		pass

def get_scc_tweets(filename,scc_graph_true_id):
	filtered_tweets = []
	with open(filename, 'rb') as csvfile:
		csv_reader = csv.reader(csvfile, delimiter='|',quotechar='\'', quoting=csv.QUOTE_MINIMAL,dialect='excel')
		
		for tweet in csv_reader:
			# time.mktime(time.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y")) # taken from net of SO user with 10k+ rep
			user_id = tweet[2]
			if(int(user_id) not in scc_graph_true_id):
				continue
			timestamp = time.mktime(time.strptime(tweet[1],"%a %b %d %H:%M:%S +0000 %Y"))
			tweet_text = clean_tweet_text(tweet[4])

			filtered_tweets = filtered_tweets + [[user_id,timestamp,tweet_text]]

	print ('total useful tweets :',len(filtered_tweets))
	reset_file('filtered_opinion.csv')
	append_tweets_to_file(filtered_tweets,'filtered_opinion.csv')

def test_using_shortest_path(graph):
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
	verify_filter(graph)
	old_id_to_good_id,good_id_to_old_id = get_graph_id_to_good_id_mapping(graph)
	new_graph = transform_graph(graph,old_id_to_good_id)

	scc_list = tarjan.tarjan(new_graph)
	print 'scclist size in graph :',len(scc_list)

	test_using_shortest_path(new_graph)

	is_subgraph_test(actual_graph,graph)
	return

def get_graph(filename):
	raw_graph = get_graph_raw(filename)
	# verify_filter(raw_graph)
	filtered_graph = filter_useless_nodes(raw_graph)
	# verify_filter(filtered_graph)
	print 'number of nodes :',len(filtered_graph)

	saveAsJson(filtered_graph,'filtered_graph.json')
	# raw_graph = None
	old_id_to_good_id,good_id_to_old_id = get_graph_id_to_good_id_mapping(filtered_graph)
	new_graph = transform_graph(filtered_graph,old_id_to_good_id)

	# test_strongly_connected(new_graph,new_graph)

	saveAsJson(old_id_to_good_id,'old_id_to_good_id.json')
	saveAsJson(good_id_to_old_id,'good_id_to_old_id.json')

	saveAsJson(new_graph,'new_graph.json')

	# filtered_graph = None

	scc_list = tarjan.tarjan(new_graph)

	scc_list.sort(key = lambda x:len(x),reverse = True)

	saveAsJson(scc_list,'scc_list.txt')

	max_scc = max(scc_list,key = lambda x:len(x))

	print ('max_scc size ',len(max_scc))

	saveAsJson(max_scc,'max_scc.json')

	scc_graph = get_scc_graph(new_graph,max_scc)

	saveAsJson(scc_graph,'scc_graph.json')
	scc_graph_true_id = transform_graph(scc_graph,good_id_to_old_id)
	saveAsJson(scc_graph_true_id,'scc_graph_true_id.json')
	print 'size of max scc graph : ',len(scc_graph_true_id)

	save_node_list(scc_graph_true_id,'nodelist.txt')
	save_edge_list(scc_graph_true_id,'edgelist.txt')

	filtered_graph = None
	scc_graph = None
	new_graph = None
	old_id_to_good_id = None
	good_id_to_old_id = None

	get_scc_tweets('tweets_ultron.csv',scc_graph_true_id)

	test_strongly_connected(scc_graph_true_id,raw_graph)

# get_graph_raw('user_follow_graph_backup.txt')

def get_remaining_users_to_crawl():
	crawled_nodes = loadJsonObject('crawled_nodes.json')
	nodes_to_crawl = loadJsonObject('users_to_crawl.txt')

	crawled_set = set(crawled_nodes)


	remaining_to_crawl = []

	for node_info in nodes_to_crawl:
		node_id = node_info[0]
		if int(node_id) not in crawled_set:
			remaining_to_crawl = remaining_to_crawl + [node_info]

	saveAsJson(remaining_to_crawl,'users_to_crawl.txt')


get_graph('user_follow_graph_backup.txt')

# must be followed after get_graph if required to run
# get_remaining_users_to_crawl()