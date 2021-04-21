from pathlib import Path
import sqlite3
from tqdm.auto import tqdm
from .try_parse import try_parse


connection = sqlite3.connect(Path(__file__).parent.parent.parent / "data" / "files.db")
contents = list(connection.cursor().execute("SELECT content FROM files"))
source_files = [
    source_file
    for (content,) in tqdm(contents, desc="Parsing source files")
    if (source_file := try_parse(content)) is not None
]
functions = [
    function for source_file in source_files for function in source_file.functions
]
print(
    f"{len(source_files)}/{len(contents)} parsed successfully, {len(functions)} functions in total"
)
