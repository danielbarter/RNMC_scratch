import sys
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
from mrnet.stochastic.rnmc import *



if len(sys.argv) != 4:
    print("usage: python run.py json_file network params")
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

ledc_entry = find_mol_entry_from_xyz_and_charge(
    molecule_entries,
    './xyz_files/LEDC.xyz',
    0)

network_folder = sys.argv[2]
param_folder = sys.argv[3]

initial_state_data = [
(li_plus_mol_entry, 30),
(ec_mol_entry,30)
]

analysis = run(molecule_entries,
               initial_state_data,
               network_folder,
               param_folder,
               number_of_threads = 20,
               number_of_steps = 500,
               number_of_simulations = 50,000
               )

analysis.generate_pathway_report(ledc_entry,10)
analysis.generate_consumption_report(ledc_entry)
analysis.generate_reaction_tally_report()
