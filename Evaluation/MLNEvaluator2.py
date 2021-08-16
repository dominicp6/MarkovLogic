import os
import numpy as np
import subprocess
import time
import json
import random
import signal
import errno
import pandas as pd
from tqdm import tqdm
from functools import wraps
from datetime import datetime
from collections import defaultdict
from typing import List

from HierarchicalClustering.GraphObjects import Hypergraph
from HierarchicalClustering.HierarchicalClusterer import HierarchicalClusterer
from HierarchicalClustering.Communities import Communities
from HierarchicalClustering.CommunityPrinter import CommunityPrinter


def timeout(seconds=100, error_message=os.strerror(errno.ETIME)):
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
                 config,
                 save_name=None,
                 lsm_dir='lsmcode',
                 infer_dir='alchemy-2/bin',
                 data_dir='Evaluation/Data',
                 temp_dir='Evaluation/Temp',
                 mln_dir='Evaluation/MLNs',
                 log_dir='Evaluation/Log',
                 results_dir='Evaluation/Results',
                 experiments_dir='Evaluation/Experiments2',
                 delete_generated_files=False,
                 seed=None,
                 ):

        self.config = config
        self.save_name = save_name

        self.lsm_dir = lsm_dir
        self.infer_dir = infer_dir
        self.data_dir = data_dir
        self.temp_dir = temp_dir
        self.mln_dir = mln_dir
        self.log_dir = log_dir
        self.results_dir = results_dir
        self.experiments_dir = experiments_dir

        self.delete_generated_files = delete_generated_files

        self.time_statistics = {}

        self.clustering_statistics = defaultdict(lambda: [])

        self.mln_statistics = {}

        self.inference_results = defaultdict(lambda: [])

        self.CLL_evaluation_statistics = defaultdict(lambda: [])

        self.mln_name = None  # custom file name for the MLN

        if seed is None:
            self.seed = random.randint(0, 1000)
        else:
            self.seed = seed

        self.log_file_name = None

    def evaluate(self,
                 database: str,
                 info_file: str,
                 output_log_file=False,
                 perform_inference=False,
                 test_databases=None):
        """
        Structure learns a MLN for each database in a list of database files.
        Evaluates the average conditional log likelihood of each MLN using leave-one-out cross-validation.
        """
        self.structure_learn_MLN(database, info_file)
        if self.time_statistics['total_structure_learning'] != -1:
            self.evaluate_formula_statistics_of_MLN(database)
            if perform_inference:
                assert test_databases is not None, "If performing inference, then need non-empty test databases."
                self.run_inference_on_MLN(database, test_databases)
        else:
            self.mln_statistics['formula_length'] = -1
            self.mln_statistics['number_of_formulas'] = -1
            self.mln_statistics['weighted_ave_formula_length'] = -1

        if output_log_file:
            self.write_log_file(database, info_file)

        if perform_inference:
            return {'num_single_nodes': self.clustering_statistics['mean_number_single_nodes'],
                    'num_clusters': self.clustering_statistics['mean_number_node_clusters'],
                    'time_random_walks': self.time_statistics['clustering_and_RWs'],
                    'time_structure_learning': self.time_statistics['total_structure_learning'],
                    'length_of_formulas': self.mln_statistics['formula_length'],
                    'weighted_ave_formula_length': self.mln_statistics['weighted_ave_formula_length'],
                    'number_of_formulas': self.mln_statistics['number_of_formulas'],
                    'CLL': self.CLL_evaluation_statistics['average']}
        else:
            return {'num_single_nodes': self.clustering_statistics['mean_number_single_nodes'],
                    'num_clusters': self.clustering_statistics['mean_number_node_clusters'],
                    'time_random_walks': self.time_statistics['clustering_and_RWs'],
                    'time_structure_learning': self.time_statistics['total_structure_learning'],
                    'length_of_formulas': self.mln_statistics['formula_length'],
                    'weighted_ave_formula_length': self.mln_statistics['weighted_ave_formula_length'],
                    'number_of_formulas': self.mln_statistics['number_of_formulas']}

    # STRUCTURE LEARNING FUNCTIONS ------------------------------------------------------------------------------------

    def structure_learn_MLN(self, database: str, info_file: str):
        """
        Structure-learn an MLN from each database in the list of database files.
        """
        initial_time = time.time()
        self.generate_communities_using_hierarchical_clustering(database, info_file)
        clustering_time = time.time()
        self.time_statistics['clustering_and_RWs'] = (clustering_time - initial_time)
        if self.save_name is None:
            self.save_name = database.rstrip('.db')
        try:
            self._run_rest_of_structure_learning_pipeline(database, info_file)
            complete_time = time.time()
            self.time_statistics['total_structure_learning'] = (complete_time - initial_time)
        except:
            self.time_statistics['total_structure_learning'] = -1

        self._remove_temporary_files_produced_during_structure_learning()

    @timeout()
    def _run_rest_of_structure_learning_pipeline(self, database, info_file):
        self._run_get_communities(info_file)
        self._run_path_finding(info_file)
        self._run_create_MLN_rules(database, info_file)
        self._run_learn_MLN_weights(database)

    def _run_get_communities(self, info_file):
        get_communities_command = f'{self.lsm_dir}/getcom/getcom {self.temp_dir}/{self.save_name}.ldb {self.temp_dir}/' \
                                  f'{self.save_name}.uldb {self.temp_dir}/{self.save_name}.srcnclusts {self.data_dir}/' \
                                  f'{info_file} 10 {self.temp_dir}/{self.save_name}.comb.ldb NOOP true {self.seed} ' \
                                  f'> {self.log_dir}/{self.save_name}-getcom.log '
        time0 = time.time()
        subprocess.call(get_communities_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['getting_communities'] = (time1 - time0)

    def _run_path_finding(self, info_file):
        path_finding_command = f'{self.lsm_dir}/pfind2/pfind {self.temp_dir}/{self.save_name}.comb.ldb 5 0 5 -1.0 ' \
                               f'{self.data_dir}/{info_file} {self.temp_dir}/{self.save_name}.rules > ' \
                               f'{self.log_dir}/{self.save_name}-findpath.log'
        time0 = time.time()
        subprocess.call(path_finding_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['path_finding'] = (time1 - time0)

    def _run_create_MLN_rules(self, database: str, info_file: str):
        create_mln_rules_command = f'{self.lsm_dir}/createrules/createrules {self.temp_dir}/{self.save_name}.rules 0 ' \
                                   f'{self.data_dir}/{database} {self.temp_dir}/{self.save_name}.comb.ldb ' \
                                   f'{self.temp_dir}/{self.save_name}.uldb {self.data_dir}/{info_file} ' \
                                   f'{self.lsm_dir}/alchemy30/bin/learnwts ' \
                                   f'{self.lsm_dir}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 {self.temp_dir}/' \
                                   f'{self.save_name}-rules.mln {self.seed} - - true false 40 > {self.log_dir}/' \
                                   f'{self.save_name}-createrules.log'
        time0 = time.time()
        subprocess.call(create_mln_rules_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['creating_rules'] = (time1 - time0)

    def _run_learn_MLN_weights(self, database_name: str):
        learn_mln_weights_command = f'{self.lsm_dir}/alchemy30/bin/learnwts -g -i {self.temp_dir}/' \
                                    f'{self.save_name}-rules.mln -o {self.mln_dir}/{self.save_name}-rules-out.mln -t ' \
                                    f'{self.data_dir}/{database_name}'
        time0 = time.time()
        subprocess.call(learn_mln_weights_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['learning_weights'] = (time1 - time0)

    def generate_communities_using_hierarchical_clustering(self, database: str, info_file: str):
        original_hypergraph = Hypergraph(os.path.join(self.data_dir, database), os.path.join(self.data_dir,
                                                                                             info_file))
        if self.config['hierarchical_clustering']:
            hierarchical_clusterer = HierarchicalClusterer(hypergraph=original_hypergraph, config=self.config)
            hypergraph_clusters = hierarchical_clusterer.run_hierarchical_clustering()

            hypergraph_communities = []
            for hypergraph in hypergraph_clusters:
                if self.config['computed_hyperparameters']:
                    hypergraph_communities.append(Communities(hypergraph, config=self.config))
                else:
                    hypergraph_communities.append(Communities(hypergraph, config=self.config,
                                                              use_js_div=self.config['use_js_div'],
                                                              num_walks=self.config['num_walks'],
                                                              walk_length=self.config['length_of_walks'],
                                                              theta_hit=self.config['theta_hit'],
                                                              theta_sym=self.config['theta_sym'],
                                                              merging_threshold=self.config['theta_js']))
        else:
            if self.config['computed_hyperparameters']:
                hypergraph_communities = [Communities(original_hypergraph, config=self.config)]
            else:
                hypergraph_communities = [Communities(original_hypergraph, config=self.config,
                                                      use_js_div=self.config['use_js_div'],
                                                      num_walks=self.config['num_walks'],
                                                      walk_length=self.config['length_of_walks'],
                                                      theta_hit=self.config['theta_hit'],
                                                      theta_sym=self.config['theta_sym'],
                                                      merging_threshold=self.config['theta_js'])]

        self._populate_clustering_statistics_dictionary(hypergraph_communities)

        community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
                                             original_hypergraph=original_hypergraph)
        community_printer.write_files(file_name=os.path.join(self.temp_dir, self.save_name))

    # EVALUATION FUNCTIONS --------------------------------------------------------------------------------------------

    def evaluate_formula_statistics_of_MLN(self, database: str):
        """
        Computes the average formula length and number of formulas for each MLN associated with each database file.
        """
        fl, std_fl, wfl, nf = self.compute_average_and_std_formula_length_and_number_of_formulas(database)
        self.mln_statistics["formula_length"] = fl
        self.mln_statistics["number_of_formulas"] = nf
        self.mln_statistics["weighted_ave_formula_length"] = wfl

    def compute_average_and_std_formula_length_and_number_of_formulas(self, database):
        mln_file_name = self.save_name + '-rules-out.mln'
        with open(os.path.join(self.mln_dir, mln_file_name), 'r') as mln_file:
            formula_lengths = []
            weighted_formula_lengths = []
            formula_weights = []
            for line in mln_file.readlines():
                split_line = line.split('  ')
                try:
                    w = float(split_line[
                                  0])  # Line corresponds to a formula if it starts with a floating point number (formula
                    # weight)
                    formula = split_line[1]
                    formula_length = len(formula.split(' v'))
                    formula_weight = np.exp(w)
                    weighted_formula_length = formula_length * formula_weight
                    formula_weights.append(formula_weight)
                    formula_lengths.append(formula_length)
                    weighted_formula_lengths.append(weighted_formula_length)
                except:
                    continue  # Line was not a formula
            number_of_formulas = len(formula_lengths)

        try:
            mean_weighted_formula_length = sum(weighted_formula_lengths) / sum(formula_weights)
        except:
            mean_weighted_formula_length = 0

        return np.mean(formula_lengths), np.std(formula_lengths), mean_weighted_formula_length, number_of_formulas

    def write_log_file(self, database: str, info_file: str):
        current_time = datetime.now()
        timestampStr = current_time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        self.log_file_name = self.experiments_dir + '/' + timestampStr + '.log'
        with open(self.log_file_name, 'w') as log_file:
            self._write_data_files_log(log_file, database, info_file)
            self._write_config_log(log_file)
            self._write_clustering_log(log_file)
            self._write_timings_log(log_file)
            self._write_MLN_log(log_file)

    def _populate_clustering_statistics_dictionary(self, hypergraph_communities: List[Communities]):
        self.clustering_statistics['number_of_clusters'] = [len(hypergraph_communities)]
        self.clustering_statistics['size_of_clusters'] = \
            [hypergraph_community.hypergraph.number_of_nodes() for hypergraph_community in hypergraph_communities]
        self.clustering_statistics['average_cluster_size'] = \
            [np.mean(self.clustering_statistics['size_of_clusters'])]

        self.clustering_statistics['community_sizes'] = \
            [[len(com) for com in hypergraph_community.communities.values()]
             for hypergraph_community in hypergraph_communities]
        self.clustering_statistics['number_of_communities'] = \
            [sum([len(community_size) for community_size in
                  self.clustering_statistics['community_sizes']])]
        self.clustering_statistics['mean_community_size_by_cluster'] = \
            [np.mean(com_len_list) for com_len_list in self.clustering_statistics['community_sizes']]
        self.clustering_statistics['mean_community_size'] = \
            [np.mean(
                [item for sublist in self.clustering_statistics['community_sizes'] for item in sublist])]
        number_of_single_nodes = []
        [number_of_single_nodes.extend([com.number_of_single_nodes
                                        for com in hypergraph_community.communities.values()])
         for hypergraph_community in hypergraph_communities]
        number_of_node_clusters = []
        [number_of_node_clusters.extend([com.number_of_clusters
                                         for com in hypergraph_community.communities.values()])
         for hypergraph_community in hypergraph_communities]
        self.clustering_statistics['mean_number_single_nodes'] = [np.mean(number_of_single_nodes)]
        self.clustering_statistics['mean_number_node_clusters'] = [np.mean(number_of_node_clusters)]
        del self.clustering_statistics['community_sizes']

    def _remove_temporary_files_produced_during_structure_learning(self):
        cwd = os.getcwd()
        pard = os.path.dirname(cwd)
        files_in_cwd = os.listdir(cwd)
        temp_files = [file for file in files_in_cwd if file.endswith("_tmpalchemy.mln")]
        self._delete_files(temp_files, parent_directory=cwd)
        self._delete_files(temp_files, parent_directory=pard)
        if self.delete_generated_files:
            files_in_data_dir = os.listdir(self.data_dir)
            generated_files = [file for file in files_in_data_dir if
                               file.endswith(tuple(".ldb", ".uldb", '.srcnclusts'))]
            self._delete_files(generated_files, parent_directory=self.data_dir)

    # INFERENCE FUNCTIONS --------------------------------------------------------------------------------------------
    # TODO: update log files with inference results
    def run_inference_on_MLN(self, database: str, evidence_database_files: List[str]):
        """
        Runs the Alchemy inference program on a specified MLN, given evidence databases.
        """

        mln_to_evaluate = os.path.join(self.mln_dir, self.save_name + '-rules-out.mln')

        file_lines = []
        for evidence_database in evidence_database_files:
            with open(f'{self.data_dir}/{evidence_database}') as evidence_file:
                file_lines.extend([line.strip() for line in evidence_file.readlines()])

        for line in tqdm(file_lines, position=0, leave=True):
            if line != "\n":
                temp_database = \
                    self._create_database_with_line_removed(file_lines, line)

                try:
                    CLL = self.run_inference_on_literal(literal=line.rstrip(),
                                                        mln=mln_to_evaluate,
                                                        trimmed_evidence_database=temp_database)
                except:
                    CLL = None
                    print(f'TimeOut Error on {line.rstrip()}')

                os.remove(temp_database)

                if CLL is not None:
                    predicate = line.split('(')[0]
                    self._update_CLL_dict(predicate, CLL)

        self._evaluate_average_CLL()

        return None

    @timeout()
    def run_inference_on_literal(self, literal, mln, trimmed_evidence_database):
        results_file = os.path.join(self.results_dir, 'temp.results')

        inference_command = f'{self.infer_dir}/infer -i {mln} -r {results_file} -e ' \
                            f'{trimmed_evidence_database} -q "{literal}"'
        subprocess.call(inference_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        shell=True)
        CLL = self._get_CLL_from_file(results_file)

        return CLL

    @staticmethod
    def _create_database_with_line_removed(lines_of_database: List[str],
                                           line_to_remove: str):

        literal_string = line_to_remove.replace("(", "").replace(")", "").replace(",", "").rstrip()
        file_lines_without_target_literal = lines_of_database.copy()
        file_lines_without_target_literal.remove(line_to_remove)
        temp_db = f"minus_{literal_string}.db"
        with open(temp_db, "w") as temp_database:
            for evidence_atom in file_lines_without_target_literal:
                temp_database.write(evidence_atom + '\n')

        return temp_db

    def _evaluate_average_CLL(self):
        """
        Computes average conditional log likelihoods from the inference results.
        """
        for predicate in self.inference_results.keys():
            self.CLL_evaluation_statistics[predicate] = [np.mean(self.inference_results[predicate]),
                                                         np.std(self.inference_results[predicate]) / np.sqrt(
                                                             len(self.inference_results[predicate]))]

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

    def _update_CLL_dict(self, predicate, CLL):
        self.inference_results[predicate].append(CLL)
        self.inference_results['average'].append(CLL)

    # WRITING LOG FILES ----------------------------------------------------------------------------------------------

    @staticmethod
    def _write_data_files_log(log_file, database, info_file):
        log_file.write('\n')
        log_file.write('DATA FILES ------------------------------- \n')
        log_file.write(f'database = {database} \n')
        log_file.write(f'info_file = {info_file} \n')

    def _write_config_log(self, log_file):
        log_file.write('\n')
        log_file.write('CONFIG ----------------------------------- \n')
        json.dump(self.config, log_file, indent=4)
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

    @staticmethod
    def _delete_files(file_names, parent_directory):
        """
        Deletes every file in a given list of file_names found in the directory parent_directory.
        """
        for file in file_names:
            path_to_file = os.path.join(parent_directory, file)
            try:
                os.remove(path_to_file)
            except:
                pass


if __name__ == "__main__":
    config = {'hierarchical_clustering': False,
              'min_cluster_size': 8,
              'max_lambda2': 0.6,
              'clustering_type': 'agglomerative_clustering',
              'max_num_paths': 3,
              'pca_dim': 2,
              'clustering_method_threshold': 1000,
              'max_path_length': 5,
              'multiprocessing': True,
              'num_walks': 10000,
              'length_of_walks': 5,
              'theta_hit': 0.98,
              'theta_sym': 0.1,
              'theta_js': 1,
              'num_top': 3,
              'epsilon': 0.01,
              'alpha': 0.05,
              'computed_hyperparameters': True,
              'pruning_value': None,
              }
    mln_eval = MLNEvaluator(config=config)
    mln_eval.evaluate(database='imdb4.db', info_file='imdb.info', output_log_file=True)
