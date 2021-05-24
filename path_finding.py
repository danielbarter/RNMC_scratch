import sys
import os
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from mrnet.network.reaction_network import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *


if len(sys.argv) != 2:
    print("usage: python serialize.py json_file network params")
    quit()

mol_list = loadfn(sys.argv[1])

li_plus_mol_entry = find_mol_entry_from_xyz_and_charge(
    mol_list,
    './xyz_files/Li.xyz',
    1)

ec_mol_entry = find_mol_entry_from_xyz_and_charge(
    mol_list,
    './xyz_files/EC.xyz',
    0)

ledc_mol_entry  = find_mol_entry_from_xyz_and_charge(
    mol_list,
    './xyz_files/LEDC.xyz',
    0)

init_mols = [li_plus_mol_entry, ec_mol_entry]

target = ledc_mol_entry

entries_box = EntriesBox(mol_list)
ri = ReactionIterator(entries_box)
rn = ReactionNetwork(ri)

initial_inds = [e.parameters["ind"] for e in init_mols]

rn.solve_prerequisites(initial_inds, "default_cost")

# set initial conditions
PRs, paths, top_path_list = rn.find_paths(
    initial_inds, target.parameters["ind"], weight="default_cost", num_paths=20
)

pathfinding_path_report("./path_finding_report", rn, paths)
# return shortest paths to every mol
