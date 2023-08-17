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
outputs = sampler.sample(smiles_list)

# check that at least the output is greater than the input.
input_len = len(smiles_list)
output_len = len(outputs)
assert (input_len <= output_len)

# write output in a .csv file
with open(output_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(["similarity"])  # header
    for o in outputs:
        writer.writerow(o)
