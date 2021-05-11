# Data Processing

The data is being extracted from the Github API, where this crawler has two option:
- Extracting the information of all public repositories.
- Extracting repositories that are retrieved by queries given to the Github Search API.

Note: In order to use the crawling functionality an access token from https://github.com/settings/tokens should be placed in ``config.yml`` at ``access_token``.

### Extracting all public repositories

To extract all repositories, the following function should be run: 
```
crawler.crawl_repos(start_id=config["start_id"], limit=config["limit"])
```
 where the `start_id` is the id of the repository where crawling should start and `limit` is the maximum number of 
 repositories that should be processed.
 
### Extracting repositories based on queries

In order to scrape all result returned from specified queries the following line should be executed: 

```
crawler.perform_searches(config["queries"], page_limit=config["page_limit"])  
```

where `queries` are the queries to be executed and should be specified in the ``config.yml`` file and the `page_limit`
is the number of pages returned from the query.
