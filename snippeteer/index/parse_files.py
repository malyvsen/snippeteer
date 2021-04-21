import base64
import multiprocessing
import sqlite3
import traceback

from tqdm import tqdm

from snippeteer.parse.source_file import SourceFile


def parallel_function(array, function, n_cores=None):
    if n_cores == 1:
        return [function(x) for x in tqdm(array)]
    with tqdm(total=len(array)) as pbar:

        if n_cores is None:
            n_cores = multiprocessing.cpu_count()
        with multiprocessing.Pool(processes=n_cores) as pool:
            jobs = [
                pool.apply_async(function, x) for x in array
            ]
            results = [job.get() for job in jobs if job.get() is not None]
        return results


def make(content):
    try:
        file_data = base64.b64decode(content).decode("utf-8")
        if file_data == '': return None
    except:
        return None
    try:
        return SourceFile.from_code(file_data)
    except:
        return None


def non_parallel(files):
    values = []
    for i, (name, content) in enumerate(files):
        if not (i % 1000): print(f"iteration {i}")
        try:
            file_data = base64.b64decode(content).decode("utf-8")
            if file_data == '':
                continue
        except:
            continue
        try:
            values.append(SourceFile.from_code(file_data))
        except:
            print(f"new exception {i}")
            traceback.print_exc()
    return values


def main(parallel=True):
    db = sqlite3.connect('../../../files.db')

    cur = db.cursor()

    cur.execute("SELECT content FROM Files")

    files = cur.fetchall()

    if parallel:
        values = parallel_function(files, make)
    else:
        values = non_parallel(files)

    functions = 0
    variables = 0
    modules = 0
    total_functions = 0
    for v in values:
        if len(v.functions) > 0:
            functions += 1
            total_functions += len(v.functions)
        if len(v.imports.modules) > 0:
            variables += 1
        if len(v.imports.variables) > 0:
            modules += 1

    print(functions, variables, modules)


if __name__ == "__main__":
    main()
