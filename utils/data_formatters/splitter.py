import ast
import csv
import json
import sys

import paths

import pandas as pd


side = sys.argv[1]
synth_dir = paths.SynthesisDir(side)

entities = json.loads((synth_dir.path_input_base / 'entities.json').read_text())

with open(synth_dir.path_input_base / 'entities.via.csv') as fd:
    csr = csv.reader(fd)
    ls = list(csr)

headers = ls[0]
ls = ls[1:]
fs = {}


sample_df = pd.read_csv((synth_dir.path_input_base / 'sample.via.csv').as_posix())
for line in ls:
    filename = line[0]
    if filename not in fs:
        fs[filename] = []

    data = {
        'region_id': int(line[1]),  #
        'region_shape_attributes': ast.literal_eval(line[2]),
        'region_attributes': ast.literal_eval(line[3])
    }
    label = data['region_attributes']['tag']

    if entities[label].get('sensitive', False) or (
        data['region_attributes']['tag_type'] == 'sensitive'):
        transcription = entities[label].get(
            'transcript', data['region_attributes']['transcription'])
        data['region_attributes'] |= {
            'text_type': label,
            'info_type': 'p'
        }
    else:
        data['region_attributes'] |= {
            'text_type': 'd',
            'info_type': 'd'
        }

    fs[filename].append(data)

for key in fs:
    with open(synth_dir.path_json / (key.split('.')[0] + '.json'), 'w') as fd:
        fd.write(json.dumps(fs[key], indent=2))
