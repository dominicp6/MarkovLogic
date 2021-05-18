import os
import pandas as pd
import numpy as np
import sys
import subprocess
import time
import multiprocessing
import json
from tqdm import tqdm
from datetime import datetime
sys.path.append('../HierarchicalClustering')
from clusterLearn import run_hierarchical_clustering

def watch_for_timeout_on_process(process, timeout):
    process.start()
    process.join(timeout = timeout)
    if process.is_alive():
        process.terminate()
        process.join()
        return TimeoutError
    else:
        return None

class MLNEvaluator(object):
    def __init__(self, LSM_DIR = '../../lsmcode', 
                       INFER_DIR = '../../alchemy-2/bin', 
                       DATA_DIR = './Data', 
                       MLN_DIR = './MLNs',
                       LOG_DIR = './Log',
                       RESULTS_DIR = './Results',
                       delete_generated_files = False):

        self.LSM_DIR = LSM_DIR
        self.INFER_DIR = INFER_DIR
        self.DATA_DIR = DATA_DIR
        self.MLN_DIR = MLN_DIR
        self.LOG_DIR = LOG_DIR
        self.RESULTS_DIR = RESULTS_DIR

        self.delete_generated_files = delete_generated_files

        self.SUFFIX1 = ''     #file suffix used when running hierarchical clustering method
        self.SUFFIX2 = '_old' #file suffix used when running the standard method

        self.time_statistics = {
            'hierarchical_clustering' : {
                'clustering' : [],
                'getting_communities' : [],
                'path_finding' : [],
                'creating_rules' : [],
                'learning_weights' : [],
                'total_structure_learning' : [],
                'performing_inference' : [],
                'performing_evaluation' : [],
                'total' : [],
            },
            'standard_method' : {
                'clustering' : [],
                'getting_communities' : [],
                'path_finding' : [],
                'creating_rules' : [],
                'learning_weights' : [],
                'total_structure_learning' : [],
                'performing_inference' : [],
                'performing_evaluation' : [],
                'total' : [],
            }
        }

        self.config = {
            'randomwalk_params' : {'number_of_walks' : 100, 
                                    'max_length' : 100,
                                    'use_sample_paths' : False, 
                                    'HT_merge_threshold' : 2,
                                    'JS_merge_threshold' : 2,
                                    'N_top' : 5,},
            'clustering_params' : { 'stop_criterion' : 'cluster_size',
                                    'min_ssev' : 0.01,
                                    'tree_output_depth' : 1,
                                    'min_cluster_size' : 20,
                                    'n_init' : 10,
                                    'max_iter' : 300,
                                    'threshold' : 0.01,
                                    'max_fractional_size' : 0.9,},
            'directory_params' : {'data_dir' : self.DATA_DIR
            },
            'terminal_params' : {
                'verbose' : False,
            }
        }

    def set_config(self, *args):
        assert len(args) == 3
        parameter_type = args[0]
        parameter = args[1]
        new_parameter_value = args[2]

        old_parameter_value = self.config[parameter_type][parameter]
        config_parameter_types = self.config.keys()
        parameters = self.config[parameter_type].keys()
        assert parameter_type in config_parameter_types
        assert parameter in parameters
        assert type(new_parameter_value) is type(old_parameter_value)
        if args[0] == 'directory_params' and args[1] == 'data_dir':
            raise ValueError('Cannot update "data_dir" config option. Instead change the DATA_DIR variable when initialising MLNEvaluator.')
        self.config[parameter_type][parameter] = new_parameter_value

    def get_query_predicates(self, info_file):
        file = open(os.path.join(self.DATA_DIR,info_file),'r')
        query_atoms = []
        for line in file.readlines():
            comment_symbol = '//'
            if line[0:2] == comment_symbol:
                continue
            atom_name = line.split('(')[0]
            query_atoms.append(atom_name)

        query_atom_string = ','.join(query_atoms)
        return query_atom_string

    def run_get_communities(self, database_name, save_name, method):
        get_communities_command = f'{self.LSM_DIR}/getcom/getcom {self.DATA_DIR}/{save_name}.ldb {self.DATA_DIR}/{save_name}.uldb {self.DATA_DIR}/{save_name}.srcnclusts {self.DATA_DIR}/{self.info_file} 10 {self.DATA_DIR}/{save_name}.comb.ldb NOOP true 1 > {self.LOG_DIR}/{save_name}-getcom.log'
        time0 = time.time()
        subprocess.call(get_communities_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['getting_communities'].append(time1-time0)

    def run_path_finding(self, database_name, save_name, method):
        path_finding_command = f'{self.LSM_DIR}/pfind2/pfind {self.DATA_DIR}/{save_name}.comb.ldb 5 0 5 -1.0 {self.DATA_DIR}/{self.info_file} {self.DATA_DIR}/{save_name}.rules > {self.LOG_DIR}/{save_name}-findpath.log'
        time0 = time.time()
        subprocess.call(path_finding_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['path_finding'].append(time1-time0)

    def run_create_MLN_rules(self, database_name, save_name, method):
        create_MLN_rules_command = f'{self.LSM_DIR}/createrules/createrules {self.DATA_DIR}/{save_name}.rules 0 {self.DATA_DIR}/{database_name} {self.DATA_DIR}/{save_name}.comb.ldb {self.DATA_DIR}/{save_name}.uldb {self.DATA_DIR}/{self.info_file} {self.LSM_DIR}/alchemy30/bin/learnwts {self.LSM_DIR}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 {self.MLN_DIR}/{save_name}-rules.mln 1 - - true false 40 > {self.LOG_DIR}/{save_name}-createrules.log'
        time0 = time.time()
        subprocess.call(create_MLN_rules_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['creating_rules'].append(time1-time0)

    def run_learn_MLN_weights(self, database_name, save_name, method):
        learn_MLN_weights_command = f'{self.LSM_DIR}/alchemy30/bin/learnwts -g -i {self.MLN_DIR}/{save_name}-rules.mln -o {self.MLN_DIR}/{save_name}-rules-out.mln -t {self.DATA_DIR}/{database_name}'
        time0 = time.time()
        subprocess.call(learn_MLN_weights_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['learning_weights'].append(time1-time0)

    def run_rest_of_structure_learning_pipeline(self, database_name, save_name, method, pbar):
        self.run_get_communities(database_name, save_name, method)
        pbar.update(1)
        self.run_path_finding(database_name, save_name, method)
        pbar.update(1)
        self.run_create_MLN_rules(database_name, save_name, method)
        pbar.update(1)
        self.run_learn_MLN_weights(database_name, save_name, method)
        pbar.update(1)

    def structure_learn_with_hierarchical_clustering(self, database_name):
        time0 = time.time()
        with tqdm(total = 5, file=sys.stdout) as pbar:
            pbar.set_description('- Structure Learning (Hierarchical Clustering)')
            run_hierarchical_clustering(database_name, self.config)
            pbar.update(1)
            time1 = time.time()
            self.time_statistics['hierarchical_clustering']['clustering'].append(time1-time0)
            save_name = database_name.rstrip('.db')+self.SUFFIX1
            self.run_rest_of_structure_learning_pipeline(database_name, save_name, method='hierarchical_clustering', pbar=pbar)

    def structure_learn_with_standard_method(self, database_name):
        save_name = database_name.rstrip('.db')+self.SUFFIX2
        random_walks_command = f'{self.LSM_DIR}/rwl/rwl {self.DATA_DIR}/{self.info_file} {self.DATA_DIR}/{database_name} {self.DATA_DIR}/{self.type_file} 10000 5 0.05 0.1 4.9 0.1 1 3 1 {self.DATA_DIR}/{save_name}.ldb {self.DATA_DIR}/{save_name}.uldb {self.DATA_DIR}/{save_name}.srcnclusts > {self.LOG_DIR}/{save_name}-rwl.log'
        time0 = time.time()
        with tqdm(total = 5, file=sys.stdout) as pbar:
            pbar.set_description('- Structure Learning (Standard Method)')
            subprocess.call(random_walks_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
            pbar.update(1)
            time1 = time.time()
            self.time_statistics['standard_method']['clustering'].append(time1-time0)
            self.run_rest_of_structure_learning_pipeline(database_name, save_name, method='standard_method', pbar=pbar)

    def structure_learn_MLNs_from_database_files(self):
        with tqdm(total = 2*len(self.database_file_names), file=sys.stdout) as pbar:
            pbar.set_description('1] Structure Learning MLNs')
            for database_name in self.database_file_names:
                time0 = time.time()
                self.structure_learn_with_standard_method(database_name)
                pbar.update(1)
                time1 = time.time()
                self.time_statistics['standard_method']['total_structure_learning'].append(time1 - time0)
                p = multiprocessing.Process(target = self.structure_learn_with_hierarchical_clustering, args = (database_name,))
                result = watch_for_timeout_on_process(process=p,timeout=5 * max(self.time_statistics['standard_method']['total_structure_learning']))
                if result == TimeoutError:
                    return TimeoutError
                else:
                    time2 = time.time()
                    self.time_statistics['hierarchical_clustering']['total_structure_learning'].append(time2-time1)
                pbar.update(1)

        return None

    def _remove_files(self, file_names, parent_directory):
        for file in file_names:
            path_to_file = os.path.join(parent_directory, file)
            os.remove(path_to_file)

    def _remove_temporary_files_produced_by_structure_learning(self):
        cwd = os.getcwd()
        files_in_cwd = os.listdir(cwd)
        temp_files = [file for file in files_in_cwd if file.endswith("_tmpalchemy.mln")]
        self._remove_files(temp_files, parent_directory=cwd)
        if self.delete_generated_files == True:
            files_in_data_dir = os.listdir(self.DATA_DIR)
            generated_files = [file for file in files_in_data_dir if file.endswith(tuple(".ldb",".uldb",'.srcnclusts'))]
            self._remove_files(generated_files, parent_directory=self.DATA_DIR)

    def run_inference_on_MLN(self, database_test_file, file_suffix):
        mln_to_evaluate = os.path.join(self.MLN_DIR, database_test_file.rstrip('.db')+f'{file_suffix}-rules-out.mln')
        evidence_database_files = ','.join([os.path.join(self.DATA_DIR, database_file) for database_file in self.database_file_names if database_file != database_test_file])
        results_file = os.path.join(self.RESULTS_DIR, database_test_file.rstrip('.db')+f'{file_suffix}.results')
        inference_command = f'{self.INFER_DIR}/infer -i {mln_to_evaluate} -r {results_file} -e {evidence_database_files} -q {self.query_predicates}'
        subprocess.call(inference_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)

    def run_inference_on_MLN_from_hierarchical_clustering(self, database_that_generated_the_MLN):
        self.run_inference_on_MLN(database_that_generated_the_MLN, file_suffix = self.SUFFIX1)

    def run_inference_on_MLN_from_standard_method(self, database_that_generated_the_MLN):
        self.run_inference_on_MLN(database_that_generated_the_MLN, file_suffix = self.SUFFIX2)

    def run_inference_on_MLNs(self, database_file_names):
        with tqdm(total = 2*len(self.database_file_names), file=sys.stdout) as pbar:
            pbar.set_description('2] Running probabilistic inference on MLNs')
            for database in self.database_file_names:
                time0 = time.time()
                self.run_inference_on_MLN_from_standard_method(database)
                time1 = time.time()
                pbar.update(1)
                self.run_inference_on_MLN_from_hierarchical_clustering(database)
                time2 = time.time()
                pbar.update(1)
                self.time_statistics['standard_method']['performing_inference'].append(time1-time0)
                self.time_statistics['hierarchical_clustering']['performing_inference'].append(time2-time1)

    def _get_file_suffix_from_method(self, method):
        if method == 'standard_method':
            return self.SUFFIX2
        elif method == 'hierarchical_clustering':
            return self.SUFFIX1
        else:
            raise ValueError('method variable must be either "standard_method" or "hierarchical_clustering"')

    def compute_average_CLL_from_MLN(self, database_test_file, method):
        file_suffix = self._get_file_suffix_from_method(method)
        results_new_file = database_test_file.rstrip('.db')+f'{file_suffix}.results'
        results_new_dataframe = pd.read_csv(os.path.join(self.RESULTS_DIR,results_new_file), delimiter=' ', names=['Ground_Atom', 'CLL'])
        return np.log(results_new_dataframe['CLL']).mean()

    def compute_average_formula_length_and_number_of_formulas(self, database_file, method):
        file_suffix = self._get_file_suffix_from_method(method)
        mln_file_name = database_file.rstrip('.db')+f'{file_suffix}-rules-out.mln'
        mln_file = open(os.path.join(self.MLN_DIR,mln_file_name), 'r')
        formula_lengths = []
        for line in mln_file.lines():
            split_line = line.split('  ')
            try:
                float(split_line[0])   # Line corresponds to a formula if it starts with a floating point number (formula weight)
                formula = split_line[1]
                formula_length = len(formula.split(' '))
                formula_lengths.append(formula_length)
            except:
                continue  # Line was not a formula
        number_of_formulas = len(formula_lengths)
        return np.mean(formula_lengths), number_of_formulas

    def evaluate_MLNs_generated_by_method(self, database_file_names, method):
        CLLs = []
        formula_lengths = []
        number_of_formulas = []
        time0 = time.time()
        for database_file in self.database_file_names:
            CLLs.append(self.compute_average_CLL_from_MLN(database_file, method))
            fl, nf = self.compute_average_formula_length_and_number_of_formulas(database_file, method)
            formula_lengths.append(fl); number_of_formulas.append(nf)
        time1 = time.time()
        self.time_statistics[method]['evaluation'].append(time1-time0)

        return [np.average(CLLs), np.average(formula_lengths), np.average(number_of_formulas)]


    def evaluate_MLNs(self, database_file_names):
        statistics_list_standard_method = self.evaluate_MLNs_generated_by_method(database_file_names, 'standard_method')
        statistics_list_hierarchical_clustering = self.evaluate_MLNs_generated_by_method(database_file_names, 'hierarchical_clustering')

        evaluation_statistics = {
            'standard_method' : {
                'average_CLL' : statistics_list_standard_method[0],
                'average_formula_length' : statistics_list_standard_method[1],
                'average_number_of_formulas' : statistics_list_standard_method[2],
            },
            'hierarchical_clustering' : {
                'average_CLL' : statistics_list_hierarchical_clustering[0],
                'average_formula_length' : statistics_list_hierarchical_clustering[1],
                'average_number_of_formulas' : statistics_list_hierarchical_clustering[2],
            },
        }
       
        return evaluation_statistics

    def _write_data_files_log(self, log_file):
        log_file.write('\n')
        log_file.write('DATA FILES ------------------------------- \n')
        log_file.write(f'database_file_names = {self.database_file_names} \n')
        log_file.write(f'info_file = {self.info_file} \n')
        log_file.write(f'type_file = {self.type_file} \n \n')

    def _write_config_log(self, log_file):
        log_file.write('\n')
        log_file.write('CONFIG ----------------------------------- \n')
        json.dump(self.config,log_file, indent=4)
        log_file.write('\n')

    def _write_timings_log(self, log_file):
        log_file.write('\n')
        log_file.write('TIMINGS ---------------------------------- \n')
        json.dump(self.time_statistics,log_file, indent=4)
        log_file.write('\n')

    def _write_evaluation_log(self, log_file):
        log_file.write('\n')
        log_file.write('EVALUATION ------------------------------- \n')
        json.dump(self.evaluation_statistics,log_file, indent=4)
        log_file.write('\n')

    def write_log_file(self, error = None):
        current_time = datetime.now()
        timestampStr = current_time.strftime("%d-%b-%Y (%H:%M:%S.%f)")
        with open(timestampStr+'.log', 'w') as log_file:
            if error == TimeoutError:
                error_msg = 'ERROR: TimeoutError when learning MLNs with Hierarchical Clustering \n'
                print(error_msg)
                log_file.write(error_msg)
            self._write_data_files_log(log_file)
            self._write_config_log(log_file)
            self._write_timings_log(log_file)
            if error == None:
                self._write_evaluation_log(log_file)             

    def evaluate(self, database_file_names, info_file, type_file):
        self.database_file_names = database_file_names
        self.info_file = info_file
        self.type_file = type_file

        self.query_predicates = self.get_query_predicates(info_file)
        result = self.structure_learn_MLNs_from_database_files()
        if result == TimeoutError:
            self.write_log_file(error = TimeoutError)
        else:
            self._remove_temporary_files_produced_by_structure_learning()
            self.run_inference_on_MLNs(database_file_names)
            self.evaluation_statistics = self.evaluate_MLNs(database_file_names)
            self.write_log_file()


if __name__ == "__main__":
    evaluator = MLNEvaluator()
    min_cluster_sizes = [10,5,2]
    for min_cluster_size in min_cluster_sizes:
        evaluator.set_config('clustering_params', 'min_cluster_size', min_cluster_size)
        evaluator.evaluate(database_file_names = ['imdb1.db', 'imdb2.db'], info_file='imdb.info', type_file='imdb.type')