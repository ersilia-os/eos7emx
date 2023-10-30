# imports
import os
import csv
import sys
from similarity import SmallWorldSampler

# parse arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# current file directory
root = os.path.dirname(os.path.abspath(__file__))


# read SMILES from .csv file, assuming one column with header
with open(input_file, "r") as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    smiles_list = [r[0] for r in reader]

# run model
sampler = SmallWorldSampler()
outputs = []
for smiles in smiles_list:
    outputs += [sampler.sample(smiles)]

header = ["sim-{0}".format(i) for i in range(1000)]
blank = [None] * len(header)
R = []
for o in outputs:
    r = o + [None] * (len(header) - len(o))
    R += [r]

input_len = len(smiles_list)
output_len = len(outputs)

with open(output_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for r in R:
        writer.writerow(r)
