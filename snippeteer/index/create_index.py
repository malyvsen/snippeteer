from elasticsearch import Elasticsearch, helpers

from parse_files import get_contents
from snippeteer.parse.names import split_name

INDEX_NAME = 'index'


def connect_elasticsearch():
	_es = None
	_es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
	if not _es.ping():
		raise Exception('Elasticsearch is not connected')
	return _es


def create_data(values):
	for v, id, url, content, star_count in values:
		for f in v.functions:

			docstring = "" if f.docstring is None else f.docstring
			try:
				if isinstance(docstring, bytes):
					docstring = docstring.decode()
				elif not isinstance(docstring, str):
					docstring = str(docstring)
			except:
				docstring = ""

			code = '\n'.join(content[f.first_line: f.last_line])

			yield {
				"_index": INDEX_NAME,
				"name": f.name,
				"search_name": ' '.join(split_name(f.name)),
				"docstring": docstring,
				"first_line": f.first_line,
				"last_line": f.last_line,
				"db_id": id,
				"code": code,
				"url": url,
				"star_count": star_count,
				"keywords": list(f.keywords),
				"arguments": list(f.arguments),
				"dependencies": list(f.dependencies),
				"num_operations": f.num_operations,
				"returns": list(f.returns),
			}


def populate_index(es):
	es.indices.delete(index=INDEX_NAME, ignore=[400, 404])
	es.indices.create(index=INDEX_NAME, ignore=400)
	values = get_contents()
	helpers.bulk(es, create_data(values))


def test_search(es):
	query_just_text = {
		"query": {
			"multi_match": {
				"query": "merge two lists",
				"type": "most_fields",
				"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
			},
		},
	}

	query_contains_dependencies_or = {
		"query": {
			"bool": {
				"must": {
					"multi_match": {
						"query": "quicksort",
						"type": "most_fields",
						"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
					}
				},
				"filter": {
					"terms": {
						"dependencies.keyword": ["numpy", "pandas.core.dtypes.missing"],
					}
				},
			}
		}
	}

	query_contains_dependencies_and = {
		"query": {
			"bool": {
				"must": {
					"multi_match": {
						"query": "quicksort",
						"type": "most_fields",
						"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
					}
				},
				"filter": [
					{
						"terms": {
							"dependencies.keyword": ["numpy"],
						}
					},
					{
						"terms": {
							"dependencies.keyword": ["pandas.core.dtypes.missing"],
						}
					},
				]
			}
		}
	}

	query_not_contain = {
		"query": {
			"bool": {
				"must": {
					"multi_match": {
						"query": "quicksort",
						"type": "most_fields",
						"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
					}
				},
				"must_not": {
					"terms": {
						"dependencies.keyword": ["random", "numpy"],
					}
				}
			}
		}
	}

	query_contain_or_and_not_contain = {
		"query": {
			"bool": {
				"must": {
					"multi_match": {
						"query": "quicksort",
						"type": "most_fields",
						"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
					}
				},
				"filter": {
					"terms": {
						"dependencies.keyword": ["numpy", 'pandas.core.dtypes.missing'],
					}
				},
				"must_not": {
					"terms": {
						"dependencies.keyword": ["random"],
					}
				}
			}
		}
	}


	query_contain_and_and_not_contain = {
		"query": {
			"bool": {
				"must": {
					"multi_match": {
						"query": "quicksort",
						"type": "most_fields",
						"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
					}
				},
				"filter": [
					{
						"terms": {
							"dependencies.keyword": ["numpy"],
						}
					},
					{
						"terms": {
							"dependencies.keyword": ["pandas.core.dtypes.missing"],
						}
					},
				],
				"must_not": {
					"terms": {
						"dependencies.keyword": ["random"],
					}
				}
			}
		}
	}


	query_not_contain_any = {
		"query": {
			"bool": {
				"must": {
					"multi_match": {
						"query": "quicksort",
						"type": "most_fields",
						"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
					}
				},
				"must_not": {
					"exists": {
						"field": "dependencies",
					}
				}
			}
		}
	}

	# score function:
	# tf-idf stars,

	res = es.search(index="index", body=query_not_contain_any)
	print("Got %d Hits:" % res['hits']['total']['value'])
	# pprint(res['hits']['hits'][4])

	bests = res['hits']['hits'][:10]
	bests = sorted(bests, key=lambda k: k["_score"]**2 + (k["_source"]['star_count']), reverse=True)

	for i, hit in enumerate(bests):
		name = hit["_source"]['name']
		docstring = hit["_source"]['docstring']
		dependencies = hit["_source"]['dependencies']
		print(f"name: {name}")
		print(f"docstring: {docstring}")
		print(f"dependencies: {dependencies}")
		print(f"score is {hit['_score']} tfidf and sorted {hit['_score']**2 + hit['_source']['star_count']}")
		if not i:
			print("source code")
			print(hit["_source"]['code'])
		print("*********************")
		if i == 4:
			break


if __name__ == '__main__':
	es = connect_elasticsearch()
	populate_index(es)