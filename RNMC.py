import numpy as np
import pyarrow.plasma as plasma
import math
import time
import os

from copy import copy
from functools import partial
from random import Random
from multiprocessing import Pool
from subprocess import Popen, DEVNULL

from pymatgen.core.structure import Molecule
from pymatgen.analysis.graphs import MoleculeGraph
from pymatgen.analysis.local_env import OpenBabelNN
from pymatgen.analysis.fragmenter import metal_edge_extender


def start_plasma_server(number_of_gb, plasma_file, logging = False):

    bytes_in_a_gb = 1000000000

    if logging:
        # plasma store inherits standard file descriptors from parent
        stdout = None
        stderr = None
    else:
        stdout = DEVNULL
        stderr = DEVNULL

    p = Popen(['plasma-store-server',
               '-m',
               str(number_of_gb * bytes_in_a_gb),
               '-s',
               plasma_file],
              stdout = stdout,
              stderr = stderr)

    # need to give the plasma store some time to start up
    time.sleep(1)

    return p

def serialize_reaction_network(rns, initial_state, folder, positive_weight_coef = 39):
    number_of_species_postfix = "/number_of_species"
    number_of_reactions_postfix = "/number_of_reactions"
    number_of_reactants_postfix = "/number_of_reactants"
    reactants_postfix = "/reactants"
    number_of_products_postfix = "/number_of_products"
    products_postfix = "/products"
    factor_zero_postfix = "/factor_zero"
    factor_two_postfix = "/factor_two"
    factor_duplicate_postfix = "/factor_duplicate"
    rates_postfix = "/rates"
    initial_state_postfix = "/initial_state"

    os.mkdir(folder)

    with open(folder + number_of_species_postfix, 'w') as f:
        f.write(str(rns.number_of_species) + '\n')

    with open(folder + number_of_reactions_postfix, 'w') as f:
        f.write(str(rns.number_of_reactions) + '\n')

    with open(folder + number_of_reactants_postfix, 'w') as f:
        for reaction in rns.index_to_reaction:
            f.write(str(len(reaction['reactants'])) + '\n')

    with open(folder + reactants_postfix, 'w') as f:
        for reaction in rns.index_to_reaction:
            for index in reaction['reactants']:
                f.write(str(index) + ' ')
            f.write('\n')

    with open(folder + number_of_products_postfix, 'w') as f:
        for reaction in rns.index_to_reaction:
            f.write(str(len(reaction['products'])) + '\n')

    with open(folder + products_postfix, 'w') as f:
        for reaction in rns.index_to_reaction:
            for index in reaction['products']:
                f.write(str(index) + ' ')
            f.write('\n')

    with open(folder + factor_two_postfix, 'w') as f:
        f.write(('%e' % 1.0) + '\n')

    with open(folder + factor_zero_postfix, 'w') as f:
        f.write(('%e' % 1.0) + '\n')

    with open(folder + factor_duplicate_postfix, 'w') as f:
        f.write(('%e' % 1.0) + '\n')

    with open(folder + rates_postfix, 'w') as f:
        for reaction in rns.index_to_reaction:
            dG = reaction['free_energy']
            if dG > 0:
                rate = math.exp(- positive_weight_coef * dG)
            else:
                rate = math.exp(- dG)
            f.write(('%e' % rate) + '\n')

    with open(folder + initial_state_postfix, 'w') as f:
        for i in range(rns.number_of_species):
            f.write(str(int(initial_state[i])) + '\n')








class ReactionNetworkSerialization:
    """
    class for serializing a reaction network.
    Ideally, we would share a ReactionNetworkSerialization object between
    all Monte Carlo objects in a Monte Carlo Bundle, but because
    of the global interpreter lock, Python doesn't have true threading
    and multiprocessing Shared Memory is somewhat clumsy as of 2020.

    We solve this using plasma (which uses the apache arrow format)
    as a shared object store.

    https://arrow.apache.org/blog/2017/08/08/plasma-in-memory-object-store/
    https://arrow.apache.org/docs/python/plasma.html

    main attributes:
    species_to_index: a dictionary which maps species names to their
    numerical_index which is used to refer to species during simulations.

    index_to_speies: the reverse dictionary to species_to_index

    species_data: maps species indicies to species data.

    rns.species_data[rns.index_to_species[index]] gives the data for a given index

    indes_to_reaction: a list which assigns indices to each reaction.
    Reactants and products are in terms of species indices.

    reactant_to_reactions: a dictionary mapping a species index to
    all the reaction indices which have that species as a reactant.

    dependency_graph: a dictionary mapping each reaction index to
    all the reaction indices which have a reactant in the reactans or products
    of the reaction. In other words, it maps a reaction index to the list
    of all reactions whose propensities need to be updated when the reaction
    occours

    rns_dict: A dictionary containing all the data which we are going to
    serialize into arrow format for the simulation processes

    """

    def pp_reaction(self,index):
        """
        pretty print a reaction given its index
        """
        reaction = self.index_to_reaction[index]
        reactants = " + ".join([self.index_to_species[reactant_index]
                                for reactant_index in reaction['reactants']])
        products = " + ".join([self.index_to_species[product_index]
                                for product_index in reaction['products']])
        dG = str(reaction['free_energy'])
        return (reactants + " -> " + products).ljust(50) + dG

    def find_index_from_mol_graph(self, mol_graph_file_path, charge):
        """
        given a file 'molecule.xyz', find the index corresponding to the
        molecule graph with given charge
        """
        target_mol_graph = MoleculeGraph.with_local_env_strategy(
            Molecule.from_file(mol_graph_file_path),
            OpenBabelNN())

        ### correction to the molecule graph
        target_mol_graph = metal_edge_extender(target_mol_graph)

        match = False
        species_index = -1
        while not match:
            species_index += 1
            data = self.species_data[species_index]
            species_mol_graph = data.mol_graph

            if data.charge == charge:
                match = target_mol_graph.isomorphic_to(species_mol_graph)

        if match:
            return species_index
        else:
            return None


    def __extract_index_species_mapping(self,reactions):
        """
        assign each species an index and construct
        forward and backward mappings between indicies and species.
        """
        species_to_index = {}
        index = 0

        for reaction in reactions:
            entry_ids = {e.entry_id for e in reaction.reactants + reaction.products}
            for entry_id in entry_ids:
                species = entry_id
                if species not in species_to_index:
                    species_to_index[species] = index
                    index = index + 1


        rev = {i : species for species, i in species_to_index.items()}
        self.number_of_species = index
        self.species_to_index = species_to_index
        self.index_to_species = rev

    def __extract_index_reaction_mapping(self,reactions):
        """
        assign each reaction an index and construct
        a mapping from reaction indices to reaction data
        """
        self.number_of_reactions = 2 * len(reactions)
        index_to_reaction = []
        for reaction in reactions:
            reactant_indices = [self.species_to_index[reactant]
                                for reactant in reaction.reactant_ids]
            product_indices = [self.species_to_index[product]
                               for product in reaction.product_ids]

            forward_free_energy = reaction.free_energy()["free_energy_A"]
            backward_free_energy = reaction.free_energy()["free_energy_B"]


            index_to_reaction.append({'reactants' : reactant_indices,
                                      'products' : product_indices,
                                      'free_energy' : forward_free_energy})
            index_to_reaction.append({'reactants' : product_indices,
                                      'products' : reactant_indices,
                                      'free_energy' : backward_free_energy})

        self.index_to_reaction = index_to_reaction

    def __extract_dependency_graph(self):
        """
        First, construct a mapping, reactant_to_reactions,
        which sends each species index to a list
        of reaction indices which have the corresponding species as a
        reactant.

        Then construct a dependency graph, which maps a reaction index
        to a list of reaction indicies whose propensities need to be updated
        after the reaction occours.
        """
        reactant_to_reactions = {}
        for reaction_index in range(self.number_of_reactions):
            reaction = self.index_to_reaction[reaction_index]

            for reactant_index in reaction['reactants']:
                if reactant_index in reactant_to_reactions:
                    reactant_to_reactions[reactant_index].append(reaction_index)
                else:
                    reactant_to_reactions[reactant_index] = [reaction_index]

        if self.logging:
            print("computed reactant to reactions")
        self.reactant_to_reactions = reactant_to_reactions

        dependency_graph = {}

        for reaction_index in range(self.number_of_reactions):
            reaction = self.index_to_reaction[reaction_index]

            impacted_reactions = []
            for species_index in reaction['reactants'] + reaction['products']:
                impacted_reactions.extend(reactant_to_reactions[species_index])

            # we need to delete duplicates
            # storing lists is way more memory efficient than storing sets
            dependency_graph[reaction_index] = list(set(impacted_reactions))

        if self.logging:
            print("computed dependency graph")
        self.dependency_graph = dependency_graph

    def __extract_species_data(self,entries_list):
        species_data = {}
        for entry in entries_list:
            entry_id = entry.entry_id
            if entry_id in self.species_to_index:
                species_data[self.species_to_index[entry_id]] = entry

        self.species_data = species_data


    def __init__(self,reaction_network,logging = False):
        """
        Input: a list of reaction objects
        """
        reactions = reaction_network.reactions
        entries_list = reaction_network.entries_list
        self.logging = logging


        self.__extract_index_species_mapping(reactions)
        if logging:
            print("extracted index species mapping")

        self.__extract_species_data(entries_list)
        if logging:
            print("extracted species data")

        self.__extract_index_reaction_mapping(reactions)
        if logging:
            print("extracted index reaction mapping")

        self.__extract_dependency_graph()
        if logging:
            print("finished serialization")

        # rns_dict is copied into the plasma store
        self.rns_dict = {}
        self.rns_dict['index_to_reaction'] = self.index_to_reaction
        self.rns_dict['number_of_reactions'] = self.number_of_reactions
        self.rns_dict['reactant_to_reactions'] = self.reactant_to_reactions
        self.rns_dict['dependency_graph'] = self.dependency_graph




class IndexedBinaryTree:
    """
    Indexed binary tree to store the propensities during an MC run. This allows
    for log(#reactions) scaling for both updating a propensity and choosing the
    next reaction.


    the value stored at a node is the sum of the values of the children.
    total propensity is stored at the root.
    """
    def __init__(self, initial_propensities):
        """
        Input: an array of initial propensities. We pad the array out to
        the next power of two to make the tree balanced.
        The tree has 2 * number_of_leaves nodes, and currently each node has
        5 attribures, so there are definately memory improvements to gain here
        by using a binary heap.
        """
        number_of_reactions = len(initial_propensities)
        number_of_leaves = 2 ** math.ceil(math.log2(number_of_reactions))
        padding = np.zeros(number_of_leaves - number_of_reactions)
        initial_propensities_padded = np.concatenate([initial_propensities,
                                                      padding])
        leaves = []
        for reaction_index, propensity in enumerate(initial_propensities_padded):
            leaves.append(BinaryTreeNode(None,None,None,propensity,reaction_index))


        node_iterator = iter(leaves)
        new_nodes = []

        # we build the tree by looping through the nodes two at a time
        while len(new_nodes) != 1:
            new_nodes = []

            for node in node_iterator:
                next_node = next(node_iterator)
                new_value = node.value + next_node.value
                new_node = BinaryTreeNode(node, next_node, None, new_value, None)
                node.parent = new_node
                next_node.parent = new_node
                new_nodes.append(new_node)


            node_iterator = iter(new_nodes)

        self.root = new_nodes[0]
        self.leaf_index = leaves[0:number_of_reactions]

    def find_next_reaction(self,threshold):
        current_node = self.root
        while current_node.left:
            left_value = current_node.left.value

            if threshold < left_value:
                current_node = current_node.left
            else:
                current_node = current_node.right
                threshold -= left_value

        return current_node.index


    def update_propensity(self, index, new_value):
        leaf = self.leaf_index[index]
        value_diff = new_value - leaf.value
        leaf.value = new_value
        node = leaf
        while node.parent:
            node = node.parent
            node.value += value_diff



class BinaryTreeNode:
    def __init__(self,left,right,parent,value,index):
        self.left = left
        self.right = right
        self.parent = parent
        self.value = value
        self.index = index




# mass action kinetics
def falling_power(n, p):
    state = 1
    while p > 0:
        state = state * n
        p = p - 1
        n = n - 1
    return state


def update_state(state, reaction):
    for species_index in reaction['reactants']:
        state[species_index] -= 1

    for species_index in reaction['products']:
        state[species_index] += 1

class MonteCarlo:
    """
    class for a single monte carlo run.

    input arguments:
    rns_dict_id (an id in the plasma store)
    initial_state_id (an id in the plasma store)
    seed to initialize the psuedorandom generator

    positive_weight_coefficient:
        exp(- pwc * dG) when dG > 0 and exp(-dG) when dG < 0.
        default is 39 eV, which is 1/kT when T = 298K

    termination_threshold:
       defaults to 1/1000. Used as a cutoff for total propensity when
       deciding if the run has reached a dead end.

    """

    def compute_propensity(self, reaction_index):
        reaction = self.rns_dict['index_to_reaction'][reaction_index]
        reactant_dict = {}
        for reactant_index in reaction['reactants']:
            if reactant_index in reactant_dict:
                reactant_dict[reactant_index] += 1
            else:
                reactant_dict[reactant_index] = 1

        dG = reaction['free_energy']

        if dG > 0:
            propensity_state = math.exp(- self.positive_weight_coef * dG)
        else:
            propensity_state = math.exp(- dG)

        for species_index, number in reactant_dict.items():
            propensity_state *= falling_power(
                self.state[species_index],
                number)

        return propensity_state

    def __initialize_propensities(self):
        initial_species_present = list(np.where(self.state > 0)[0])
        initial_propensities = np.zeros(self.rns_dict['number_of_reactions'])
        reaction_indicies = []
        for species_index in initial_species_present:
            reaction_indicies.extend(
                self.rns_dict['reactant_to_reactions'][species_index])

        for reaction_index in set(reaction_indicies):
            initial_propensities[reaction_index] = self.compute_propensity(
                reaction_index)

        return initial_propensities

    def step(self):
        """
        perform an MC step. Return True if everything is good.
        If total propensity gets very small, this is a sign that we have
        reached a dead end. Return False in that case, which will
        terminate the run
        """
        if self.propensity_tree.root.value < self.termination_threshold:
            return False

        random_1 = self.random.uniform(0,1)
        random_2 = self.random.uniform(0,1)

        self.time = math.log(1 / random_1) / self.propensity_tree.root.value
        self.number_of_steps += 1

        threshold = random_2 * self.propensity_tree.root.value
        next_reaction_index = self.propensity_tree.find_next_reaction(threshold)
        self.reactions_which_occoured.append(next_reaction_index)
        next_reaction = self.rns_dict['index_to_reaction'][next_reaction_index]
        affected_reactions = self.rns_dict['dependency_graph'][next_reaction_index]

        update_state(self.state, next_reaction)

        for reaction_index in affected_reactions:
            new_propensity = self.compute_propensity(reaction_index)
            self.propensity_tree.update_propensity(reaction_index, new_propensity)

        return True

    def run_until(self,time_cutoff):
        while self.time < time_cutoff:
            if not self.step():
                break
        if self.logging:
            print("run finished: " + str(self.number_of_steps) + " steps")


    def __init__(self,
                 seed,
                 rns_dict_id,
                 initial_state_id,
                 plasma_file,
                 positive_weight_coef = 39,
                 termination_threshold = 1 / 1000,
                 logging = False):

        # initialize state from the plasma store
        client = plasma.connect(plasma_file)
        self.rns_dict = client.get(rns_dict_id)
        initial_state = client.get(initial_state_id)

        self.seed = seed
        self.positive_weight_coef = positive_weight_coef
        self.termination_threshold = termination_threshold
        self.logging = logging


        self.random = Random()
        self.random.seed(self.seed)


        self.reactions_which_occoured = []
        self.time = 0
        self.number_of_steps = 0
        self.state = np.copy(initial_state)

        initial_propensities = self.__initialize_propensities()
        self.propensity_tree = IndexedBinaryTree(initial_propensities)
        if self.logging:
            print("initialization finished")


def collect_duplicate_pathways(pathways):
    pathway_dict = {}
    for pathway in pathways:
        key = frozenset(pathway)
        if key in pathway_dict:
            pathway_dict[key]['frequency'] += 1
        else:
            pathway_dict[key] = {'pathway' : pathway, 'frequency' : 1}
    return pathway_dict



# this needs to be a global function so we can pickle it and send it
# to the worker processes
def run_with_seed(seed,
                  rns_dict_id,
                  initial_state_id,
                  plasma_file,
                  positive_weight_coef,
                  termination_threshold,
                  time_cutoff,
                  logging):
    """
    create and run a MonteCarlo object and return the reaction history
    """
    mc = MonteCarlo(seed,
                    rns_dict_id,
                    initial_state_id,
                    plasma_file,
                    positive_weight_coef,
                    termination_threshold,
                    logging)

    mc.run_until(time_cutoff)
    return mc.reactions_which_occoured



class MonteCarloBundler:
    """
    Class to bundle together a bunch of MC runs and run them in paralell.
    Input arguments.
    reaction_network_serialization
    initial_state
    time_cutoff
    seed_array
    positive_weight_coef (default 39)
    termination_threshold (default 1/1000)

    a subtle but important point: we don't want to pass a method of
    MonteCarloBundler to the worker processes as this will cause the whole
    object to be pickled and passed through a pipe (including the reaction
    network serialization attribute)
    """

    def extract_reaction_pathways(self, target_species_index):
        """
        given a reaction history and a target molecule, find the
        first reaction which produced the target molecule (if any).
        Apply that reaction to the initial state to produce a partial
        state array. Missing reactants have negative values in the
        partial state array. Now loop through the reaction history
        to resolve the missing reactants.
        """
        reaction_pathway_list = []
        for reaction_history in self.reaction_histories:

            # -1 if target wasn't produced
            # index of reaction if target was produced
            reaction_producing_target_index = -1
            for reaction_index in reaction_history:
                reaction = self.rns.index_to_reaction[reaction_index]
                if target_species_index in reaction['products']:
                    reaction_producing_target_index = reaction_index
                    break

            if reaction_producing_target_index == -1:
                continue
            else:
                pathway = [reaction_producing_target_index]
                partial_state = np.copy(self.initial_state)
                final_reaction = self.rns.index_to_reaction[pathway[0]]
                update_state(partial_state, final_reaction)

                negative_species = list(np.where(partial_state < 0)[0])

                while(len(negative_species) != 0):
                    for species_index in negative_species:
                        for reaction_index in reaction_history:
                            reaction = self.rns.index_to_reaction[reaction_index]
                            if species_index in reaction['products']:
                                update_state(partial_state, reaction)
                                pathway.insert(0,reaction_index)
                                break

                    negative_species = list(np.where(partial_state < 0)[0])

                reaction_pathway_list.append(pathway)

        reaction_pathway_dict = collect_duplicate_pathways(reaction_pathway_list)
        self.reaction_pathways_dict[target_species_index] = reaction_pathway_dict


    def pp_pathways(self,target_species_index):
        if target_species_index not in self.reaction_pathways_dict:
            self.extract_reaction_pathways(target_species_index)

        pathways = self.reaction_pathways_dict[target_species_index]

        for _, unique_pathway in sorted(pathways.items(),
                                        key = lambda item: -item[1]['frequency']):

            print(str(unique_pathway['frequency']) + " occurrences:")
            for reaction_index in unique_pathway['pathway']:
                print(self.rns.pp_reaction(reaction_index))
            print()

    def __init__(self, number_of_processes,
                 reaction_network_serialization,
                 initial_state,
                 time_cutoff,
                 seed_array,
                 plasma_file,
                 positive_weight_coef = 39,
                 termination_threshold = 1 / 1000,
                 logging = False):
        self.rns = reaction_network_serialization
        self.initial_state = initial_state


        # serialize the relevent state for access by worker processes
        if logging:
            print('connecting to plasma server')
        client = plasma.connect(plasma_file)
        if logging:
            print('transfering data to plasma store')
        rns_dict_id = client.put(self.rns.rns_dict)
        initial_state_id = client.put(self.initial_state)
        if logging:
            print('transfer to plasma store complete')

        # it is important that this partial func doesn't have a reference
        # to self, otherwise it will end up pickling the whole
        # reactionNetworkSerialization and sending it to each process
        run_with_seed_partial = partial(
            run_with_seed,
            rns_dict_id = rns_dict_id,
            initial_state_id = initial_state_id,
            plasma_file = plasma_file,
            positive_weight_coef = positive_weight_coef,
            termination_threshold = termination_threshold,
            time_cutoff = time_cutoff,
            logging = logging)

        self.reaction_pathways_dict = {}

        # if number of processes <= 1, we create a process pool
        # this is useful for profiling
        if number_of_processes > 1:
            pool = Pool(number_of_processes)
            self.reaction_histories = pool.map(
                run_with_seed_partial,
                seed_array)
            pool.close()
            pool.join()

        else:
            self.reaction_histories = []
            for seed in seed_array:
                self.reaction_histories.append(
                    run_with_seed_partial(seed))
