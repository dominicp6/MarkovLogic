import os
import pandas as pd
import numpy as np
import subprocess
import time
import json
import signal
import errno
import random
from functools import wraps
from datetime import datetime
from collections import defaultdict
from tqdm import tqdm
from typing import List

from GraphObjects import Hypergraph
from HierarchicalClusterer import HierarchicalClusterer
from Communities import Communities
from CommunityPrinter import CommunityPrinter


def timeout(seconds=7, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


class MLNEvaluator(object):
    def __init__(self,
                 hc_config=None,
                 sm_config=None,
                 only_alchemy=False,
                 only_new_algorithm=False,
                 with_clustering=True,
                 with_original_hyperparameters=False,
                 lsm_dir='lsmcode',
                 infer_dir='alchemy-2/bin',
                 data_dir='Evaluation/Data',
                 temp_dir='Evaluation/Temp',
                 mln_dir='Evaluation/MLNs',
                 log_dir='Evaluation/Log',
                 results_dir='Evaluation/Results',
                 experiments_dir='Evaluation/Experiments',
                 delete_generated_files=False,
                 seed=None,
                 ):

        self.only_alchemy = only_alchemy
        self.only_new_algorithm = only_new_algorithm
        self.with_clustering = with_clustering
        self.with_original_hyperparameters = with_original_hyperparameters

        self.lsm_dir = lsm_dir
        self.infer_dir = infer_dir
        self.data_dir = data_dir
        self.temp_dir = temp_dir
        self.mln_dir = mln_dir
        self.log_dir = log_dir
        self.results_dir = results_dir
        self.experiments_dir = experiments_dir

        self.delete_generated_files = delete_generated_files

        self.hierarchical_clustering_suffix = '_hc'  # file suffix used when running hierarchical clustering method
        self.alchemy_file_suffix = '_sm'  # file suffix used when running the standard method

        self.time_statistics = defaultdict(lambda: defaultdict(lambda: []))

        self.clustering_statistics = defaultdict(lambda: defaultdict(lambda: []))

        self.mln_statistics = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: [])))

        self.evaluation_statistics = defaultdict(lambda: defaultdict(lambda: []))

        self.inference_results = defaultdict(lambda: defaultdict(lambda: []))

        self.mln_name = None  # custom file name for the MLN

        if seed is None:
            self.seed = random.randint(0, 1000)
        else:
            self.seed = seed

        if hc_config is None:
            self.hc_config = {
                'clustering_params': {
                    'min_cluster_size': 10,
                    'max_lambda2': 0.8,
                },
                'random_walk_params': {
                    'epsilon': 0.05,
                    'max_num_paths': 3,
                    'pca_dim': 2,
                    'clustering_method_threshold': 50,
                    'max_path_length': 5,
                    'theta_p': 0.01,
                    'pruning_value': None,
                    'multiprocessing': True
                }
            }
        else:
            self.hc_config = hc_config

        if sm_config is None:
            self.sm_config = {
                "num_walks": 10000,
                "max_length": 5,
                "theta_hit": 4.9,
                "theta_sym": 0.1,
                "theta_js": 1,
                "num_top": 3,
            }
        else:
            self.sm_config = sm_config

        self.log_file_name = None

    def evaluate(self, database_files: List[str], info_file: str, type_file: str, mln_name=None):
        """
        Structure learns a MLN for each database in a list of database files.
        Evaluates the average conditional log likelihood of each MLN using leave-one-out cross-validation.
        """
        if len(database_files) == 1:
            self.mln_name = mln_name  # if a single database, the user can specify a custom mln name
        self.structure_learn_MLNs(database_files, info_file, type_file)
        self.evaluate_formula_statistics_of_MLNs(database_files)
        self.write_log_file(database_files, info_file, type_file)
        self.run_inference_on_MLNs(database_files, info_file)
        self._evaluate_CLL_of_MLNs()
        self._append_CLL_evaluation_to_log_file()
        print('Done')

    def evaluate_CLL_of_MLN(self, path_to_mln: str, paths_to_evidence_databases: List[str]):
        """
        Evaluates the average conditional log likelihood of a single MLN given evidence databases.
        """
        self.inference_results.clear()
        self.run_inference_on_MLN(mln=path_to_mln, evidence_database_files=paths_to_evidence_databases)
        self._evaluate_CLL_of_MLNs()
        self._write_CLL_log_file(mln=path_to_mln, evidence_databases=paths_to_evidence_databases)

    # STRUCTURE LEARNING FUNCTIONS ------------------------------------------------------------------------------------

    def structure_learn_MLNs(self, database_files: List[str], info_file: str, type_file: str):
        """
        Structure-learn an MLN from each database in the list of database files.
        """
        for database in database_files:
            if self.only_alchemy:
                self._structure_learn_using_Alchemy_algorithm(database, info_file, type_file)
            elif self.only_new_algorithm:
                self._structure_learn_using_new_algorithm(database, info_file)
            else:
                self._structure_learn_using_Alchemy_algorithm(database, info_file, type_file)
                self._structure_learn_using_new_algorithm(database, info_file)

    def _structure_learn_using_Alchemy_algorithm(self, database: str, info_file: str, type_file: str):
        print(f'Structure Learning {database} using Alchemy Algorithm')
        print(' Random walks...')
        save_name = database.rstrip('.db') + self.alchemy_file_suffix
        random_walks_command = f'{self.lsm_dir}/rwl/rwl {self.data_dir}/{info_file} {self.data_dir}/' \
                               f'{database} {self.data_dir}/{type_file} {self.sm_config["num_walks"]} ' \
                               f'{self.sm_config["max_length"]} 0.05 0.1 {self.sm_config["theta_hit"]} ' \
                               f'{self.sm_config["theta_sym"]} {self.sm_config["theta_js"]} ' \
                               f'{self.sm_config["num_top"]} {self.seed} {self.temp_dir}/{save_name}.ldb ' \
                               f'{self.temp_dir}/{save_name}.uldb {self.temp_dir}/{save_name}.srcnclusts > ' \
                               f'{self.log_dir}/{save_name}-rwl.log'
        initial_time = time.time()
        subprocess.call(random_walks_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        random_walks_time = time.time()
        self.time_statistics['alchemy_algorithm']['RWs'].append(random_walks_time - initial_time)
        self._run_rest_of_structure_learning_pipeline(database, info_file, save_name, algorithm='alchemy_algorithm')

        complete_time = time.time()
        self.time_statistics['alchemy_algorithm']['total_structure_learning'].append(complete_time - initial_time)
        self._remove_temporary_files_produced_during_structure_learning()

    def _structure_learn_using_new_algorithm(self, database: str, info_file: str):
        print(f'Structure Learning {database} using New Algorithm')
        print(' Random walks...')
        initial_time = time.time()
        self.generate_communities_using_hierarchical_clustering(database, info_file)
        clustering_time = time.time()
        self.time_statistics['new_algorithm']['clustering_and_RWs'].append(clustering_time - initial_time)
        save_name = database.rstrip('.db') + self.hierarchical_clustering_suffix
        self._run_rest_of_structure_learning_pipeline(database, info_file, save_name, algorithm='new_algorithm')

        complete_time = time.time()
        self.time_statistics['new_algorithm']['total_structure_learning'].append(complete_time - initial_time)
        self._remove_temporary_files_produced_during_structure_learning()

    def _run_rest_of_structure_learning_pipeline(self, database, info_file, save_name, algorithm):
        print(' Communities...')
        self._run_get_communities(info_file, save_name, algorithm)
        print(' Paths...')
        self._run_path_finding(info_file, save_name, algorithm)
        print(' Finding formulas...')
        self._run_create_MLN_rules(database, info_file, save_name, algorithm)
        print(' Calculating weights..')
        self._run_learn_MLN_weights(database, save_name, algorithm)

    def _run_get_communities(self, info_file, save_name, algorithm):
        get_communities_command = f'{self.lsm_dir}/getcom/getcom {self.temp_dir}/{save_name}.ldb {self.temp_dir}/' \
                                  f'{save_name}.uldb {self.temp_dir}/{save_name}.srcnclusts {self.data_dir}/' \
                                  f'{info_file} 10 {self.temp_dir}/{save_name}.comb.ldb NOOP true {self.seed} ' \
                                  f'> {self.log_dir}/{save_name}-getcom.log '
        time0 = time.time()
        subprocess.call(get_communities_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[algorithm]['getting_communities'].append(time1 - time0)

    def _run_path_finding(self, info_file, save_name, algorithm):
        path_finding_command = f'{self.lsm_dir}/pfind2/pfind {self.temp_dir}/{save_name}.comb.ldb 5 0 5 -1.0 ' \
                               f'{self.data_dir}/{info_file} {self.temp_dir}/{save_name}.rules > ' \
                               f'{self.log_dir}/{save_name}-findpath.log'
        time0 = time.time()
        subprocess.call(path_finding_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[algorithm]['path_finding'].append(time1 - time0)

    def _run_create_MLN_rules(self, database: str, info_file: str, save_name: str, algorithm: str):
        create_mln_rules_command = f'{self.lsm_dir}/createrules/createrules {self.temp_dir}/{save_name}.rules 0 ' \
                                   f'{self.data_dir}/{database} {self.temp_dir}/{save_name}.comb.ldb ' \
                                   f'{self.temp_dir}/{save_name}.uldb {self.data_dir}/{info_file} ' \
                                   f'{self.lsm_dir}/alchemy30/bin/learnwts ' \
                                   f'{self.lsm_dir}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 {self.temp_dir}/' \
                                   f'{save_name}-rules.mln {self.seed} - - true false 40 > {self.log_dir}/' \
                                   f'{save_name}-createrules.log'
        time0 = time.time()
        subprocess.call(create_mln_rules_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[algorithm]['creating_rules'].append(time1 - time0)

    def _run_learn_MLN_weights(self, database_name: str, save_name: str, algorithm: str):
        if self.mln_name is not None:
            save_name = self.mln_name
        learn_mln_weights_command = f'{self.lsm_dir}/alchemy30/bin/learnwts -g -i {self.temp_dir}/' \
                                    f'{save_name}-rules.mln -o {self.mln_dir}/{save_name}-rules-out.mln -t ' \
                                    f'{self.data_dir}/{database_name}'
        time0 = time.time()
        subprocess.call(learn_mln_weights_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[algorithm]['learning_weights'].append(time1 - time0)

    def generate_communities_using_hierarchical_clustering(self, database_file: str, info_file: str):
        original_hypergraph = Hypergraph(os.path.join(self.data_dir, database_file), os.path.join(self.data_dir,
                                                                                                  info_file))
        if self.with_clustering:
            hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph,
                                                           config=self.hc_config['clustering_params'])
            hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()

            hypergraph_communities = []
            for hypergraph in hypergraph_clusters:
                if self.with_original_hyperparameters:
                    hypergraph_communities.append(Communities(hypergraph, config=self.hc_config['random_walk_params'],
                                                              num_walks=self.sm_config['num_walks'],
                                                              walk_length=self.sm_config['max_length'],
                                                              theta_hit=self.sm_config['theta_hit'],
                                                              theta_sym=self.sm_config['theta_sym'],
                                                              theta_js=self.sm_config['theta_js']))
                else:
                    hypergraph_communities.append(Communities(hypergraph, config=self.hc_config['random_walk_params']))
        else:
            if self.with_original_hyperparameters:
                hypergraph_communities = [Communities(original_hypergraph, config=self.hc_config['random_walk_params'],
                                                      num_walks=self.sm_config['num_walks'],
                                                      walk_length=self.sm_config['max_length'],
                                                      theta_hit=self.sm_config['theta_hit'],
                                                      theta_sym=self.sm_config['theta_sym'],
                                                      theta_js=self.sm_config['theta_js'])]
            else:
                hypergraph_communities = [Communities(original_hypergraph, config=self.hc_config['random_walk_params'])]

        self._populate_clustering_statistics_dictionary(database_file, hypergraph_communities)

        community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
                                             original_hypergraph=original_hypergraph)
        community_printer.write_files(file_name=os.path.join(self.temp_dir, database_file.rstrip('.db') +
                                                             self.hierarchical_clustering_suffix))

    # INFERENCE FUNCTIONS ---------------------------------------------------------------------------------------------

    def run_inference_on_MLNs(self, database_files: List[str], info_file: str):
        query_predicates = self._get_query_predicates(info_file)

        for database in database_files:
            print(f'Running inference on {database}')
            mln = database.rstrip('.db')
            # evidence databases are all other databases not used to generate the MLN
            evidence_database_files = [os.path.join(self.data_dir, database_file) for database_file in database_files if
                                       database_file != database]
            if self.only_alchemy:
                self.run_inference_on_MLN_by_method(mln, evidence_database_files, 'alchemy_algorithm')
            elif self.only_new_algorithm:
                self.run_inference_on_MLN_by_method(mln, evidence_database_files, 'new_algorithm')
            else:
                self.run_inference_on_MLN_by_method(mln, evidence_database_files, 'alchemy_algorithm')
                self.run_inference_on_MLN_by_method(mln, evidence_database_files, 'new_algorithm')

    def run_inference_on_MLN_by_method(self, mln: str, evidence_database_files: List[str], algorithm: str):
        initial_time = time.time()
        self.run_inference_on_MLN(mln, evidence_database_files)
        final_time = time.time()
        self.time_statistics[algorithm]['performing_inference'].append(final_time - initial_time)

    def run_inference_on_MLN(self, mln: str, evidence_database_files: List[str]):
        """
        Runs the Alchemy inference program on a specified MLN, given evidence databases.
        """
        mln_to_evaluate = os.path.join(self.mln_dir, mln + '-rules-out.mln')

        for evidence_database in evidence_database_files:
            print(f"... {evidence_database} as evidence database")
            self.run_inference_on_database(evidence_database, mln_to_evaluate)

        return None

    def run_inference_on_database(self, evidence_database, mln):
        with open(evidence_database) as evidence_file:
            file_lines = evidence_file.readlines()
            for line in tqdm(file_lines):
                if line != "\n":
                    temp_database = \
                        self._create_evidence_database_with_line_removed(evidence_database, file_lines, line)

                    try:
                        CLL = self.run_inference_on_literal(literal=line.rstrip(),
                                                            mln=mln,
                                                            trimmed_evidence_database=temp_database)
                    except:
                        CLL = None
                        print(f'TimeOut Error on {line.rstrip()}')

                    os.remove(temp_database)

                    if CLL is not None:
                        predicate = line.split('(')[0]
                        self._update_CLL_dict(predicate, CLL, mln)

    @timeout()
    def run_inference_on_literal(self, literal, mln, trimmed_evidence_database):
        results_file = os.path.join(self.results_dir, 'temp.results')

        inference_command = f'{self.infer_dir}/infer -i {mln} -r {results_file} -e ' \
                            f'{trimmed_evidence_database} -q "{literal}"'
        subprocess.call(inference_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        shell=True)
        CLL = self._get_CLL_from_file(results_file)

        return CLL

    # EVALUATION FUNCTIONS --------------------------------------------------------------------------------------------

    def evaluate_formula_statistics_of_MLNs(self, database_files: List[str]):
        """
        Computes the average formula length and number of formulas for each MLN associated with each database file.
        """
        if not self.only_new_algorithm:
            self.evaluate_formula_statistics(database_files, 'alchemy_algorithm')
        self.evaluate_formula_statistics(database_files, 'new_algorithm')

    def evaluate_formula_statistics(self, database_files: List[str], algorithm: str):
        formula_lengths = []
        std_formula_lengths = []
        number_of_formulas = []

        for database_file in database_files:
            fl, std_fl, nf = self.compute_average_and_std_formula_length_and_number_of_formulas(database_file,
                                                                                                algorithm)
            self.mln_statistics[algorithm][database_file]["formula_length"] = [fl, std_fl]
            self.mln_statistics[algorithm][database_file]["number_of_formulas"] = [nf]
            formula_lengths.append(fl)
            number_of_formulas.append(nf)
            std_formula_lengths.append(std_fl)
        self.mln_statistics[algorithm]["average"]["formula_length"] = [np.mean(formula_lengths),
                                                                       np.sqrt(sum([x ** 2 for x in
                                                                                    std_formula_lengths]))
                                                                       / np.sqrt(sum(number_of_formulas))]
        self.mln_statistics[algorithm]["average"]["number_of_formulas"] = [np.mean(number_of_formulas),
                                                                           np.std(number_of_formulas) / np.sqrt(
                                                                               len(number_of_formulas))]

    def compute_average_and_std_formula_length_and_number_of_formulas(self, database_file, algorithm):
        file_suffix = self._get_file_suffix_from_method(algorithm)
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

        return np.mean(formula_lengths), np.std(formula_lengths), number_of_formulas

    def _evaluate_CLL_of_MLNs(self):
        """
        Computes average conditional log likelihoods from the inference results.
        """
        average_CLL_dict = defaultdict(lambda: [])
        for mln in self.inference_results.keys():
            for predicate in self.inference_results[mln].keys():
                self.evaluation_statistics[mln][predicate] = [np.mean(self.inference_results[mln][predicate]),
                                                              np.std(self.inference_results[mln][predicate]) / np.sqrt(
                                                                  len(self.inference_results[mln][predicate]))]
                average_CLL_dict[predicate].extend(self.inference_results[mln][predicate])

        for predicate in average_CLL_dict.keys():
            mean = np.mean(average_CLL_dict[predicate])
            std = np.std(average_CLL_dict[predicate]) / np.sqrt(len(average_CLL_dict[predicate]))
            average_CLL_dict[predicate] = [mean, std]

        self.evaluation_statistics['average'] = average_CLL_dict

    def write_log_file(self, database_files: List[str], info_file: str, type_file: str):
        current_time = datetime.now()
        timestampStr = current_time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        self.log_file_name = self.experiments_dir + '/' + timestampStr + '.log'
        with open(self.log_file_name, 'w') as log_file:
            self._write_data_files_log(log_file, database_files, info_file, type_file)
            self._write_config_log(log_file)
            self._write_clustering_log(log_file)
            self._write_timings_log(log_file)
            self._write_MLN_log(log_file)

    def _populate_clustering_statistics_dictionary(self, database_file: str, hypergraph_communities: List[Communities]):
        self.clustering_statistics[database_file]['number_of_clusters'] = [len(hypergraph_communities)]
        self.clustering_statistics[database_file]['size_of_clusters'] = \
            [hypergraph_community.hypergraph.number_of_nodes() for hypergraph_community in hypergraph_communities]
        self.clustering_statistics[database_file]['average_cluster_size'] = \
            [np.mean(self.clustering_statistics[database_file]['size_of_clusters'])]

        self.clustering_statistics[database_file]['community_sizes'] = \
            [[len(com) for com in hypergraph_community.communities.values()]
             for hypergraph_community in hypergraph_communities]
        self.clustering_statistics[database_file]['number_of_communities'] = \
            [sum([len(community_size) for community_size in
                  self.clustering_statistics[database_file]['community_sizes']])]
        self.clustering_statistics[database_file]['mean_community_size_by_cluster'] = \
            [np.mean(com_len_list) for com_len_list in self.clustering_statistics[database_file]['community_sizes']]
        self.clustering_statistics[database_file]['mean_community_size'] = \
            [np.mean(
                [item for sublist in self.clustering_statistics[database_file]['community_sizes'] for item in sublist])]
        number_of_single_nodes = []
        [number_of_single_nodes.extend([com.number_of_single_nodes
                                        for com in hypergraph_community.communities.values()])
         for hypergraph_community in hypergraph_communities]
        number_of_node_clusters = []
        [number_of_node_clusters.extend([com.number_of_clusters
                                         for com in hypergraph_community.communities.values()])
         for hypergraph_community in hypergraph_communities]
        self.clustering_statistics[database_file]['mean_number_single_nodes'] = [np.mean(number_of_single_nodes)]
        self.clustering_statistics[database_file]['mean_number_node_clusters'] = [np.mean(number_of_node_clusters)]
        del self.clustering_statistics[database_file]['community_sizes']

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

    # WRITING LOG FILES ----------------------------------------------------------------------------------------------

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
        log_file.write(f'only_new_algorithm             {self.only_new_algorithm} \n')
        log_file.write(f'with_clustering                {self.with_clustering} \n')
        log_file.write(f'with_original_hyperparameters  {self.with_original_hyperparameters} \n')
        json.dump(self.hc_config, log_file, indent=4)
        if not self.only_new_algorithm:
            log_file.write('\n')
            json.dump(self.sm_config, log_file, indent=4)
        log_file.write('\n')

    def _write_clustering_log(self, log_file):
        log_file.write('\n')
        log_file.write('CLUSTERING ------------------------------- \n')
        json.dump(self.clustering_statistics, log_file, indent=4)

    def _write_timings_log(self, log_file):
        log_file.write('\n')
        log_file.write('TIMINGS ---------------------------------- \n')
        json.dump(self.time_statistics, log_file, indent=4)
        log_file.write('\n')

    def _write_MLN_log(self, log_file):
        log_file.write('\n')
        log_file.write('MLN STATS -------------------------------- \n')
        json.dump(self.mln_statistics, log_file, indent=4)
        log_file.write('\n')

    def _append_CLL_evaluation_to_log_file(self):
        with open(self.log_file_name, 'a') as log_file:
            log_file.write('\n')
            log_file.write('EVALUATION ------------------------------- \n')
            json.dump(self.evaluation_statistics, log_file, indent=4)
            log_file.write('\n')

    def _write_CLL_log_file(self, mln, evidence_databases):
        current_time = datetime.now()
        timestampStr = current_time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        self.log_file_name = self.experiments_dir + '/' + 'CLL_eval_' + timestampStr + '.log'
        with open(self.log_file_name, 'w') as log_file:
            log_file.write('CLL EVALUTATION ------------------------------ \n')
            log_file.write(f'mln = {mln}\n')
            log_file.write(f'evidence_databases = {evidence_databases}\n')
            log_file.write('\n')
            json.dump(self.evaluation_statistics, log_file, indent=4)

    # HELPER FUNCTIONS -----------------------------------------------------------------------------------------------

    @staticmethod
    def _create_evidence_database_with_line_removed(evidence_database: str,
                                                    lines_of_evidence_database: List[str],
                                                    line: str):
        literal_string = line.replace("(", "").replace(")", "").replace(",", "").rstrip()
        file_lines_without_target_literal = lines_of_evidence_database.copy()
        file_lines_without_target_literal.remove(line)
        temp_evidence_db = f"{evidence_database.split('/')[-1].strip('.db')}_minus_{literal_string}.db"
        with open(temp_evidence_db, "w") as trimmed_evidence_database:
            for evidence_atom in file_lines_without_target_literal:
                trimmed_evidence_database.write(evidence_atom)

        return temp_evidence_db

    @staticmethod
    def _get_CLL_from_file(file):
        results_new_dataframe = pd.read_csv(file,
                                            delimiter=' ',
                                            names=['Ground_Atom', 'probability'])
        try:
            probability = results_new_dataframe['probability'][0]
            if probability > 0:
                CLL = np.log(probability)
            else:
                CLL = None
        except:
            CLL = None

        return CLL

    def _update_CLL_dict(self, predicate, CLL, mln):
        self.inference_results[mln][predicate].append(CLL)
        self.inference_results[mln]['average'].append(CLL)

    def _get_query_predicates(self, info_file: str):
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

    def _get_file_suffix_from_method(self, algorithm: str):
        if algorithm == 'alchemy_algorithm':
            return self.alchemy_file_suffix
        elif algorithm == 'new_algorithm':
            return self.hierarchical_clustering_suffix
        else:
            raise ValueError('method variable must be either "alchemy_algorithm" or "new_algorithm"')

    @staticmethod
    def _delete_files(file_names, parent_directory):
        """
        Deletes every file in a given list of file_names found in the directory parent_directory.
        """
        for file in file_names:
            path_to_file = os.path.join(parent_directory, file)
            os.remove(path_to_file)


if __name__ == "__main__":
    evaluator = MLNEvaluator(only_new_algorithm=True, with_clustering=True, with_original_hyperparameters=False)
    # for database in ['imdb1.db','imdb4.db', 'imdb5.db']:
    evaluator.evaluate(database_files=['imdb1.db'],
                       info_file='imdb.info', type_file='imdb.type')
    # evaluator.evaluate_MLNs(database_file_names=['imdb1.db', 'imdb2.db'])
    # evaluator.run_inference_on_MLN('imdb1_sm', ['./Data/imdb2.db'])
    #evaluator.evaluate_CLL_of_MLN('imdb3_hc', ['./Data/imdb2.db', './Data/imdb4.db', './Data/imdb5.db'])
