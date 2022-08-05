import ast
import csv
import sys
import json
import os

import paths


with open(sys.argv[1]) as fd:
    csr = csv.reader(fd)
    ls = list(csr)

headers = ls[0]
ls = ls[1:]
fs = {}

def parse_tag(tag):
    if tag in ('dataNascimento', 'dataexp'):
        return 'date'
    elif tag == 'naturalidade':
        return 'city-est'
    elif tag in ('uf'):
        return 'state'
    else:
        return tag

for line in ls:
    if line[0] not in fs:
        fs[line[0]] = []
    data = {
        headers[4]: int(line[4]),
        headers[5]: ast.literal_eval(line[5]),
        headers[6]: ast.literal_eval(line[6])
    }

    if data[headers[6]]['tag_type'] == 'sensitive':
        data[headers[6]] |= {
            'text_type': parse_tag(data[headers[6]]['tag']),
            'info_type': 'p'
        }
    else:
        data[headers[6]] |= {
            'text_type': 'd',
            'info_type': 'd'
        }

    fs[line[0]].append(data)

os.makedirs(paths.json_path, exist_ok=True)
for key in fs.keys():
    with open(paths.json_path + key.split('.')[0] + '.json', 'w') as fd:
        fd.write(json.dumps(fs[key], indent=2))
