import sys
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
import pickle

molecule_list_json = sys.argv[1]

molecule_entries = loadfn(molecule_list_json)
reaction_generator = ReactionGenerator(molecule_entries)

produced_reactions = []

for reaction in reaction_generator:
    produced_reactions.append((frozenset(reaction.reactant_indices),
                               frozenset(reaction.product_indices)))

produced_reactions = frozenset(produced_reactions)

with open('./goal','rb') as f:
    goal = pickle.load(f)
