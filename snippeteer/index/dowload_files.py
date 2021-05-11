import base64
import multiprocessing
import os
import pickle
import sqlite3
import time
import urllib.error
import urllib.error
import urllib.request
import urllib.request
import zipfile

from tqdm import tqdm


# inspired by https://github.com/facebookresearch/Neural-Code-Search-Evaluation-Dataset/blob/master/download.py

def parallel_download(array, function, n_cores=None):
	if n_cores == 1:
		return [function(x, y, i) for x, y, i in tqdm(array)]
	with tqdm(total=len(array)) as pbar:

		def update(*args):
			pbar.update()

		if n_cores is None:
			n_cores = multiprocessing.cpu_count()
			print(f"using {n_cores} cores")
		with multiprocessing.Pool(processes=n_cores) as pool:
			jobs = [
				pool.apply_async(function, (x, y, i), callback=update) for x, y, i in array
			]
			results = [job.get() for job in jobs]
		return results


def download_project(url, default_branch, repo_id):
	zip_url = url.strip()
	zip_url = f"{zip_url}/archive/{default_branch}.zip"

	# get only username/projectname, replace / with @
	username_projectname = "/".join(zip_url.strip().split("/")[3:5])
	zipfile_name = username_projectname.replace("/", "@") + ".zip"
	entries = []
	try:
		urllib.request.urlretrieve(zip_url, zipfile_name)
	except urllib.error.URLError:
		return entries

	try:
		with zipfile.ZipFile(zipfile_name, "r") as f:
			for file in f.infolist():
				if os.path.splitext(file.filename)[1] == ".py":
					dest_file = "/".join(file.filename.split("/")[1:])
					name_file = dest_file.split("/")[-1]

					url_dest = f"{url}/blob/master/{dest_file}"
					download_url = f"https://raw.githubusercontent.com/{username_projectname}/{default_branch}/{dest_file}"
					content = f.read(file.filename)
					content = base64.b64encode(content)
					entries.append((name_file, repo_id, url_dest, content, download_url))

		os.remove(zipfile_name)
	except Exception:
		os.remove(zipfile_name)

	return entries


def create_list_urls():
	dics = []  # just in case there are repetead repositories
	repos = {}
	urls = []
	repos_db = []
	path = "../../data"
	for file in os.listdir(path):
		if file.endswith(".pkl"):
			with open(os.path.join(path, file), "rb") as f:
				dics.append(pickle.load(f))

	for d in dics:
		repos = {**repos, **d}

	for id, v in repos.items():
		url = (v['html_url'], v['default_branch'], id)
		urls.append(url)

		aux = (id, v['repo_name'], v['owner'], v['html_url'], int(v['fork_count']), int(v['star_count'])
		       , int(v['contributor_count']), int(v['collaborator_count']))
		repos_db.append(aux)

	return urls, repos_db

def handle_sql_tables(cur):
	cur.execute(
		"""CREATE TABLE IF NOT EXISTS "Repositories" ("repo_id" INTEGER, "name" TEXT, "owner" TEXT, "url" TEXT,
		"fork_count" INTEGER, "star_count" INTEGER, "contributor_count"	INTEGER,"collaborator_count" INTEGER, 
		PRIMARY KEY("repo_id"))""""")
	cur.execute(
		"""CREATE TABLE IF NOT EXISTS Files ("Name" TEXT, "repo_id" INTEGER, "url" TEXT, "content" BLOB, 
		"download_url"	TEXT, FOREIGN KEY("repo_id") REFERENCES Repositories("repo_id"))""")

def main():
	start_time = time.time()

	db = sqlite3.connect('../../data/files.db')

	urls, repos_db = create_list_urls()

	print(f"list created, there is {len(urls)}repos")

	cur = db.cursor()

	handle_sql_tables(cur)

	cur.executemany("INSERT INTO Repositories VALUES (?, ? ,?, ?, ?, ?, ?, ?)", repos_db)

	entries = parallel_download(urls, download_project)

	entries = [item for sublist in entries for item in sublist]

	cur.executemany("INSERT INTO Files VALUES (?, ? ,?, ?, ?)", entries)
	db.commit()
	db.close()

	print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == '__main__':
	main()
