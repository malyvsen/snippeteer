import base64
import multiprocessing
import sqlite3
import traceback

from tqdm import tqdm

from snippeteer.parse.source_file import SourceFile


def parallel_function(array, function, n_cores=None):
	if n_cores == 1:
		return [function(x, y) for x, y, z in tqdm(array)]
	with tqdm(total=len(array)) as pbar:

		def update(*args):
			pbar.update()

		if n_cores is None:
			n_cores = multiprocessing.cpu_count()
		with multiprocessing.Pool(processes=n_cores) as pool:
			jobs = [
				pool.apply_async(function, (x, y, z, w), callback=update) for x, y, z, w in array
			]
			results = [job.get() for job in jobs if job.get() is not None]
		return results


def make(rowid, content, url, star_count):
	try:
		file_data = base64.b64decode(content).decode("utf-8")
		if file_data == '': return None
	except:
		return None
	try:
		return SourceFile.from_code(file_data), rowid, url, file_data.split('\n'), star_count
	except:
		return None


def non_parallel(files):
	values = []
	for i, (rowid, content, url, star_count) in enumerate(files):
		if not (i % 1000): print(f"iteration {i}")
		try:
			file_data = base64.b64decode(content).decode("utf-8")
			if file_data == '':
				continue
		except:
			continue
		try:
			aux = (SourceFile.from_code(file_data), rowid, url, file_data.split('\n'), star_count)
			values.append(aux)
		except:
			print(f"new exception {i}")
			traceback.print_exc()
	return values


def get_contents():
	db = sqlite3.connect('../../data/files.db')

	cur = db.cursor()

	query = "SELECT f.rowid, f.content, f.url, r.star_count  FROM Files as f inner join Repositories as r on f.repo_id == r.repo_id"
	cur.execute(query)

	files = cur.fetchall()

	return parallel_function(files, make)
