import csv
import sys
import json
import ast

label_path = './labels/'

with open(sys.argv[1]) as fd:
    csr = csv.reader(fd)
    ls = [x for x in csr]

headers = ls[0]
ls = ls[1:]
fs = {}

for line in ls:
    if line[0] not in fs:
        fs[line[0]] = []
    data = {}
    data[headers[4]] = int(line[4])
    data[headers[5]] = ast.literal_eval(line[5])
    data[headers[6]] = ast.literal_eval(line[6])

    fs[line[0]].append(data)

for key in fs.keys():
    with open(label_path + key.split('.')[0] + '.json', 'w') as fd:
        fd.write(json.dumps(fs[key], indent=2))
