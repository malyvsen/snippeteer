import math
from urllib.parse import unquote

from elasticsearch import Elasticsearch
from flask import Flask, render_template, request, url_for

app = Flask(__name__)
es = Elasticsearch()


@app.route("/", methods=["GET"])
def index():
    def parse_filter(term):
        key, value = term[:term.index(":")], term[term.index(":") + 1:]
        exclude = key.startswith("!")
        exact = value.startswith("=")
        return key[int(exclude):], value[int(exact):], exclude, exact

    page = max(1, request.args.get("p", 1, type=int))
    min_stars = max(0, request.args.get("s", 0, type=int))
    max_ops = max(0, request.args.get("o", 1000, type=int))
    terms = unquote(request.args.get("q", "", type=str)).split()

    # Extract free text query and filters
    filters, free_text_query = [], []
    for term in terms:
        if ":" in term:
            parsed_filter = parse_filter(term)
            if len(parsed_filter[1]) > 0:
                filters.append(parsed_filter)
                continue
        free_text_query.append(term)
    free_text_query = " ".join(free_text_query)

    # Create query and search
    query, applied_filters = create_query(free_text_query, filters, min_stars, max_ops)
    results = es.search(body={"query": query}, from_=(page - 1) * 10, size=10)

    # Parse results
    num_pages = math.ceil(results["hits"]["total"]["value"] / 10)
    parsed_results = list(map(lambda result: result["_source"], results["hits"]["hits"]))

    prev_page_url = url_for("index", q=request.args.get("q"), p=max(page - 1, 1), s=min_stars, o=max_ops)
    next_page_url = _url = url_for("index", q=request.args.get("q"), p=min(page + 1, num_pages), s=min_stars, o=max_ops)
    first_page_url = url_for("index", q=request.args.get("q"), p=1, s=min_stars, o=max_ops)
    return render_template("index.html", query=free_text_query, filters=applied_filters, results=parsed_results,
                           prev=prev_page_url, next=next_page_url, first=first_page_url, page=page, num_pages=num_pages,
                           min_stars=min_stars, max_ops=max_ops)


def create_query(free_text_query, filters, min_stars, max_ops):
    query = {
        "function_score": {
            "query": {
                "bool": {
                    "must": [{"multi_match": {
                        "query": free_text_query,
                        "fields": ["name^5", "search_name^5", "docstring^4", "arguments^3", "returns^2", "keywords"]
                    }}],
                    "filter": [{"range": {"star_count": {"gte": min_stars}}},
                               {"range": {"num_operations": {"lte": max_ops}}}],
                    "must_not": []
                },
            },
            "script_score": {
                "script": {
                    "source": "_score * Math.max(0.1, Math.log(1 + doc['star_count'].value) - 0.2 * Math.log(1 + doc['num_operations'].value))"
                }
            },
            "boost_mode": "replace"
        }
    }

    applied_filters = []
    for field, value, exclude, exact in filters:
        if exact:
            item = {"term": {f"{field}.keyword": {"value": value}}}
        else:
            item = {"wildcard": {f"{field}": {"value": f"*{value}*"}}}

        query["function_score"]["query"]["bool"]["must_not" if exclude else "filter"].append(item)
        applied_filters.append({"key": field, "value": value, "exclude": exclude, "exact": exact})
    return query, applied_filters


if __name__ == "__main__":
    app.run()
