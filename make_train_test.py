import csv
from glob import glob
import sys
import numpy as np

if sys.argv[1] not in ['cross', 'std']:
    print("Mode must be cross or std.")
    exit(-1)
    
mode = sys.argv[1]
fdir = sys.argv[2]
ratio = 0.8

if mode == 'cross':
    fs = {}
    for file in glob(f"{fdir}/*"):
        idx = int(file.split('/')[-1].split('_')[0])
        if idx not in fs:
            fs[idx] = []
        fs[idx].append(file)

    idxs = sorted(fs.keys())
    train_idx, valid_idx, test_idx = np.array_split(np.array(idxs), np.array([int(ratio*len(idxs)), int((ratio + ((1 - ratio)/2))*len(idxs))]))

#    train_idx = idxs[:int(ratio*len(idxs))]
#    valid_idx = idxs[int(ratio*len(idxs)):int((ratio + ((1 - ratio)/2))*len(idxs))]
#    test_idx = idxs[int((ratio + ((1 - ratio)/2))*len(idxs)):]
    
    train = [x for y in train_idx for x in fs[y]]
    valid = [x for y in valid_idx for x in fs[y]]
    test = [x for y in test_idx for x in fs[y]]

else:
    fs = glob(f"{fdir}/*")
    
    train = fs[:int(ratio*len(fs))]
    valid = fs[int(ratio*len(fs)):int((ratio + ((1 - ratio)/2))*len(fs))]
    test = fs[int((ratio + ((1 - ratio)/2))*len(fs)):]

    
    
print(train)
print(valid)
print(test)