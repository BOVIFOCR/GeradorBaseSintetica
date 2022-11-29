from glob import glob
import re
import sys

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
    file = open(file_name, "r", encoding = 'unicode_escape')

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
    print(name)
    #out_lines = get_meta_verso(out_lines)
    for i in range(0, len(out_lines)):
        new_file.write(out_lines[i] + "\n")

    new_file.close()
    file.close()

fs = glob(f"{sys.argv[1]}/*.txt")
#fs = glob("../nbidv2/*.txt")

for f in fs:
    gen_new_file(f)
