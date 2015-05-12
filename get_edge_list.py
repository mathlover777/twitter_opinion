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

def get_edge_list(filename,output_filename):
	graph = loadJsonObject(filename)
	with open(output_filename,'wb') as fp: 
		for node in graph:
			for followed_node in graph[node]:
				fp.write(str(node) + ' ' + str(followed_node) + '\n')
	return

get_edge_list('new_graph.json','edge_list.txt')