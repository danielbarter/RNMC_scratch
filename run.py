import sys
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.rnmc import *

if sys.argc != 2:
    print("usage: python run.py json_file")
    quit()

molecule_entries = loadfn(sys.argv[2])

li_plus_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/Li.xyz',
    1)

ec_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/EC.xyz',
    0)

network_folder = "/tmp/network"
param_folder = "/tmp/params"

initial_state_data = [
(li_plus_mol_entry, 30),
(ec_mol_entry,30)
]

run(molecule_entries,
    initial_state_data,
    network_folder,
    param_folder,
    4,
    200,
    1000)

