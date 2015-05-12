import json
import tarjan
import time
import csv

def get_crawled_nodes():
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
	print str(len(raw_graph)) + ' nodes crawled'
	saveAsJson(crawled_nodes,'data/crawled_nodes.json')


def get_remaining_users_to_crawl():
	crawled_nodes = loadJsonObject('data/crawled_nodes.json')
	nodes_to_crawl = loadJsonObject('data/users_to_crawl.txt')

	crawled_set = set(crawled_nodes)



	remaining_to_crawl = []

	for node_info in nodes_to_crawl:
		node_id = node_info[0]
		if int(node_id) not in crawled_set:
			remaining_to_crawl = remaining_to_crawl + [node_info]

	print str(len(crawled_nodes)) + ' out of ' + str(len(nodes_to_crawl)) + ' done'
	print str(len(remaining_to_crawl)) + ' nodes remaining !'
	saveAsJson(remaining_to_crawl,'data/users_to_crawl.txt')

get_crawled_nodes('user_follow_graph_backup.txt')
get_remaining_users_to_crawl()
