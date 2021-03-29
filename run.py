import sys
import os
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.serialize import *
from mrnet.stochastic.analyze import *



if len(sys.argv) != 2:
    print("usage: python run.py json_file")
    quit()

molecule_entries = loadfn(sys.argv[1])

li_plus_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/Li.xyz',
    1)

ec_mol_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/EC.xyz',
    0)

ledc_mol_entry  = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/LEDC.xyz',
    0)

initial_state_data = [
(li_plus_mol_entry, 30),
(ec_mol_entry,30)
]

reaction_generator = ReactionGenerator(molecule_entries,single_elem_interm_ignore=[])
rnsd = SerializedReactionNetwork(reaction_generator)
rnsd.serialize("./network", initial_state_data)
serialize_simulation_parameters("./params", number_of_threads=7)

run_simulator("./network", "./params")

sa = load_analysis("./network")
sa.generate_pathway_report(ledc_mol_entry,10)
sa.generate_consumption_report(ledc_mol_entry)
sa.generate_reaction_tally_report()
