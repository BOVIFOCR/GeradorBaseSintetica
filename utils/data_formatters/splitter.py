import ast
import csv
import json
import os
import sys

import paths

with open(sys.argv[1]) as fd:
    csr = csv.reader(fd)
    ls = list(csr)

side = sys.argv[2]
synth_dir = paths.SynthesisDir(sys.argv[2])

entities = json.loads((synth_dir.path_static / f'{side}_entities.json').read_text())

headers = ls[0]
ls = ls[1:]
fs = {}


def parse_label(tag):
    if tag in ('dataNascimento', 'dataexp'):
        return 'date'
    elif tag == 'naturalidade':
        return 'city-est'
    elif tag in ('uf'):
        return 'state'
    else:
        return tag


for line in ls:
    filename = line[0]
    if filename not in fs:
        fs[filename] = []

    data = {
        'region_id': int(line[4]),  #
        'region_shape_attributes': ast.literal_eval(line[5]),
        'region_attributes': ast.literal_eval(line[6])
    }
    label = data['region_attributes']['tag']

    if entities[label]['sensitive'] or data['region_attributes']['tag_type'] == 'sensitive':
        transcription = entities[label].get('transcript', data['region_attributes']['transcription'])
        data['region_attributes'] |= {
            'text_type': parse_label(label),
            'info_type': 'p'
        }
    else:
        data['region_attributes'] |= {
            'text_type': 'd',
            'info_type': 'd'
        }

    fs[filename].append(data)

os.makedirs(paths.json_path, exist_ok=True)
for key in fs.keys():
    with open(paths.json_path / (key.split('.')[0] + '.json'), 'w') as fd:
        fd.write(json.dumps(fs[key], indent=2))
