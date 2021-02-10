from RNMC import *
import sys
import pickle

sys.path.append('./mrnet/src')


import mrnet.network
import mrnet.core.mol_entry
import mrnet.core.reactions
import mrnet.core.rates


# reactants and products are lists of pairs (.xyz file, charge)
def is_reaction_present(rnsd, reactants, products):
    reactant_indices = []
    product_indices = []
    for (file_xyz,charge) in reactants:
        index = rnsd.find_index_from_mol_graph(file_xyz, charge)
        reactant_indices.append(index)

    for (file_xyz,charge) in products:
        index = rnsd.find_index_from_mol_graph(file_xyz, charge)
        product_indices.append(index)

    reactants_unordered = frozenset(reactant_indices)
    products_unordered = frozenset(product_indices)
    for reaction in rnsd.index_to_reaction:
        if (reactants_unordered == frozenset(reactions['reactants']) and
            products_unordered == frozenset(reactions['products'])):
            return reaction

    return None

if len(sys.argv) != 2:
    print("usage: python analyze.py network_folder")
    exit()

network_folder = sys.argv[1]

with open(network_folder + "/rnsd.pickle",'rb') as f:
    rnsd = pickle.load(f)

# TODO: don't want network folder as an attribute of rnsd
rnsd.network_folder = network_folder
sa = SimulationAnalyser(rnsd, network_folder)


LEDC_index = rnsd.find_index_from_mol_graph('./mrnet/test_files/reaction_network_files/LEDC.xyz',0)
Li2CO3_index = rnsd.find_index_from_mol_graph('./li2co3_0.xyz', 0)
sa.generate_pathway_report(LEDC_index)
