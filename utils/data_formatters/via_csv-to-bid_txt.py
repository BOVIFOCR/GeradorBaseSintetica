import json
import os
from pathlib import Path

import pandas as pd

from paths import json_path

df = pd.read_csv('via.csv')

outpath = json_path
outpath.mkdir(exist_ok=True)

entities = json.loads(Path('files/entities.json').read_text())

for _, row in df.iterrows():
    fname = row['filename']

    shape_attrs = json.loads(row['region_shape_attributes'])
    sample_attrs = json.loads(row['region_attributes'])

    out_fpath = (outpath / (os.path.splitext(fname)[0] + '.txt'))

    if not out_fpath.exists():
        with open(out_fpath, 'w') as fp:
            fp.write('x, y, width, height, transcription, tag\n')

    tag = sample_attrs['tag']
    transcription = entities[tag].get('transcript', sample_attrs['transcription'])
    with open(out_fpath, 'a') as fp:
        fp.writelines([
            f'{shape_attrs["all_points_x"]}, {shape_attrs["all_points_y"]}, -1, -1, {transcription}, {tag}\n'])
