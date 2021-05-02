from elasticsearch import Elasticsearch

from queries import *

INDEX_NAME = 'index'

class Search:

	def __init__(self):
		self.elasticsearch = self.connect_elasticsearch()
		self.res = None

	@staticmethod
	def connect_elasticsearch():
		_es = None
		_es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
		if not _es.ping():
			raise Exception('Elasticsearch is not connected')
		return _es

	@staticmethod
	def __prepare_and_filters(dependencies):
		ret = []
		for d in dependencies:
			ret.append({"terms": {"dependencies.keyword": [d]}})
		return ret

	def __process_query(self, text, dependencies_contains, dependencies_not_contains, boolean_dependencies,
	                    any_dependencies):
		if any_dependencies:
			body = query_not_contain_any.copy()
			body['query']['bool']['must']['multi_match']['query'] = text
		elif dependencies_contains and dependencies_not_contains:
			if boolean_dependencies == 'or':
				body = query_contain_or_and_not_contain.copy()
				body['query']['bool']['must']['multi_match']['query'] = text
				body['query']['bool']['filter']['terms']['dependencies.keyword'] = dependencies_contains
				body['query']['bool']['must_not']['terms']['dependencies.keyword'] = dependencies_not_contains
			else:
				body = query_contain_and_and_not_contain.copy()
				body['query']['bool']['must']['multi_match']['query'] = text
				body['query']['bool']['filter'] = self.__prepare_and_filters(dependencies_contains)
				body['query']['bool']['must_not']['terms']['dependencies.keyword'] = dependencies_not_contains
		elif dependencies_contains:
			if boolean_dependencies == 'or':
				body = query_contains_dependencies_or.copy()
				body['query']['bool']['must']['multi_match']['query'] = text
				body['query']['bool']['filter']['terms']['dependencies.keyword'] = dependencies_contains
			else:
				body = query_contains_dependencies_and.copy()
				body['query']['bool']['must']['multi_match']['query'] = text
				body['query']['bool']['filter'] = self.__prepare_and_filters(dependencies_contains)
		elif dependencies_not_contains:
			body = query_not_contain.copy()
			body['query']['bool']['must']['multi_match']['query'] = text
			body['query']['bool']['must_not']['terms']['dependencies.keyword'] = dependencies_not_contains
		else:
			body = query_just_text.copy()
			body['query']['multi_match']['query'] = text

		return body

	def search(self, text, dependencies_contains, dependencies_not_contains, boolean_dependencies="or",
	           no_dependencies=False):
		query = self.__process_query(text, dependencies_contains, dependencies_not_contains, boolean_dependencies,
		                             no_dependencies)
		self.res = self.elasticsearch.search(index=INDEX_NAME, body=query)
		return self.res

	# As example, delete at some point
	def print_top(self, n=10):
		print("Got %d Hits:" % self.res['hits']['total']['value'])
		# pprint(res['hits']['hits'][4])

		bests = self.res['hits']['hits'][:n]
		# bests = sorted(bests, key=lambda k: k["_score"] ** 2 + (k["_source"]['star_count']), reverse=True)

		for i, hit in enumerate(bests):
			name = hit["_source"]['name']
			docstring = hit["_source"]['docstring']
			dependencies = hit["_source"]['dependencies']
			print(f"name: {name}")
			print(f"docstring: {docstring}")
			print(f"dependencies: {dependencies}")
			print(f"score is {hit['_score']} tfidf and sorted {hit['_score'] ** 2 + hit['_source']['star_count']}")
			if not i:
				print("source code")
				print(hit["_source"]['code'])
			print("*********************")


if __name__ == '__main__':
	search = Search()
	query = "quicksort"
	dependencies = []
	not_contains = []
	search.search(query, dependencies, not_contains, boolean_dependencies='or', no_dependencies=False)
	search.print_top()
