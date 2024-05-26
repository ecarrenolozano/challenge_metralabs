
import os

from pathlib import Path

import shutil

import sys


data_path = Path(sys.argv[1])

new_path = Path(data_path.__str__() + '_part2')

files = data_path.glob('**/*')

split_at = int(sys.argv[2])

print("Splitting at", split_at)

for file_path in files:

    if file_path.is_dir():
        continue

    timestamp = int(os.path.basename(file_path.__str__())[:19])

    if timestamp >= split_at:
        new_file_path = file_path.__str__().replace(data_path.__str__(), new_path.__str__())

        Path(new_file_path).parent.mkdir(parents=True, exist_ok=True)

        shutil.move(file_path.__str__(), new_file_path)