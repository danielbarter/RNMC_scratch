import sys
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn
import pickle


# you are probably gonna want to do something else while waiting for this
# it takes ~ 30 minutes when running on sams molecule list

molecule_list_json = sys.argv[1]
molecule_entries = loadfn(molecule_list_json)
reaction_generator = ReactionGenerator(molecule_entries)

# don't generate the elementry reactions
reaction_generator.current_chunk = []


with open('./goal','rb') as f:
    goal = pickle.load(f)

missing_reactions = set(goal)


# suggesting that interpreter garbage collect the large frozen set
# trying to keep memory footprint low
goal = None
extras = []


for reaction in reaction_generator:
    reaction_sig = ((frozenset(reaction.reactant_indices),
                     frozenset(reaction.product_indices)))

    if reaction_sig in missing_reactions:
        missing_reactions.remove(reaction_sig)

    else:
        extras.append(reaction_sig)






if (len(missing_reactions) == 0 and len(extras) == 0):
    print("all good!")
else:
    print(len(missing_reactions),
          " reactions are missing.")
    print(len(extras),
          " extra reactions.")
    print("this is bad....")

