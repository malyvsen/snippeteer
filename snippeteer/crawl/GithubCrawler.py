import requests
import json
import pickle
import time

from typing import Any, Dict, Tuple
from time import sleep


class GithubCrawler:
    def __init__(self, token):
        self.access_token = token
        self.header = {"Authorization": f"token {self.access_token}"}
        self.repo_info = {}
        self.language = "Python"
        self.query_url = "https://api.github.com/repositories"

    def find_repo(self, repo_url: str) -> Any:
        r = requests.get(repo_url, headers=self.header)
        if r.status_code == 200:
            r = json.loads(r.text)
            return r
        else:
            return None

    def store_repo_info(self, response: Dict) -> None:
        """Find and store information for each repo in repsonse"""
        for repo in response:
            if repo["fork"] is False and self.language_match(repo):

                fork_count, star_count, default_branch = self.get_repo_specific_info(repo)

                self.repo_info[repo["id"]] = {
                    "repo_name": get_repo_name(repo),
                    "owner": get_owner_login(repo),
                    "html_url": get_html_url(repo),
                    "repo_url": get_repo_url(repo),
                    "fork_count": fork_count,
                    "star_count": star_count,
                    "default_branch": default_branch,
                    "contributor_count": self.get_contributor_count(repo),
                    "collaborator_count": self.get_collaborator_count(repo),
                }

    def crawl_repos(self, start_id=0, limit=100) -> None:

        params = {"since": start_id}
        r = requests.get("https://api.github.com/repositories",
                         headers=self.header, params=params)
        repo_counter = 0
        while "next" in r.links and repo_counter < limit:
            nr = int(r.links["next"]["url"].split("=")[-1])
            r = requests.get(r.links["next"]["url"], headers=self.header)
            if r.status_code == 200:
                r_json = json.loads(r.text)
                self.store_repo_info(r_json)
                repo_counter += len(r_json)

                if repo_counter % 1000 == 0 and repo_counter > 0:
                    # Save current info to file
                    save_obj(self.repo_info, file_name=f"crawled_info/dictionary_{nr}")
                    self.repo_info.clear()
            else:
                self.check_sleep()

            if "next" not in r.links:
                params = {"since": nr + 100}
                r = requests.get("https://api.github.com/repositories",
                                 headers=self.header, params=params)

    def perform_searches(self, queries, page_limit=5):
        """Retrieve the """
        for query in queries:
            i = 0
            r = requests.get(f"https://api.github.com/search/repositories?q={query}", headers=self.header)
            while r.status_code == 200 and i < page_limit:

                print(f"Query: {query}, page: {i}")
                # Process query results.
                r_json = json.loads(r.text)
                # print(r_json)
                self.store_query_info(r_json)

                if "next" in r.links:
                    r = requests.get(r.links["next"]["url"], headers=self.header)
                    i += 1
                else:
                    break

                if r.status_code != 200:
                    self.check_sleep()

            save_obj(self.repo_info, file_name=f"crawled_info/query_{query}")
            self.repo_info.clear()

    def store_query_info(self, response: Dict) -> None:
        """Find and store information for each repo in repsonse"""
        for repo in response["items"]:
            if repo["fork"] is False and self.language_match(repo):

                fork_count, star_count, default_branch = self.get_repo_specific_info(repo)

                self.repo_info[repo["id"]] = {
                    "repo_name": get_repo_name(repo),
                    "owner": get_owner_login(repo),
                    "html_url": get_html_url(repo),
                    "repo_url": get_repo_url(repo),
                    "fork_count": fork_count,
                    "star_count": star_count,
                    "default_branch": default_branch,
                    "contributor_count": self.get_contributor_count(repo),
                    "collaborator_count": self.get_collaborator_count(repo),
                }

    def get_repo_specific_info(self, repo: Dict) -> Tuple[int, int, None]:
        if "url" in repo:
            r = self.find_repo(repo["url"])
        else:
            return 0, 0, None
        if not r:
            return 0, 0, None

        fork_count = r["forks_count"] if "forks_count" in r else 0
        star_count = r["watchers_count"] if "watchers_count" in r else 0
        default_branch = r["default_branch"] if "default_branch" in r else None
        #  """https://developer.github.com/changes/2012-09-05-watcher-api/"""

        return fork_count, star_count, default_branch

    def get_repo_info(self):
        return self.repo_info

    def get_languages(self, language_url: str):
        r = requests.get(language_url, headers=self.header)
        if r.status_code == 200:
            r = json.loads(r.text)
            return r
        else:
            return None

    def language_match(self, repo: Dict) -> bool:
        if "language" in repo:
            if repo["language"] == self.language:
                return True
        if "languages_url" in repo:
            language_dict = self.get_languages(repo["languages_url"])
            if language_dict and self.language in language_dict:
                return True

        return False

    def get_contributor_count(self, repo: Dict) -> int:
        if "contributors_url" in repo:
            r = requests.get(
                repo["contributors_url"] + "?per_page=1", headers=self.header
            )
            if "last" in r.links:
                return int(r.links["last"]["url"].split("=")[-1])
        return 0

    def get_collaborator_count(self, repo: Dict) -> int:
        if "collaborators_url" in repo:
            r = requests.get(
                repo["collaborators_url"] + "?per_page=1", headers=self.header
            )
            if "last" in r.links:
                return int(r.links["last"]["url"].split("=")[-1])
        return 0

    def check_rate_limit(self):
        url = 'https://api.github.com/rate_limit'
        r = requests.get(url, headers=self.header)
        r = json.loads(r.text)
        return r["rate"]["remaining"], r["rate"]["reset"]

    def check_sleep(self):
        remaining, reset_time = self.check_rate_limit()
        if remaining == 0:
            wait_time = (reset_time - int(time.time())) // 60 + 1
            print(f"Going to sleep for {wait_time} minutes..")
            sleep(wait_time)


def get_repo_name(repo: Dict):
    return repo["name"] if "name" in repo else None


def get_owner_login(repo: Dict):
    return (
        repo["owner"]["login"] if "owner" in repo and "login" in repo["owner"] else None
    )


def get_html_url(repo: Dict):
    return repo["html_url"] if "html_url" in repo else None


def get_repo_url(repo: Dict):
    return repo["url"] if "url" in repo else None


def save_obj(dict_, file_name ):
    with open(file_name + '.pkl', 'wb') as f:
        pickle.dump(dict_, f, pickle.HIGHEST_PROTOCOL)
