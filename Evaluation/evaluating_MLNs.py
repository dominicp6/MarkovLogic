import os
import pandas as pd
import numpy as np
import sys
import subprocess
import time
import multiprocessing
sys.path.append('../HierarchicalClustering')
from clusterLearn import run_hierarchical_clustering

#TASKS -----------------------------------------
#1. Extract out functions            [DONE]
#2. Mute scripts                     [DONE]
#2.5 Fix structure learning pipeline for hierarchical clustering [DONE?]
#3. Compute average clause length    [DONE]
#4. Compute runtimes                 [DONE]
# Tidy evaluate function
#4.5 Remove other temporary files
#4.8. Add progress bar 
#5. Generate log file                
#6. Package up into class            [DONE]
#7. Iterate over hyperparams
#-----------------------------------------------

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
                       DATA_DIR = '../../lsmcode/data', 
                       MLN_DIR = './MLNs',
                       RESULTS_DIR = './Results'):

        self.LSM_DIR = LSM_DIR
        self.INFER_DIR = INFER_DIR
        self.DATA_DIR = DATA_DIR
        self.MLN_DIR = MLN_DIR
        self.RESULTS_DIR = RESULTS_DIR

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
            'clustering_params' : { 'stop_criterion' : 'eigenvalue',
                                    'min_ssev' : 0.01,
                                    'tree_output_depth' : 1,
                                    'min_cluster_size' : 1,
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

    def update_config(self, *args):
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
        self.config[parameter_type][parameter] = new_parameter_value

    def get_query_predicates(self, info_file):
        file = open(os.path.join(self.DATA_DIR,info_file),'r')
        query_atoms = []
        for line in file.readlines():
            if line[0:2] == '//': #skip comment lines
                continue
            query_atoms.append(line.split('(')[0])

        query_atom_string = ','.join(query_atoms)
        return query_atom_string

    # def generate_folds(self, file, number_of_folds):
    #     pass

    # def read_database_files(self, database_file_names, number_of_folds):
    #     if len(database_file_names) == 1:
    #         pass
    #     else:
    #         return database_file_names

    def run_get_communities(self, database_name, save_name, method):
        get_communities_command = f'{self.LSM_DIR}/getcom/getcom {self.DATA_DIR}/{save_name}.ldb {self.DATA_DIR}/{save_name}.uldb {self.DATA_DIR}/{save_name}.srcnclusts {self.DATA_DIR}/$3 10 {self.DATA_DIR}/$1.comb.ldb NOOP true 1 > {self.DATA_DIR}/$1-getcom.log'
        time0 = time.time()
        subprocess.call(get_communities_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['getting_communities'].append(time1-time0)

    def run_path_finding(self, database_name, save_name, method):
        path_finding_command = f'{self.LSM_DIR}/pfind2/pfind {self.DATA_DIR}/{save_name}.comb.ldb 5 0 5 -1.0 {self.DATA_DIR}/{self.info_file} {self.DATA_DIR}/{save_name}.rules > {self.DATA_DIR}/{save_name}-findpath.log'
        time0 = time.time()
        subprocess.call(path_finding_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics[method]['path_finding'].append(time1-time0)

    def run_create_MLN_rules(self, database_name, save_name, method):
        create_MLN_rules_command = f'{self.LSM_DIR}/createrules/createrules {self.DATA_DIR}/{save_name}.rules 0 {self.DATA_DIR}/{database_name} {self.DATA_DIR}/{save_name}.comb.ldb {self.DATA_DIR}/{save_name}.uldb {self.DATA_DIR}/{self.info_file} {self.LSM_DIR}/alchemy30/bin/learnwts {self.LSM_DIR}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 {self.MLN_DIR}/{save_name}-rules.mln 1 - - true false 40 > {self.DATA_DIR}/{save_name}-createrules.log'
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

    def run_rest_of_structure_learning_pipeline(self, database_name, save_name, method):
        self.run_get_communities(database_name, save_name, method)
        self.run_path_finding(database_name, save_name, method)
        self.run_create_MLN_rules(database_name, save_name, method)
        self.run_learn_MLN_weights(database_name, save_name, method)

    def structure_learn_with_hierarchical_clustering(self, database_name):
        time0 = time.time()
        run_hierarchical_clustering(database_name, self.config)
        time1 = time.time()
        self.time_statistics['hierarchical_clustering']['clustering'].append(time1-time0)
        save_name = database_name.rstrip('.db')+self.SUFFIX1
        self.run_rest_of_structure_learning_pipeline(database_name, save_name, method='hierarchical_clustering')

    def structure_learn_with_standard_method(self, database_name):
        save_name = database_name.rstrip('.db')+self.SUFFIX2
        random_walks_command = f'{self.LSM_DIR}/rwl/rwl {self.DATA_DIR}/{self.info_file} {self.DATA_DIR}/{database_name} {self.DATA_DIR}/{self.type_file} 10000 5 0.05 0.1 4.9 0.1 1 3 1 {self.DATA_DIE}/{save_name}.ldb {self.DATA_DIR}/{save_name}.uldb {self.DATA_DIR}/{save_name}.srcnclusts > {self.DATA_DIR}/{save_name}-rwl.log'
        time0 = time.time()
        subprocess.call(random_walks_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        time1 = time.time()
        self.time_statistics['standard_method']['clustering'].append(time1-time0)
        self.run_rest_of_structure_learning_pipeline(database_name, save_name, method='standard_method')

    def structure_learn_MLNs_from_database_files(self):
        for database_name in self.database_file_names:
            time0 = time.time()
            self.structure_learn_with_standard_method(database_name)
            time1 = time.time()
            self.time_statistics['standard_method']['total_structure_learning'].append(time1 - time0)
            p = multiprocessing.Process(target = self.structure_learn_with_hierarchical_clustering, args = (database_name,))
            result = watch_for_timeout_on_process(process=p,timeout=5 * max(self.time_statistics['standard_method']['total_structure_learning']))
            if result == TimeoutError:
                return TimeoutError
            else:
                time2 = time.time()
                self.time_statistics['hierarchical_clustering']['total_structure_learning'].append(time2-time1)

        return None

    def _remove_temporary_files_produced_by_structure_learning(self):
        #TODO: remove ldb, uldb, srcclusts files
        cwd = os.getcwd()
        files_in_directory = os.listdir(cwd)
        temp_files = [file for file in files_in_directory if file.endswith("_tmpalchemy.mln")]
        for temp_file in temp_files:
            path_to_file = os.path.join(cwd, temp_file)
            os.remove(path_to_file)

    def run_inference_on_MLN(self, database_test_file, file_suffix):
        mln_to_evaluate = os.path.join(self.MLN_DIR, database_test_file.rstrip('.db')+f'{file_suffix}-rules-out.mln')
        evidence_database_files = ','.join([os.path.join(self.DATA_DIR, database_file) for database_file in self.database_file_names if database_file != database_test_file])
        results_file = os.path.join(self.RESULTS_DIR, database_test_file.rstrip('.db')+f'{file_suffix}.results')
        inference_command = f'{self.INFER_DIR}/infer -i {mln_to_evaluate} -r {results_file} -e {evidence_database_files} -q {self.query_predicates}'
        print('Doing inference...')
        subprocess.call(inference_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
        print('Finished inference...')

    def run_inference_on_MLN_from_hierarchical_clustering(self, database_that_generated_the_MLN):
        self.run_inference_on_MLN(database_that_generated_the_MLN, file_suffix = self.SUFFIX1)

    def run_inference_on_MLN_from_standard_method(self, database_that_generated_the_MLN):
        self.run_inference_on_MLN(database_that_generated_the_MLN, file_suffix = self.SUFFIX2)

    def run_inference_on_MLNs(self, database_file_names):
        for database in self.database_file_names:
            time0 = time.time()
            self.run_inference_on_MLN_from_standard_method(database)
            time1 = time.time()
            self.run_inference_on_MLN_from_hierarchical_clustering(database)
            time2 = time.time()
            self.time_statistics['standard_method']['inference'].append(time1-time0)
            self.time_statistics['hierarchical_clustering']['inference'].append(time2-time1)

    def compute_average_CLL_from_MLN(self, database_test_file, file_suffix):
        results_new_file = database_test_file.rstrip('.db')+f'{file_suffix}.results'
        results_new_dataframe = pd.read_csv(os.path.join(self.RESULTS_DIR,results_new_file), delimiter=' ', names=['Ground_Atom', 'CLL'])
        return np.log(results_new_dataframe['CLL']).mean()

    def compute_average_CLL_from_MLN_with_hierarchical_clustering(self, database_that_generated_the_MLN):
        return self.compute_average_CLL_from_MLN(database_that_generated_the_MLN, file_suffix = self.SUFFIX1)

    def compute_average_CLL_from_MLN_with_standard_method(self, database_that_generated_the_MLN):
        return self.compute_average_CLL_from_MLN(database_that_generated_the_MLN, file_suffix = self.SUFFIX2)

    def compute_average_formula_length_and_number_of_formulas(self, database_file, file_suffix):
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

    def compute_average_formula_length_and_number_of_formulas_for_hierarchical_clustering(self, database_file):
        return self.compute_average_formula_length_and_number_of_formulas(database_file, file_suffix = self.SUFFIX1)

    def compute_average_formula_length_and_number_of_formulas_for_standard_method(self, database_file):
        return self.compute_average_formula_length_and_number_of_formulas(database_file, file_suffix = self.SUFFIX2)

    def evaluate_MLNs(self, database_file_names):
        CLLs_hierarchical_clustering = []
        CLLs_standard_method = []
        formula_lengths_hierarchical_clustering = []
        formula_lengths_standard_method = []
        number_of_formulas_hierarchical_clustering = []
        number_of_formulas_standard_method = []
        #TODO: Compute AUC statistic?
        time0 = time.time()
        for database_file in self.database_file_names:
            CLLs_standard_method.append(self.compute_average_CLL_from_MLN_with_standard_method(database_file))
            fl, nf = self.compute_average_formula_length_and_number_of_formulas_for_standard_method(database_file)
            formula_lengths_standard_method.append(fl); number_of_formulas_standard_method.append(nf)
        time1 = time.time()
        for database_file in self.database_file_names:
            CLLs_hierarchical_clustering.append(self.compute_average_CLL_from_MLN_with_hierarchical_clustering(database_file))
            fl, nf = self.compute_average_formula_length_and_number_of_formulas_for_hierarchical_clustering(database_file)
            formula_lengths_hierarchical_clustering.append(fl); number_of_formulas_hierarchical_clustering.append(nf)
        time2 = time.time()
        self.time_statistics['standard_method']['evaluation'].append(time1-time0)
        self.time_statistics['hierarchical_clustering']['evaluation'].append(time2-time1)
        
        evaluation_statistics = {
            'standard_method' : {
                'average_CLL' : np.average(CLLs_standard_method),
                'average_formula_length' : np.average(formula_lengths_standard_method),
                'average_number_of_formulas' : np.average(number_of_formulas_standard_method),
            },
            'hierarchical_clustering' : {
                'average_CLL' : np.average(CLLs_hierarchical_clustering),
                'average_formula_length' : np.average(formula_lengths_hierarchical_clustering),
                'average_number_of_formulas' : np.average(number_of_formulas_hierarchical_clustering),
            },
        }
       
        return evaluation_statistics

    def write_log_file(self, error = None):
        if error == TimeoutError:
            raise TimeoutError
            #TODO: implement

        print(self.time_statistics)
        #TODO: implement function
        pass

    def evaluate(self, database_file_names, info_file, type_file, number_of_folds = 5):
        #TO REMOVE IN FINAL EVALUATOR ---------------
        self.database_file_names = ['imdb1.db', 'imdb2.db']#, 'imdb3.db', 'imdb4.db', 'imdb5.db']
        self.info_file = 'imdb.info'
        self.type_file = 'imdb.type'
        number_of_folds = 5
        #--------------------------------------------

        print('Something at the beginnning....')
        self.query_predicates = self.get_query_predicates(info_file)
        #TODO: add random partitioning for automatically creating folds
        result = self.structure_learn_MLNs_from_database_files()
        if result == TimeoutError:
            self.write_log_file(error = TimeoutError)
            return TimeoutError
        else:
            self._remove_temporary_files_produced_by_structure_learning()
            self.run_inference_on_MLNs(database_file_names)
            evaluation_statistics = self.evaluate_MLNs(database_file_names)
            self.write_log_file()
            print('Something at the end...')


if __name__ == "__main__":
    evaluator = MLNEvaluator()
    evaluator.evaluate(database_file_names = ['imdb1.db', 'imdb2.db'], info_file='imdb.info', type_file='imdb.type')