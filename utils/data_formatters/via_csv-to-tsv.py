import json
import os
from pathlib import Path

import pandas as pd

from src.paths import json_path

df = pd.read_csv('via.csv')

outpath = json_path
outpath.mkdir(exist_ok=True)

entities = json.loads(Path('files/entities.json').read_text())
cur_ids = {}

for _, row in df.iterrows():
    fname = row['filename']
    if fname not in cur_ids:
        cur_ids[fname] = 0

    shape_attrs = json.loads(row['region_shape_attributes'])
    sample_attrs = json.loads(row['region_attributes'])

    out_fpath = (outpath / (os.path.splitext(fname)[0] + '.tsv'))

    tag = sample_attrs['tag']
    if entities[tag]['is_entity']:
        transcription = entities[tag].get('transcript', sample_attrs['transcription'])
        points_str = ','.join(','.join(
            map(str, map(int, p))) for p in zip(shape_attrs["all_points_x"], shape_attrs["all_points_y"]))
        with open(out_fpath, 'a') as fp:
            fp.write(f'{cur_ids[fname]},{points_str},{transcription},{tag}\n')
        cur_ids[fname] += 1