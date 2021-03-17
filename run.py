import sys
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.rnmc import *


molecule_entries = loadfn("./mol_lists/ronalds_MoleculeEntry.json")

li_plus_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/Li.xyz',
    1)

ec_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/EC.xyz',
    0)

network_folder = Path("/tmp/network")
param_folder = Path("/tmp/params")

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

