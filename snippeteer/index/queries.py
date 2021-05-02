# Any filter, gives more importance to the fields (not really sure how much it effects de ^x)
# most_fields: Finds documents which match any field and combines the _score from each field

query_just_text = {
	"query": {
		"multi_match": {
			"query": "",
			"type": "most_fields",
			"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
		},
	},
}

# Shows results that contain at least one of the dependencies

query_contains_dependencies_or = {
	"query": {
		"bool": {
			"must": {
				"multi_match": {
					"query": "",
					"type": "most_fields",
					"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
				}
			},
			"filter": {
				"terms": {
					"dependencies.keyword": [],
				}
			},
		}
	}
}

# Shows results that contain ALL the dependencies

query_contains_dependencies_and = {
	"query": {
		"bool": {
			"must": {
				"multi_match": {
					"query": "",
					"type": "most_fields",
					"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
				}
			},
			"filter": [
				{
					"terms": {
						"dependencies.keyword": [],
					}
				},
				{
					"terms": {
						"dependencies.keyword": [],
					}
				},
			]
		}
	}
}


# Shows results not containing any of the dependencies given

query_not_contain = {
	"query": {
		"bool": {
			"must": {
				"multi_match": {
					"query": "",
					"type": "most_fields",
					"fields": ["name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
				}
			},
			"must_not": {
				"terms": {
					"dependencies.keyword": [],
				}
			}
		}
	}
}

# Shows results that contain ALL the dependencies and not containing any of the dependencies given

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
					"dependencies.keyword": [],
				}
			},
			"must_not": {
				"terms": {
					"dependencies.keyword": [],
				}
			}
		}
	}
}

# Shows results that contain at least one of the dependencies and not containing any of the dependencies given

query_contain_and_and_not_contain = {
	"query": {
		"bool": {
			"must": {
				"multi_match": {
					"query": "",
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

# Shows results that do not contain ANY dependencies

query_not_contain_any = {
	"query": {
		"bool": {
			"must": {
				"multi_match": {
					"query": "",
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
