import subprocess
import random
import pandas as pd
import numpy as np
from collections import defaultdict
from MarkovLogic.HierarchicalClustering.database import *
from MarkovLogic.HierarchicalClustering.GraphObjects import Hypergraph, Graph
from tqdm import tqdm
from GlobalDistribution import get_global_distribution
import networkx as nx


def split_formula_fragments(formula_fragments: list[str]):
    antecedent_predicate = formula_fragments[0].strip()
    dependent_predicates_string = formula_fragments[1].strip()

    connective_type = ''

    # check for disjunction
    if "v" in dependent_predicates_string:
        connective_type = 'disjunction'
        dependent_predicates = [predicate.strip() for predicate in dependent_predicates_string.split('v')]
    # check for conjunction
    elif "^" in dependent_predicates_string:
        connective_type = 'conjunction'
        dependent_predicates = [predicate.strip() for predicate in dependent_predicates_string.split('^')]
    else:
        dependent_predicates = [dependent_predicates_string]

    # check if predicate is negated, label it appropriately
    dependent_predicates = [(predicate, False) if predicate[0] != '!'
                            else (predicate[1:], True)
                            for predicate in dependent_predicates]

    return antecedent_predicate, dependent_predicates, connective_type


def parse_database_configuration_line(line: str):
    """
    TODO
    """
    line = line.strip()

    if is_implication(line):
        formula_type = 'implication'
        formula_fragments = line.split('->')
        antecedent_predicate, dependent_predicates, connective_type = split_formula_fragments(formula_fragments)
    elif is_dependency(line):
        formula_type = 'dependency'
        formula_fragments = line.split('|')
        antecedent_predicate, dependent_predicates, connective_type = split_formula_fragments(formula_fragments)
    else:
        raise SyntaxError(f'Line [{line}] has invalid syntax.')

    return formula_type, antecedent_predicate, dependent_predicates, connective_type


def is_implication(line: str):
    """
    TODO
    """
    predicate_match = "((\w|-|')+\(((\w|-|')+|((\w|-|')+,\s*)+(\w|-|')+)\))"
    implication_syntax = re.match(f"{predicate_match}(\s)*(->)(\s)*({predicate_match}(\s)(V|^|))*", line)

    is_implication_syntax = bool(implication_syntax)

    return is_implication_syntax


def is_dependency(line: str):
    """
    TODO
    """
    predicate_match = "((\w|-|')+\(((\w|-|')+|((\w|-|')+,\s*)+(\w|-|')+)\))"
    dependency_syntax = re.match(f"{predicate_match}(\s)*(\|)(\s)*({predicate_match}(\s)(V|^|))*", line)

    is_dependency_syntax = bool(dependency_syntax)

    return is_dependency_syntax


def parse_pattern(antecedent_predicate, dependent_predicates):
    get_arguments = lambda predicate: [argument.strip() for argument in predicate.split('(')[1][:-1].split(',')]
    dependent_predicate_names = [dependent_predicate[0].split('(')[0] for dependent_predicate in dependent_predicates]
    are_dependent_predicates_negated = [dependent_predicate[1] for dependent_predicate in dependent_predicates]
    args_antecedent_predicate = get_arguments(antecedent_predicate)
    args_dependent_predicates = [get_arguments(dependent_predicate[0]) for dependent_predicate in dependent_predicates]
    for pred_num, dependent_predicate_args in enumerate(args_dependent_predicates):
        for arg_num, arg in enumerate(dependent_predicate_args):
            try:
                index = args_antecedent_predicate.index(arg)
            except:
                index = None

            args_dependent_predicates[pred_num][arg_num] = index

    pattern = [(predicate, predicate_args, is_predicate_negated)
               for predicate, predicate_args, is_predicate_negated
               in zip(dependent_predicate_names, args_dependent_predicates, are_dependent_predicates_negated)]

    return pattern


class SyntheticDatasetMaker(object):
    def __init__(self,
                 info_file,
                 constants_file,
                 mln_file,
                 database_file,
                 database_configuration,
                 infer_dir='../alchemy-2/bin'):
        self.infer_dir = infer_dir
        self.predicate_argument_types, self.constant_types = self._parse_info_file(info_file)
        self.constants = self._parse_constants_file(constants_file)
        self.mln = mln_file

        self.synthetic_database = 'synthetic_database.db'
        self.temporary_file = 'temp'

        self.predicate_probability = get_global_distribution(database_file)
        self.database_ground_atoms = set()
        self.ground_atoms_by_predicate = defaultdict(lambda: [])

        self.implication_rules = defaultdict(lambda: {'pattern': [], 'connective': ''})
        self.dependency_rules = defaultdict(lambda: {'pattern': [], 'connective': ''})
        self.parse_database_configuration(database_configuration)
        print(self.implication_rules)
        print(self.dependency_rules)

    def generate_synthetic_database(self, number_of_samples):
        self.initialise_files()

        number_of_lines_in_database = 270
        for _ in tqdm(range(number_of_lines_in_database)):
            ground_atom = self.generate_new_ground_atom(number_of_samples)

            if ground_atom is None:
                continue
            else:
                predicate = ground_atom.split('(')[0]
                if predicate in self.implication_rules.keys():
                    ground_atoms = self.generate_dependent_ground_atoms(number_of_samples, ground_atom)
                    #print(f'Dependent ground atoms {ground_atoms}')
                    if any([ground_atom is None for ground_atom in ground_atoms]):
                        continue
                    else:
                        [self.add_ground_atom_to_database(ground_atom) for ground_atom in ground_atoms]

                self.add_ground_atom_to_database(ground_atom)

        self.remove_unconnected_ground_atoms()

    def generate_new_ground_atom(self, number_of_samples, template=None):
        if template is None:
            # get predicate at random from global probabilities
            predicate = np.random.choice(list(self.predicate_probability.keys()),
                                         p=list(self.predicate_probability.values()))
            predicate_args = None
        else:
            predicate = template[0]
            predicate_args = template[1]

        ground_atoms = self.generate_candidate_ground_atoms(predicate, number_of_samples, predicate_args)
       # print(ground_atoms)
        if ground_atoms:
            ground_atom_probabilities = [self.run_inference(ground_atom) for ground_atom in ground_atoms]
           # print(f'Probabilities {ground_atom_probabilities}')
            ground_atom = self.get_optimal_ground_atom(ground_atoms, ground_atom_probabilities)
        else:
            ground_atom = None
            #print(f'Warning: No suitable ground atom found for predicate {predicate}')

        return ground_atom

    def generate_dependent_ground_atoms(self, number_of_samples, ground_atom):
        templates = self.generate_templates(ground_atom)
       # print(f'Templates {templates}')

        ground_atoms = []
        for template in templates:
            ground_atoms.append(self.generate_new_ground_atom(number_of_samples, template))

        return ground_atoms

    def add_ground_atom_to_database(self, ground_atom):
        predicate = ground_atom.split('(')[0]
        predicate_arguments = [argument.strip() for argument in ground_atom.split('(')[1][:-1].split(',')]
        self.ground_atoms_by_predicate[predicate].append(predicate_arguments)
        self.database_ground_atoms.add(ground_atom)
        with open(self.synthetic_database, 'a') as synthetic_database:
            synthetic_database.write(ground_atom + '\n')

    def remove_unconnected_ground_atoms(self):
        hypergraph = Hypergraph(database_file='synthetic_database.db', info_file='imdb.info', assert_connected=False)
        graph = hypergraph.convert_to_graph(assert_connected=False)
        largest_cc = graph.subgraph(max(nx.connected_components(graph), key=len))
        largest_cc_graph = Graph()
        for edge in largest_cc.edges():
            largest_cc_graph.add_edge(*edge)

        largest_cc_hypergraph = largest_cc_graph.convert_to_hypergraph_from_template(hypergraph)
        print("Number of edges", largest_cc_hypergraph.number_of_edges())
        database = largest_cc_hypergraph.get_database_of_hypergraph()
        with open(self.synthetic_database, "w") as synthetic_database:
            synthetic_database.write(database)

    def generate_candidate_ground_atoms(self, predicate, number_of_samples, predicate_args=None):

        valid_constants = self.get_valid_constants_given_dependency_rules(predicate)
        print(predicate)
        print(valid_constants, 'valid constants')
        #input()

        ground_atom_samples = set()

        max_number_of_samples = self.get_max_number_of_samples(predicate, predicate_args)

        number_of_samples_remaining = min(number_of_samples, max_number_of_samples + 1)
        excess_samples = max_number_of_samples - number_of_samples

        while number_of_samples_remaining > 0:
            constants = []
            for arg_idx, const_type in enumerate(self.predicate_argument_types[predicate]):
                if predicate_args is None or predicate_args[arg_idx] is None:
                    if valid_constants is None:
                        constants.append(random.choice(self.constants[const_type]))
                    elif all([len(const) > 1 for const in valid_constants]):
                        constants.append(random.choice(valid_constants[arg_idx]))
                    else:
                        return None
                else:
                    constants.append(predicate_args[arg_idx])

            ground_atom = f'{predicate}({",".join(constants)})'
            if ground_atom not in self.database_ground_atoms:
                ground_atom_samples.add(ground_atom)
                number_of_samples_remaining -= 1
            else:
                if excess_samples > 0:
                    excess_samples -= 1
                else:
                    number_of_samples_remaining -= 1

        return list(ground_atom_samples)

    def generate_templates(self, ground_atom):
        # TODO: simplify logic
        predicate = ground_atom.split('(')[0]
        ground_atom_arguments = ground_atom.split('(')[1][:-1].split(',')
        connective = self.implication_rules[predicate]['connective']
        pattern = self.implication_rules[predicate]['pattern']
        templates = []

        dependent_predicates = [pattern[i][0] for i in range(len(pattern))]

        # TODO: update so that it checks for pre-existing ground atoms
        if connective == 'conjunction':
            dependent_predicates_arguments = [pattern[i][1] for i in range(len(pattern))]
            for idx in range(len(pattern)):
                arguments = [ground_atom_arguments[index] if index is not None else None
                             for index in dependent_predicates_arguments[idx]]
                templates.append((dependent_predicates[idx],
                                  arguments))
        elif connective == 'disjunction':
            probs = {pred: prob for pred, prob in
                     self.predicate_probability.items()
                     if pred in dependent_predicates}
            marginal_probability = sum(probs.values())
            dependent_predicate_probs = {pred: prob / marginal_probability for pred, prob in probs.items()}
            dependent_predicate = np.random.choice(list(dependent_predicate_probs.keys()),
                                                   p=list(dependent_predicate_probs.values()))
            predicate_index = dependent_predicates.index(dependent_predicate)
            dependent_predicate_arguments = pattern[predicate_index][1]
            arguments = [ground_atom_arguments[index] if index is not None else None
                         for index in dependent_predicate_arguments]
            templates.append((dependent_predicate, arguments))
        else:
            dependent_predicate_arguments = pattern[0][1]
            arguments = [ground_atom_arguments[index] if index is not None else None
                         for index in dependent_predicate_arguments]
            templates.append((dependent_predicates[0], arguments))

        return templates

    def get_valid_constants_given_dependency_rules(self, predicate):
        valid_constants = None
        #print(predicate)
        if predicate in self.dependency_rules.keys():
            #print(self.dependency_rules.keys())
            # TODO: simplify logic
            connective = self.dependency_rules[predicate]['connective']
            pattern = self.dependency_rules[predicate]['pattern']
            valid_constants = [self.constants[const_type] for const_type
                               in self.predicate_argument_types[predicate]]
            if connective == 'conjunction':
                for item in pattern:
                    dependent_predicate = item[0]
                    dependent_predicate_arguments = item[1]
                    dependent_predicate_negated = item[2]
                    for dependent_predicate_argument_index, antecedent_predicate_argument_index \
                            in enumerate(dependent_predicate_arguments):
                        if antecedent_predicate_argument_index is not None:
                            if not dependent_predicate_negated:
                                valid_constants[antecedent_predicate_argument_index] = \
                                    [ground_atom[dependent_predicate_argument_index] for ground_atom
                                     in self.ground_atoms_by_predicate[dependent_predicate]]
                            else:
                                print(predicate)
                                print(pattern)
                                print(valid_constants)
                                valid_constants[antecedent_predicate_argument_index] = \
                                    list(set(valid_constants[antecedent_predicate_argument_index]).
                                         difference(set([ground_atom[dependent_predicate_argument_index]
                                                         for ground_atom in
                                                         self.ground_atoms_by_predicate[dependent_predicate]])))
                                print(valid_constants)
                                #input()

            elif connective == 'disjunction':
                dependent_predicates = [pattern[i][0] for i in range(len(pattern))]
                probs = {pred: prob for pred, prob in
                         self.predicate_probability.items()
                         if pred in dependent_predicates}
                marginal_probability = sum(probs.values())
                dependent_predicate_probs = {pred: prob / marginal_probability for pred, prob in probs.items()}
                dependent_predicate = np.random.choice(list(dependent_predicate_probs.keys()),
                                                       p=list(dependent_predicate_probs.values()))
                predicate_index = dependent_predicates.index(predicate)
                dependent_predicate_arguments = pattern[predicate_index][1]
                dependent_predicate_negated = pattern[predicate_index][2]
                for dependent_predicate_argument_index, antecedent_predicate_argument_index \
                        in enumerate(dependent_predicate_arguments):
                    if antecedent_predicate_argument_index is not None:
                        if not dependent_predicate_negated:
                            valid_constants[antecedent_predicate_argument_index] = \
                                [ground_atom[dependent_predicate_argument_index] for ground_atom
                                 in self.ground_atoms_by_predicate[dependent_predicate]]
                        else:
                            print(predicate)
                            print(pattern)
                            print(valid_constants)
                            valid_constants[antecedent_predicate_argument_index] = \
                                list(set(valid_constants[antecedent_predicate_argument_index]).
                                     difference(set([ground_atom[dependent_predicate_argument_index]
                                                     for ground_atom in
                                                     self.ground_atoms_by_predicate[dependent_predicate]])))
                            print(valid_constants)
                            #input()
            else:
                dependent_predicate = pattern[0][0]
                dependent_predicate_arguments = pattern[0][1]
                dependent_predicate_negated = pattern[0][2]
                for dependent_predicate_argument_index, antecedent_predicate_argument_index \
                        in enumerate(dependent_predicate_arguments):
                    if antecedent_predicate_argument_index is not None:
                        if not dependent_predicate_negated:
                            valid_constants[antecedent_predicate_argument_index] = \
                                [ground_atom[dependent_predicate_argument_index] for ground_atom
                                 in self.ground_atoms_by_predicate[dependent_predicate]]
                        else:
                            #print(predicate)
                            #print(pattern)
                            #print(len(valid_constants[antecedent_predicate_argument_index]))
                            valid_constants[antecedent_predicate_argument_index] = \
                                list(set(valid_constants[antecedent_predicate_argument_index]).
                                     difference(set([ground_atom[dependent_predicate_argument_index]
                                                     for ground_atom in
                                                     self.ground_atoms_by_predicate[dependent_predicate]])))
                            #print(len(valid_constants[antecedent_predicate_argument_index]))
                            #input()

        return valid_constants

    def get_max_number_of_samples(self, predicate, predicate_args):
        if predicate_args is None:
            max_number_of_samples = sum([len(self.constants[const_type])
                                         for const_type in self.predicate_argument_types[predicate]])
        else:
            constant_types = [const_type for arg_idx, const_type in
                              enumerate(self.predicate_argument_types[predicate]) if predicate_args[arg_idx] is None]
            max_number_of_samples = sum([len(self.constants[const_type]) for const_type in constant_types])

        return max_number_of_samples



    @staticmethod
    def get_optimal_ground_atom(ground_atoms, probabilities):

        # if no probability obtained for any ground atom then choose a ground atom uniformly at random
        if all(probability is None for probability in probabilities):
            ground_atom = np.random.choice(ground_atoms)
        # else sample from ground atoms weighted by their probability of being true
        else:
            indices_of_null_probabilities = [index for index, prob in enumerate(probabilities) if prob is None]
            indices_of_null_probabilities.sort(reverse=True)
            for index in indices_of_null_probabilities:
                del probabilities[index]
                del ground_atoms[index]

            ground_atom_scores = np.array(probabilities) / np.sum(probabilities)
            ground_atom = np.random.choice(ground_atoms, p=ground_atom_scores)

        #print(f"Optimal {ground_atom}")
        return ground_atom

    def initialise_files(self):
        with open('empty.db', 'w') as file:
            file.write('')

        with open(self.temporary_file, 'w') as file:
            file.write('')

        with open(self.synthetic_database, 'w') as file:
            file.write('')

    def run_inference(self, candidate_literal):
        inference_command = f'{self.infer_dir}/infer -i {self.mln} -r {self.temporary_file} -e ' \
                            f'{self.synthetic_database} -q "{candidate_literal}"'
        subprocess.call(inference_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        shell=True)
        prob = self._get_probability_from_file(self.temporary_file)

        return prob

    @staticmethod
    def _get_probability_from_file(file):
        results_new_dataframe = pd.read_csv(file,
                                            delimiter=' ',
                                            names=['Ground_Atom', 'probability'])
        prob = 0
        try:
            probability = results_new_dataframe['probability'][0]
            if probability > 0:
                prob = probability
            else:
                prob = None
        except:
            prob = None

        return prob

    @staticmethod
    def _parse_info_file(path_to_info_file: str):
        """
        Parses the info file and returns a dictionary that maps predicate names to a list of strings which specify
        the ordered sequence of constant types that must go into the predicate's argument slots.

        e.g. {'Friends' : ['person', 'person'], 'Family' : ['person', 'person', 'person'], 'Smokes', ['person']}
        """
        predicate_argument_types = {}
        constant_types = set()

        with open(path_to_info_file, 'r') as info_file:
            for line_idx, line in enumerate(info_file.readlines()):
                # Skip empty lines, or lines which are commented out (// symbol)
                if is_empty_or_comment(line):
                    continue

                predicate, types = parse_line(line=line, line_idx=line_idx, file_name=path_to_info_file)

                predicate_argument_types[predicate] = types
                constant_types.update(types)

        return predicate_argument_types, constant_types

    def _parse_constants_file(self, path_to_constants_file: str):
        """
        TODO: Description
        """

        constants_dictionary = defaultdict(lambda: [])

        with open(path_to_constants_file, 'r') as constant_file:
            current_constant_type = ''
            for line_idx, line in enumerate(constant_file.readlines()):
                # Skip empty lines, or lines which are commented out (// symbol)
                if is_empty_or_comment(line):
                    continue

                line = line.strip()

                if line in self.constant_types:
                    current_constant_type = line
                    continue
                else:
                    constants_dictionary[current_constant_type].append(line)

        return constants_dictionary

    def parse_database_configuration(self, database_configuration):
        with open(database_configuration, 'r') as file:
            for line in file.readlines():
                if is_empty_or_comment(line):
                    continue
                else:
                    formula_type, \
                    antecedent_predicate, \
                    dependent_predicates, \
                    connective_type = \
                        parse_database_configuration_line(line)

                    predicate = antecedent_predicate.split('(')[0]

                    if formula_type == 'implication':
                        self.implication_rules[predicate]['connective'] = connective_type
                        self.implication_rules[predicate]['pattern'] = parse_pattern(antecedent_predicate,
                                                                                     dependent_predicates)
                    elif formula_type == 'dependency':
                        self.dependency_rules[predicate]['connective'] = connective_type
                        self.dependency_rules[predicate]['pattern'] = parse_pattern(antecedent_predicate,
                                                                                    dependent_predicates)
                    else:
                        raise ValueError('Formula must be either of implication or dependency type.')


if __name__ == "__main__":
    sdm = SyntheticDatasetMaker(info_file='imdb.info',
                                constants_file='imdb.constants',
                                mln_file='imdb1.mln',
                                database_file='imdb1.db',
                                database_configuration='imdb.configuration'
                                )

    sdm.generate_synthetic_database(number_of_samples=10)
