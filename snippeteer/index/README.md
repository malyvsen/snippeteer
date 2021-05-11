### Downloading the python files

It downloads all the python files in parallel of the extracted repositories that are stored in the `data` folder. It store all the content as well as the relevant information of the repositories in the 'files.db'

-Run `python download_files.py`

### Indexing to ElasticSearch
It uses the Python Parser in parallel over all the files avaibles in `files.db`, it creates a collection documents for each function and store this collection to ElasticSearch.

- Start the ElasticSearch instance with its default settings.
- Run `python create_index.py`

An ElasticSearch document is:
```
			Document = {
				"name": Name of the function,
				"docstring": Docstring of the function,
				"first_line": Line where the function starts,
				"last_line": Line where the function ends,
				"code": Complete code of the function,
				"url": URL of the github file,
				"star_count": Number of starts of the repository,
				"keywords": Keywords of the function,
				"arguments": Aruments of the function,
				"dependencies": Dependencies of the function,
				"num_operations": Number of operations that the function uses,
				"returns": Return of the function,
			}
```
