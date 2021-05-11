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


if __name__ == '__main__':
	es = connect_elasticsearch()
	populate_index(es)
