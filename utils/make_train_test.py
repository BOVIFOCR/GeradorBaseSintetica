import csv
from glob import glob
import sys
import random
import shutil
from pathlib import Path

import numpy as np


if sys.argv[1] not in ['cross', 'std']:
    print("Mode must be cross or std.")
    exit(-1)

mode = sys.argv[1]
fdir = sys.argv[2]
odir = sys.argv[3]
ratio = .4, .2, .4

if mode == 'cross':
    fs = {}
    for file in glob(f"{fdir}/*"):
        idx = int(file.split('/')[-1].split('_')[0])
        if idx not in fs:
            fs[idx] = []
        fs[idx].append(file)
    abs_ratio = tuple(map(lambda r: int(r * len(fs)), ratio))

    idxs = sorted(fs.keys())
    random.shuffle(idxs)

    train_idx = idxs[:ratio[0]]
    valid_idx = idxs[ratio[0]:ratio[0]+ratio[1]]
    test_idx = idxs[ratio[0]+ratio[1]:]

    train = [
        synth_fname for orig_fname in train_idx
        for synth_fname in fs[orig_fname]]
    valid = [
        synth_fname for orig_fname in valid_idx
        for synth_fname in fs[orig_fname]]
    test = [
        synth_fname for orig_fname in test_idx
        for synth_fname in fs[orig_fname]]

else:
    fs = glob(f"{fdir}/*")

    train = fs[:int(ratio*len(fs))]
    valid = fs[int(ratio*len(fs)):int((ratio + ((1 - ratio)/2))*len(fs))]
    test = fs[int((ratio + ((1 - ratio)/2))*len(fs)):]

for part_name, part_files in zip(('train', 'valid', 'test'), (train, valid, test)):
    for fname in part_files:
        op = Path(odir) / part_name
        shutil.copyfile(fname, op.as_posix())
