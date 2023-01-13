from glob import glob
import re
import random
import sys

import numpy as np


def expand_line(line, id):
    els = line.split(',')
    processed = [str(id)]
    nb = ','.join(els[:-2])

    #if els[-2] == "" or els[-2] == " ":
    #    return None
    if 'assin' in els[-1]:
        return None

    if "[" not in nb and "]" not in nb:
        coors = (int(els[0]), int(els[1]))
        size = (int(els[2]), int(els[3]))

        processed.append(str(coors[0]))
        processed.append(str(coors[1]))

        processed.append(str(coors[0] + size[0]))
        processed.append(str(coors[1]))

        processed.append(str(coors[0] + size[0]))
        processed.append(str(coors[1] + size[1]))

        processed.append(str(coors[0]))
        processed.append(str(coors[1] + size[1]))

        processed = processed + els[4:]

    else:
        processed.append(re.sub("[\[\]]", "", els[0][1:]))
        processed.append(re.sub("[\[\]]", "", els[4][1:])) # Extra space at the start.

        processed.append(re.sub("[\[\]]", "", els[3][1:]))
        processed.append(re.sub("[\[\]]", "", els[7][1:]))

        processed.append(re.sub("[\[\]]", "", els[2][1:]))
        processed.append(re.sub("[\[\]]", "", els[6][1:]))

        processed.append(re.sub("[\[\]]", "", els[1][1:]))
        processed.append(re.sub("[\[\]]", "", els[5][1:]))

        processed = processed + [els[-2], els[-1]] # Skipping -1 -1

    processed = ','.join(processed)
    return processed


def gen_new_file(name):
    file_name = name
    file = open(file_name, "r", encoding='unicode_escape')

    new_file_name = file_name.replace("_GT.txt", ".tsv")
    new_file = open(new_file_name, "w")

    in_lines = file.readlines()
    id = 0
    out_lines = []
    for line in in_lines[1:]:
        out_line = expand_line(line.replace("\n", ""), id)
        if out_line is not None:
            out_line = out_line.split(',')
            out_line[-1] = out_line[-1][1:]
            out_line[-2] = out_line[-2][1:]
            out_lines.append(",".join(out_line))
            id += 1
    for i in range(0, len(out_lines)):
        new_file.write(out_lines[i] + "\n")

    new_file.close()
    file.close()


if sys.argv[1] not in ['cross', 'std']:
    print("Mode must be cross or std.")
    exit(-1)

mode = sys.argv[1]
fdir = sys.argv[2]
ratio = 0.8
ratio_test = 0.1

fs = glob(f"{fdir}/*.txt")

for f in fs:
    gen_new_file(f)

if mode == 'cross':
    fs = {}
    for file in glob(f"{fdir}/*.txt"):
        idx = file.split('/')[-1].split('_')[0]
        if idx not in fs:
            fs[idx] = []
        fs[idx].append(file)

    idxs = sorted(fs.keys())
    random.shuffle(idxs)
    train_idx, valid_idx, test_idx = np.array_split(
        np.array(idxs),
        np.array([int(ratio*len(idxs)), int((1 - ratio_test)*len(idxs))])
    )

    train = [x for y in train_idx for x in fs[y]]
    valid = [x for y in valid_idx for x in fs[y]]
    test = [x for y in test_idx for x in fs[y]]

else:
    fs = glob(f"{fdir}/*.tsv")

    train = fs[:int(ratio*len(fs))]
    valid = fs[int(ratio*len(fs)):int((ratio + ((1 - ratio)/2))*len(fs))]
    test = fs[int((ratio + ((1 - ratio)/2))*len(fs)):]

train = [x.replace("_GT.txt", ".jpg") for x in train]
valid = [x.replace("_GT.txt", ".jpg") for x in valid]
test = [x.replace("_GT.txt", ".jpg") for x in test]
random.shuffle(train)
random.shuffle(test)
random.shuffle(valid)

with open("./train.csv", "w") as fd:
    for idx, f in enumerate(train):
        fd.write(f"{idx},RG,{f.split('/')[-1]}\n")
with open("./valid.csv", "w") as fd:
    for idx, f in enumerate(valid):
        fd.write(f"{idx},RG,{f.split('/')[-1]}\n")
with open("./test.csv", "w") as fd:
    for idx, f in enumerate(test):
        fd.write(f"{idx},RG,{f.split('/')[-1]}\n")
