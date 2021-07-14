import os
import numpy as np
import subprocess
import time
import json
import random
from datetime import datetime
from collections import defaultdict

from HierarchicalClustering.GraphObjects import Hypergraph
from HierarchicalClustering.HierarchicalClusterer import HierarchicalClusterer
from HierarchicalClustering.Communities import Communities
from HierarchicalClustering.CommunityPrinter import CommunityPrinter


class MLNEvaluator(object):
    def __init__(self,
                 config,
                 lsm_dir='../../lsmcode',
                 data_dir='./Data',
                 temp_dir='./Temp',
                 mln_dir='./MLNs',
                 log_dir='./Log',
                 results_dir='./Results',
                 experiments_dir='./Experiments2',
                 delete_generated_files=False,
                 seed=None,
                 ):

        self.config = config

        self.lsm_dir = lsm_dir
        self.data_dir = data_dir
        self.temp_dir = temp_dir
        self.mln_dir = mln_dir
        self.log_dir = log_dir
        self.results_dir = results_dir
        self.experiments_dir = experiments_dir

        self.delete_generated_files = delete_generated_files

        self.file_suffix = '_new_SOTA'

        self.time_statistics = defaultdict(lambda: [])

        self.clustering_statistics = defaultdict(lambda: [])

        self.mln_statistics = defaultdict(lambda: [])

        self.mln_name = None  # custom file name for the MLN

        if seed is None:
            self.seed = random.randint(0, 1000)
        else:
            self.seed = seed

        self.log_file_name = None

    def evaluate(self, database: str, info_file: str):
        """
        Structure learns a MLN for each database in a list of database files.
        Evaluates the average conditional log likelihood of each MLN using leave-one-out cross-validation.
        """
        self.structure_learn_MLN(database, info_file)
        self.evaluate_formula_statistics_of_MLNs(database)
        self.write_log_file(database, info_file)

        print('Done')
        return {'num_single_nodes': self.clustering_statistics['mean_number_single_nodes'],
                'num_clusters': self.clustering_statistics['mean_number_node_clusters'],
                'time_random_walks': self.time_statistics['clustering_and_RWs'],
                'time_structure_learning': self.time_statistics['total_structure_learning'],
                'length_of_formulas': self.mln_statistics['formula_length'],
                'number_of_formulas': self.mln_statistics['number_of_formulas']}

    # STRUCTURE LEARNING FUNCTIONS ------------------------------------------------------------------------------------

    def structure_learn_MLN(self, database: str, info_file: str):
        """
        Structure-learn an MLN from each database in the list of database files.
        """
        print(f'Structure Learning {database} using New Algorithm')
        print(' Random walks...')
        initial_time = time.time()
        self.generate_communities_using_hierarchical_clustering(database, info_file)
        clustering_time = time.time()
        self.time_statistics['clustering_and_RWs'].append(clustering_time - initial_time)
        save_name = database.rstrip('.db') + self.file_suffix
        self._run_rest_of_structure_learning_pipeline(database, info_file, save_name)

        complete_time = time.time()
        self.time_statistics['total_structure_learning'].append(complete_time - initial_time)
        self._remove_temporary_files_produced_during_structure_learning()

    def _run_rest_of_structure_learning_pipeline(self, database, info_file, save_name):
        print(' Communities...')
        self._run_get_communities(info_file, save_name)
        print(' Paths...')
        self._run_path_finding(info_file, save_name)
        print(' Finding formulas...')
        self._run_create_MLN_rules(database, info_file, save_name)
        print(' Calculating weights..')
        self._run_learn_MLN_weights(database, save_name)

    def _run_get_communities(self, info_file, save_name):
        get_communities_command = f'{self.lsm_dir}/getcom/getcom {self.temp_dir}/{save_name}.ldb {self.temp_dir}/' \
                                  f'{save_name}.uldb {self.temp_dir}/{save_name}.srcnclusts {self.data_dir}/' \
                                  f'{info_file} 10 {self.temp_dir}/{save_name}.comb.ldb NOOP true {self.seed} ' \
                                  f'> {self.log_dir}/{save_name}-getcom.log '
        time0 = time.time()
        subprocess.call(get_communities_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['getting_communities'].append(time1 - time0)

    def _run_path_finding(self, info_file, save_name):
        path_finding_command = f'{self.lsm_dir}/pfind2/pfind {self.temp_dir}/{save_name}.comb.ldb 5 0 5 -1.0 ' \
                               f'{self.data_dir}/{info_file} {self.temp_dir}/{save_name}.rules > ' \
                               f'{self.log_dir}/{save_name}-findpath.log'
        time0 = time.time()
        subprocess.call(path_finding_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['path_finding'].append(time1 - time0)

    def _run_create_MLN_rules(self, database: str, info_file: str, save_name: str):
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
        self.time_statistics['creating_rules'].append(time1 - time0)

    def _run_learn_MLN_weights(self, database_name: str, save_name: str):
        learn_mln_weights_command = f'{self.lsm_dir}/alchemy30/bin/learnwts -g -i {self.temp_dir}/' \
                                    f'{save_name}-rules.mln -o {self.mln_dir}/{save_name}-rules-out.mln -t ' \
                                    f'{self.data_dir}/{database_name}'
        time0 = time.time()
        subprocess.call(learn_mln_weights_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['learning_weights'].append(time1 - time0)

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
                                                              num_walks=self.config['num_walks'],
                                                              walk_length=self.config['length_of_walks'],
                                                              theta_hit=self.config['theta_hit'],
                                                              theta_sym=self.config['theta_sym'],
                                                              theta_js=self.config['theta_js']))
        else:
            if self.config['computed_hyperparameters']:
                hypergraph_communities = [Communities(original_hypergraph, config=self.config)]
            else:
                hypergraph_communities = [Communities(original_hypergraph, config=self.config,
                                                      num_walks=self.config['num_walks'],
                                                      walk_length=self.config['length_of_walks'],
                                                      theta_hit=self.config['theta_hit'],
                                                      theta_sym=self.config['theta_sym'],
                                                      theta_js=self.config['theta_js'])]

        self._populate_clustering_statistics_dictionary(hypergraph_communities)

        community_printer = CommunityPrinter(list_of_communities=hypergraph_communities,
                                             original_hypergraph=original_hypergraph)
        community_printer.write_files(file_name=os.path.join(self.temp_dir, database.rstrip('.db') +
                                                             self.file_suffix))

    # EVALUATION FUNCTIONS --------------------------------------------------------------------------------------------

    def evaluate_formula_statistics_of_MLNs(self, database: str):
        """
        Computes the average formula length and number of formulas for each MLN associated with each database file.
        """
        formula_lengths = []
        std_formula_lengths = []
        number_of_formulas = []

        fl, std_fl, nf = self.compute_average_and_std_formula_length_and_number_of_formulas(database)
        self.mln_statistics["formula_length"] = [fl]
        self.mln_statistics["number_of_formulas"] = [nf]
        formula_lengths.append(fl)
        number_of_formulas.append(nf)
        std_formula_lengths.append(std_fl)

    def compute_average_and_std_formula_length_and_number_of_formulas(self, database):
        mln_file_name = database.rstrip('.db') + f'{self.file_suffix}-rules-out.mln'
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

    def _populate_clustering_statistics_dictionary(self, hypergraph_communities: list[Communities]):
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
            os.remove(path_to_file)
