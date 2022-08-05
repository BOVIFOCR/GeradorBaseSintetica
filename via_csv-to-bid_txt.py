import os
from pathlib import Path

import json
import pandas as pd

df = pd.read_csv('via.csv')
outpath = Path('labels-reboot')

outpath.mkdir(exist_ok=True)

entities = json.loads(Path('files/entities.json').read_text())['front']

for _, row in df.iterrows():
    fname = row['filename']

    shape_attrs = json.loads(row['region_shape_attributes'])
    sample_attrs = json.loads(row['region_attributes'])

    out_fpath = (outpath / (os.path.splitext(fname)[0] + '.txt'))

    if not out_fpath.exists():
        with open(out_fpath, 'w') as fp:
            fp.write('x, y, width, height, transcription, tag\n')

    tag = sample_attrs['tag']
    transcription = entities['headers'].get(tag, sample_attrs["transcription"])  # indeed, headers transcriptions are null, but can be inferred from entities.json
    with open(out_fpath, 'a') as fp:
        fp.writelines([
            f'{shape_attrs["all_points_x"]}, {shape_attrs["all_points_y"]}, -1, -1, {transcription}, {tag}\n'])
