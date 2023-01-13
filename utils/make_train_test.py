from glob import glob
import sys
import numpy as np
import random

if sys.argv[1] not in ['cross', 'std']:
    print("Mode must be cross or std.")
    exit(-1)

mode = sys.argv[1]
fdir = sys.argv[2]
ratio = 0.8
ratio_test = 0.1

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
        np.array([int(ratio*len(idxs)), int((1 - ratio_test)*len(idxs))]))

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
