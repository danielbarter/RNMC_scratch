import sys
sys.path.append('./mrnet/src')
from mrnet.network.reaction_generation import *
from monty.serialization import loadfn

molecule_list_json = sys.argv[1]
molecule_entries = loadfn(molecule_list_json)
reaction_generator = ReactionGenerator(molecule_entries)


def mass_balancer(reaction):
    reactant_atoms = {}
    product_atoms = {}
    for reactant in reaction.reactants:
        for atom in reactant.species:
            if atom in reactant_atoms:
                reactant_atoms[atom] += 1
            else:
                reactant_atoms[atom] = 1

    for product in reaction.products:
        for atom in product.species:
            if atom in product_atoms:
                product_atoms[atom] += 1
            else:
                product_atoms[atom] = 1

    return reactant_atoms, product_atoms


mass_not_conserved = []
counter = 0

for reaction in reaction_generator:
    counter += 1
    reactant_atoms, product_atoms = mass_balancer(reaction)
    if reactant_atoms != product_atoms:
        mass_not_conserved.append(reaction)

print(counter, "reactions")
print(mass_not_conserved)

