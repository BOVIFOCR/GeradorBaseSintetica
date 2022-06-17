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

def parse_tag(tag):
    if tag == 'nome' or tag.startswith('ass') or tag == 'filiacao':
        return 'name'
    elif tag == 'data-nascimento' or tag == 'data-expedicao':
        return 'date'
    elif tag == 'naturalidade':
        return 'city'
    elif tag == 'obs' or tag == 'org' or tag == 'cpf' or tag == 'rg' or tag == '5-code' or tag == 'comarca':
        return tag
    elif tag == 'doc-origem':
        return 'doc'
    elif tag == 'fator-rh':
        return 'rh'
    elif tag == 'protocol' or tag == 'unknown':
        return 'unknown'

for line in ls:
    if line[0] not in fs:
        fs[line[0]] = []
    data = {}
    data[headers[4]] = int(line[4])
    data[headers[5]] = ast.literal_eval(line[5])
    data[headers[6]] = ast.literal_eval(line[6])
    tag = data[headers[6]]['tag']
    if tag.startswith('info') or tag == 'meta':
        data[headers[6]]['text_type'] = 'd'
        data[headers[6]]['info_type'] = 'd'
    else:
        data[headers[6]]['text_type'] = 'p'
        data[headers[6]]['info_type'] = parse_tag(tag)

    fs[line[0]].append(data)

for key in fs.keys():
    with open(label_path + key.split('.')[0] + '.json', 'w') as fd:
        fd.write(json.dumps(fs[key], indent=2))
