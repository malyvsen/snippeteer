import yaml

from pathlib import Path
from GithubCrawler import GithubCrawler


def main():
    crawler = GithubCrawler(config["access_token"])

    # Crawl all public repos.
    crawler.crawl_repos(start_id=config["start_id"], limit=config["limit"])

    # Retrieve the result from specified queries
    crawler.perform_searches(config["queries"], page_limit=config["page_limit"])


if __name__ == "__main__":
    config = yaml.load(Path("config.yaml").read_text(), Loader=yaml.SafeLoader)
    main()
