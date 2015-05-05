import json
import tarjan

def saveAsJson(A,filename):
	with open(filename,'wb') as fp:
		json.dump(A,fp,indent = 4)

def loadJsonObject(filename):
	with open(filename,'r') as fp:
		return json.loads(fp.read())

def get_graph_raw(filename):
	raw_graph = {}
	with open(filename,'rb') as fp:
		for line in fp:
			if('*' in line):
				continue
			node_adjacency = json.loads(line)
			user_id = node_adjacency[0]
			follow_list = node_adjacency[1]
			user_id_long = int(user_id)
			follow_list_long = map(lambda x:int(x),follow_list)
			# print follow_list_long
			# print user_id_long
			raw_graph[user_id_long] = follow_list_long

	saveAsJson(raw_graph,'raw_graph.json')
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


def get_graph(filename):
	raw_graph = get_graph_raw(filename)
	# verify_filter(raw_graph)
	filtered_graph = filter_useless_nodes(raw_graph)
	# verify_filter(filtered_graph)
	print 'number of nodes :',len(filtered_graph)

	saveAsJson(filtered_graph,'filtered_graph.json')
	raw_graph = None
	old_id_to_good_id,good_id_to_old_id = get_graph_id_to_good_id_mapping(filtered_graph)
	new_graph = transform_graph(filtered_graph,old_id_to_good_id)

	saveAsJson(old_id_to_good_id,'old_id_to_good_id.json')
	saveAsJson(good_id_to_old_id,'good_id_to_old_id.json')

	saveAsJson(new_graph,'new_graph.json')

	filtered_graph = None

	scc_list = tarjan.tarjan(new_graph)

	scc_list.sort(key = lambda x:len(x),reverse = True)

	saveAsJson(scc_list,'scc_list.txt')

	max_scc = max(scc_list,key = lambda x:len(x))

	saveAsJson(max_scc,'max_scc.json')

# get_graph_raw('user_follow_graph_backup.txt')
get_graph('user_follow_graph_backup.txt')