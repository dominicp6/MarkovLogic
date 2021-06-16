import os
import pandas as pd
import numpy as np
import subprocess
import time
import json
from datetime import datetime

from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities
from CommunityPrinter import CommunityPrinter


class MLNEvaluator(object):
    def __init__(self, lsm_dir='../../lsmcode',
                 infer_dir='../../alchemy-2/bin',
                 data_dir='./Data',
                 mln_dir='./MLNs',
                 log_dir='./Log',
                 results_dir='./Results',
                 delete_generated_files=False):

        self.lsm_dir = lsm_dir
        self.infer_dir = infer_dir
        self.data_dir = data_dir
        self.mln_dir = mln_dir
        self.log_dir = log_dir
        self.results_dir = results_dir

        self.delete_generated_files = delete_generated_files

        self.hierarchical_clustering_suffix = '_hc'  # file suffix used when running hierarchical clustering method
        self.standard_method_suffix = '_sm'  # file suffix used when running the standard method

        self.time_statistics = {
            'hierarchical_clustering': {
                'clustering': [],
                'getting_communities': [],
                'path_finding': [],
                'creating_rules': [],
                'learning_weights': [],
                'total_structure_learning': [],
                'performing_inference': [],
                'performing_evaluation': [],
            },
            'standard_method': {
                'clustering': [],
                'getting_communities': [],
                'path_finding': [],
                'creating_rules': [],
                'learning_weights': [],
                'total_structure_learning': [],
                'performing_inference': [],
                'performing_evaluation': [],
            }
        }

        self.evaluation_statistics = {
            'standard_method': {
                'average_CLL': None,
                'average_formula_length': None,
                'average_number_of_formulas': None,
            },
            'hierarchical_clustering': {
                'average_CLL': None,
                'average_formula_length': None,
                'average_number_of_formulas': None,
            },
        }

        self.config = {
            'clustering_params': {
                'min_cluster_size': 10,
                'max_lambda2': 0.8,
            },
            'random_walk_params': {
                'num_walks': 10000,
                'max_length': 5,
                'theta_hit': 4.9,
                'theta_sym': 0.1,
                'theta_js': 1.0,
                'num_top': 3
            },
        }

    def evaluate(self, database_files, info_file, type_file):
        self.structure_learn_MLNs(database_files, info_file, type_file)
        self.run_inference_on_MLNs(database_files, info_file)
        self.evaluate_MLNs(database_files)
        self.write_log_file(database_files, info_file, type_file)

    def structure_learn_MLNs(self, database_files, info_file, type_file):
        for database in database_files:
            self._structure_learn_with_standard_method(database, info_file, type_file)
            self._structure_learn_with_hierarchical_clustering(database, info_file)

    def run_inference_on_MLNs(self, database_files, info_file):
        query_predicates = self.get_query_predicates(info_file)
        print('Running inference')
        for database in database_files:
            mln = database.rstrip('.db')
            evidence_database_files = ','.join(
                [os.path.join(self.data_dir, database_file) for database_file in database_files if
                 database_file != database])
            self.run_inference_on_MLN_by_method(mln, evidence_database_files, query_predicates, 'standard_method')
            self.run_inference_on_MLN_by_method(mln, evidence_database_files, query_predicates,
                                                'hierarchical_clustering')

    def evaluate_MLNs(self, database_file_names):
        print('Evaluating')
        standard_method_statistics = self.evaluate_MLNs_by_method(database_file_names, 'standard_method')
        hierarchical_clustering_statistics = self.evaluate_MLNs_by_method(database_file_names,
                                                                          'hierarchical_clustering')

        self.evaluation_statistics = {
            'standard_method': {
                'average_CLL': standard_method_statistics[0],
                'average_formula_length': standard_method_statistics[1],
                'average_number_of_formulas': standard_method_statistics[2],
            },
            'hierarchical_clustering': {
                'average_CLL': hierarchical_clustering_statistics[0],
                'average_formula_length': hierarchical_clustering_statistics[1],
                'average_number_of_formulas': hierarchical_clustering_statistics[2],
            },
        }

    def write_log_file(self, database_files, info_file, type_file):
        current_time = datetime.now()
        timestampStr = current_time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        with open(timestampStr + '.log', 'w') as log_file:
            self._write_data_files_log(log_file, database_files, info_file, type_file)
            self._write_config_log(log_file)
            self._write_timings_log(log_file)
            self._write_evaluation_log(log_file)

    def _structure_learn_with_standard_method(self, database, info_file, type_file):
        print('Structure Learning (Standard Method)')
        print(' Random walks...')
        save_name = database.rstrip('.db') + self.standard_method_suffix
        random_walks_command = f'{self.lsm_dir}/rwl/rwl {self.data_dir}/{info_file} {self.data_dir}/' \
                               f'{database} {self.data_dir}/{type_file} {self.config["num_walks"]} ' \
                               f'{self.config["max_length"]} 0.05 0.1 {self.config["theta_hit"]} ' \
                               f'{self.config["theta_sym"]} {self.config["theta_js"]} {self.config["num_top"]} 1 ' \
                               f'{self.data_dir}/{save_name}.ldb {self.data_dir}/{save_name}.uldb {self.data_dir}/' \
                               f'{save_name}.srcnclusts > {self.log_dir}/{save_name}-rwl.log'
        initial_time = time.time()
        subprocess.call(random_walks_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        clustering_time = time.time()
        self.time_statistics['standard_method']['clustering'].append(clustering_time - initial_time)
        self._run_rest_of_structure_learning_pipeline(database, info_file, save_name, method='standard_method')

        complete_time = time.time()
        self.time_statistics['standard_method']['total_structure_learning'].append(complete_time - initial_time)
        self._remove_temporary_files_produced_during_structure_learning()

    def _structure_learn_with_hierarchical_clustering(self, database, info_file):
        print('Structure Learning (Hierarchical Clustering)')
        print(' Random walks...')
        initial_time = time.time()
        self.generate_communities_using_hierarchical_clustering(database, info_file)
        clustering_time = time.time()
        self.time_statistics['hierarchical_clustering']['clustering'].append(clustering_time - initial_time)
        save_name = database.rstrip('.db') + self.hierarchical_clustering_suffix
        self._run_rest_of_structure_learning_pipeline(database, info_file, save_name, method='hierarchical_clustering')

        complete_time = time.time()
        self.time_statistics['hierarchical_clustering']['total_structure_learning'].append(complete_time - initial_time)
        self._remove_temporary_files_produced_during_structure_learning()

    def run_inference_on_MLN_by_method(self, mln: str, evidence_database_files: str,
                                       query_predicates: str, method: str):
        mln += self._get_file_suffix_from_method(method)
        initial_time = time.time()
        self.run_inference_on_MLN(mln, evidence_database_files, query_predicates)
        final_time = time.time()
        self.time_statistics[method]['performing_inference'].append(final_time - initial_time)

    def evaluate_MLNs_by_method(self, database_files, method):
        CLLs = []
        formula_lengths = []
        number_of_formulas = []
        time0 = time.time()
        for database_file in database_files:
            CLLs.append(self.compute_average_CLL_from_MLN(database_file, method))
            fl, nf = self.compute_average_formula_length_and_number_of_formulas(database_file, method)
            formula_lengths.append(fl)
            number_of_formulas.append(nf)
        time1 = time.time()
        self.time_statistics[method]['performing_evaluation'].append(time1 - time0)

        return [np.average(CLLs), np.average(formula_lengths), np.average(number_of_formulas)]

    def generate_communities_using_hierarchical_clustering(self, database_file, info_file):
        original_hypergraph = Hypergraph(os.path.join(self.data_dir, database_file), os.path.join(self.data_dir,
                                                                                                  info_file))
        hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph,
                                                       config=self.config['clustering_params'])
        hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()

        hypergraph_communities = []
        for hypergraph in hypergraph_clusters:
            hypergraph_communities.append(Communities(hypergraph, config=self.config['random_walk_params']))

        community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
                                             original_hypergraph=original_hypergraph)
        community_printer.write_files(file_name=os.path.join(self.data_dir, database_file.rstrip('.db') +
                                                             self.hierarchical_clustering_suffix))

    def _run_rest_of_structure_learning_pipeline(self, database, info_file, save_name, method):
        print(' Communities...')
        self._run_get_communities(info_file, save_name, method)
        print(' Paths...')
        self._run_path_finding(info_file, save_name, method)
        print(' Finding formulas...')
        self._run_create_MLN_rules(database, info_file, save_name, method)
        print(' Calculating weights..')
        self._run_learn_MLN_weights(database, save_name, method)

    def _remove_temporary_files_produced_during_structure_learning(self):
        cwd = os.getcwd()
        files_in_cwd = os.listdir(cwd)
        temp_files = [file for file in files_in_cwd if file.endswith("_tmpalchemy.mln")]
        self._delete_files(temp_files, parent_directory=cwd)
        if self.delete_generated_files:
            files_in_data_dir = os.listdir(self.data_dir)
            generated_files = [file for file in files_in_data_dir if
                               file.endswith(tuple(".ldb", ".uldb", '.srcnclusts'))]
            self._delete_files(generated_files, parent_directory=self.data_dir)

    def run_inference_on_MLN(self, mln: str, evidence_database_files: str, query_predicates: str):
        """
        Runs the Alchemy inference program on a specified MLN, given evidence databases.
        """
        mln_to_evaluate = os.path.join(self.mln_dir, mln + '-rules-out.mln')
        results_file = os.path.join(self.results_dir, mln + '.results')
        inference_command = f'{self.infer_dir}/infer -i {mln_to_evaluate} -r {results_file} -e ' \
                            f'{evidence_database_files} -q {query_predicates}'
        subprocess.call(inference_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    def get_query_predicates(self, info_file):
        """
        Reads from an info file a list of predicates to be used as queries for inference.

                smoking.info
                ----------------------
                Friends(person, person)
        e.g.    Smokes(person)             returns    'Friends, Smokes, Cancer'
                Cancer(person)
        """
        file = open(os.path.join(self.data_dir, info_file), 'r')
        query_atoms = []
        for line in file.readlines():
            comment_symbol = '//'
            if line[0:2] == comment_symbol:
                continue
            atom_name = line.split('(')[0]
            query_atoms.append(atom_name)

        query_atom_string = ','.join(query_atoms)
        return query_atom_string

    def compute_average_CLL_from_MLN(self, database_test_file, method):
        file_suffix = self._get_file_suffix_from_method(method)
        results_new_file = database_test_file.rstrip('.db') + f'{file_suffix}.results'
        results_new_dataframe = pd.read_csv(os.path.join(self.results_dir, results_new_file), delimiter=' ',
                                            names=['Ground_Atom', 'CLL'])
        return np.log(results_new_dataframe['CLL']).mean()

    def compute_average_formula_length_and_number_of_formulas(self, database_file, method):
        file_suffix = self._get_file_suffix_from_method(method)
        mln_file_name = database_file.rstrip('.db') + f'{file_suffix}-rules-out.mln'
        with open(os.path.join(self.mln_dir, mln_file_name), 'r') as mln_file:
            formula_lengths = []
            for line in mln_file.readlines():
                split_line = line.split('  ')
                try:
                    float(split_line[
                              0])  # Line corresponds to a formula if it starts with a floating point number (formula
                    # weight)
                    formula = split_line[1]
                    formula_length = len(formula.split(' '))
                    formula_lengths.append(formula_length)
                except:
                    continue  # Line was not a formula
            number_of_formulas = len(formula_lengths)

        return np.mean(formula_lengths), number_of_formulas

    def _run_get_communities(self, info_file, save_name, method):
        get_communities_command = f'{self.lsm_dir}/getcom/getcom {self.data_dir}/{save_name}.ldb {self.data_dir}/' \
                                  f'{save_name}.uldb {self.data_dir}/{save_name}.srcnclusts {self.data_dir}/' \
                                  f'{info_file} 10 {self.data_dir}/{save_name}.comb.ldb NOOP true 1 > ' \
                                  f'{self.log_dir}/{save_name}-getcom.log '
        time0 = time.time()
        subprocess.call(get_communities_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['getting_communities'].append(time1 - time0)

    def _run_path_finding(self, info_file, save_name, method):
        path_finding_command = f'{self.lsm_dir}/pfind2/pfind {self.data_dir}/{save_name}.comb.ldb 5 0 5 -1.0 ' \
                               f'{self.data_dir}/{info_file} {self.data_dir}/{save_name}.rules > ' \
                               f'{self.log_dir}/{save_name}-findpath.log'
        time0 = time.time()
        subprocess.call(path_finding_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['path_finding'].append(time1 - time0)

    def _run_create_MLN_rules(self, database, info_file, save_name, method):
        create_mln_rules_command = f'{self.lsm_dir}/createrules/createrules {self.data_dir}/{save_name}.rules 0 ' \
                                   f'{self.data_dir}/{database} {self.data_dir}/{save_name}.comb.ldb ' \
                                   f'{self.data_dir}/{save_name}.uldb {self.data_dir}/{info_file} ' \
                                   f'{self.lsm_dir}/alchemy30/bin/learnwts ' \
                                   f'{self.lsm_dir}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 {self.mln_dir}/' \
                                   f'{save_name}-rules.mln 1 - - true false 40 > {self.log_dir}/' \
                                   f'{save_name}-createrules.log'
        time0 = time.time()
        subprocess.call(create_mln_rules_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['creating_rules'].append(time1 - time0)

    def _run_learn_MLN_weights(self, database_name, save_name, method):
        learn_mln_weights_command = f'{self.lsm_dir}/alchemy30/bin/learnwts -g -i {self.mln_dir}/' \
                                    f'{save_name}-rules.mln -o {self.mln_dir}/{save_name}-rules-out.mln -t ' \
                                    f'{self.data_dir}/{database_name}'
        time0 = time.time()
        subprocess.call(learn_mln_weights_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['learning_weights'].append(time1 - time0)

    def _get_file_suffix_from_method(self, method):
        if method == 'standard_method':
            return self.standard_method_suffix
        elif method == 'hierarchical_clustering':
            return self.hierarchical_clustering_suffix
        else:
            raise ValueError('method variable must be either "standard_method" or "hierarchical_clustering"')

    @staticmethod
    def _delete_files(file_names, parent_directory):
        """
        Deletes every file in a given list of file_names found in the directory parent_directory.
        """
        for file in file_names:
            path_to_file = os.path.join(parent_directory, file)
            os.remove(path_to_file)

    @staticmethod
    def _write_data_files_log(log_file, database_files, info_file, type_file):
        log_file.write('\n')
        log_file.write('DATA FILES ------------------------------- \n')
        log_file.write(f'database_file_names = {database_files} \n')
        log_file.write(f'info_file = {info_file} \n')
        log_file.write(f'type_file = {type_file} \n \n')

    def _write_config_log(self, log_file):
        log_file.write('\n')
        log_file.write('CONFIG ----------------------------------- \n')
        json.dump(self.config, log_file, indent=4)
        log_file.write('\n')

    def _write_timings_log(self, log_file):
        log_file.write('\n')
        log_file.write('TIMINGS ---------------------------------- \n')
        json.dump(self.time_statistics, log_file, indent=4)
        log_file.write('\n')

    def _write_evaluation_log(self, log_file):
        log_file.write('\n')
        log_file.write('EVALUATION ------------------------------- \n')
        json.dump(self.evaluation_statistics, log_file, indent=4)
        log_file.write('\n')


if __name__ == "__main__":
    evaluator = MLNEvaluator()
    min_cluster_sizes = [10]  # , 5, 2]
    for min_cluster_size in min_cluster_sizes:
        evaluator.evaluate(database_files=['imdb1.db'], info_file='imdb.info', type_file='imdb.type')
