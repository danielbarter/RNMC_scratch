import sys
import os
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *
from mrnet.stochastic.analyze import *

from multiprocessing import Pool

if len(sys.argv) != 2:
    print("usage: python serialize.py json_file")
    quit()

molecule_entries = loadfn(sys.argv[1])

ledc_mol_entry  = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/LEDC.xyz',
    0)

p0 = "./runs/network_0"
p1 = "./runs/network_1"
p2 = "./runs/network_2"
p3 = "./runs/network_3"

def f(p):
    a = load_analysis(p)
    a.generate_pathway_report(ledc_mol_entry, 100)

with Pool(4) as p:
    p.map(f, [p0, p1, p2, p3])

