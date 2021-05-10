import os
import pandas as pd
import numpy as np
import sys
import subprocess
sys.path.append('../HierarchicalClustering')
from clusterLearn import generate_community_files


#TASKS -----------------------------------------
#1. Extract out functions            [DONE]
#2. Mute scripts                     [DONE]
#2.5 Fix structure learning pipeline for hierarchical clustering
#3. Compute average clause length
#4. Compute runtimes
#5. Generate log file
#6. Package up into class
#7. Iterate over hyperparams
#-----------------------------------------------


LSM_DIR = '../../lsmcode'
INFER_DIR = '../../alchemy-2/bin'
DATA_DIR = '../../lsmcode/data'
MLN_DIR = './MLNs'
RESULTS_DIR = './Results'

SUFFIX1 = ''     #file suffix used when running hierarchical clustering method
SUFFIX2 = '_old' #file suffix used when running the standard method

config = {
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
    'directory_params' : {'data_dir' : DATA_DIR
    },
    'terminal_params' : {
        'verbose' : False,
    }
}

database_file_names = ['imdb1.db', 'imdb2.db']#, 'imdb3.db', 'imdb4.db', 'imdb5.db']
info_file = 'imdb.info'
type_file = 'imdb.type'
number_of_folds = 5

def get_query_predicates(info_file):
    file = open(os.path.join(DATA_DIR,info_file),'r')
    query_atoms = []
    for line in file.readlines():
        if line[0:2] == '//': #skip comment lines
            continue
        query_atoms.append(line.split('(')[0])

    query_atom_string = ','.join(query_atoms)
    return query_atom_string

def generate_folds(file, number_of_folds):
    pass

def read_database_files(database_file_names, number_of_folds):
    if len(database_file_names) == 1:
        pass
        #TODO: generate fold database files
    else:
        return database_file_names

def structure_learn_with_hierarchical_clustering(database_name):
    generate_community_files(database_name, config)
    save_name = database_name.rstrip('.db')
    structure_learn_command = f'./learnMLNfromCommunities.sh {save_name} {database_name} {info_file} {type_file} {LSM_DIR} {DATA_DIR} {MLN_DIR}'
    print('Doing structure learning hierarchical clustering...')
    subprocess.call(structure_learn_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
    print('Finished structure learning hierarchical clustering...')

def structure_learn_with_standard_method(database_name):
    save_name = database_name.rstrip('.db')+'_old'
    structure_learn_command = f'./learnMLN.sh {save_name} {database_name} {info_file} {type_file} {LSM_DIR} {DATA_DIR} {MLN_DIR}'
    print('Doing structure learning standard method...')
    subprocess.call(structure_learn_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
    print('Finished structure learning standard method...')

def structure_learn_MLNs_from_database_files(database_file_names):
    for database_name in database_file_names:
        structure_learn_with_hierarchical_clustering(database_name)
        structure_learn_with_standard_method(database_name)

def remove_temporary_files_produced_by_structure_learning():
    #TODO: remove ldb, uldb, srcclusts files
    cwd = os.getcwd()
    files_in_directory = os.listdir(cwd)
    temp_files = [file for file in files_in_directory if file.endswith("_tmpalchemy.mln")]
    for temp_file in temp_files:
        path_to_file = os.path.join(cwd, temp_file)
        os.remove(path_to_file)

def run_inference_on_MLN(database_test_file, file_suffix):
    mln_to_evaluate = os.path.join(MLN_DIR, database_test_file.rstrip('.db')+f'{file_suffix}-rules-out.mln')
    evidence_database_files = ','.join([os.path.join(DATA_DIR, database_file) for database_file in database_file_names if database_file != database_test_file])
    results_file = os.path.join(RESULTS_DIR, database_test_file.rstrip('.db')+f'{file_suffix}.results')
    inference_command = f'{INFER_DIR}/infer -i {mln_to_evaluate} -r {results_file} -e {evidence_database_files} -q {query_predicates}'
    print('Doing inference...')
    subprocess.call(inference_command,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL, shell=True)
    print('Finished inference...')

def run_inference_on_MLN_from_hierarchical_clustering(database_that_generated_the_MLN):
    run_inference_on_MLN(database_that_generated_the_MLN, file_suffix = SUFFIX1)

def run_inference_on_MLN_from_standard_method(database_that_generated_the_MLN):
    run_inference_on_MLN(database_that_generated_the_MLN, file_suffix = SUFFIX2)

def run_inference_on_MLNs(database_file_names):
    for database in database_file_names:
        run_inference_on_MLN_from_hierarchical_clustering(database)
        run_inference_on_MLN_from_standard_method(database)

def compute_average_CLL_from_MLN(database_test_file, file_suffix):
    results_new_file = database_test_file.rstrip('.db')+f'{file_suffix}.results'
    results_new_dataframe = pd.read_csv(os.path.join(RESULTS_DIR,results_new_file), delimiter=' ', names=['Ground_Atom', 'CLL'])
    return np.log(results_new_dataframe['CLL']).mean()

def compute_average_CLL_from_MLN_with_hierarchical_clustering(database_that_generated_the_MLN):
    return compute_average_CLL_from_MLN(database_that_generated_the_MLN, file_suffix = SUFFIX1)

def compute_average_CLL_from_MLN_with_standard_method(database_that_generated_the_MLN):
    return compute_average_CLL_from_MLN(database_that_generated_the_MLN, file_suffix = SUFFIX2)

def evaluate_MLNs(database_file_names):
    CLLs_hierarchical_clustering = []
    CLLs_standard_method = []
    for database_file in database_file_names:
        CLLs_hierarchical_clustering.append(compute_average_CLL_from_MLN_with_hierarchical_clustering(database_file))
        CLLs_standard_method.append(compute_average_CLL_from_MLN_with_standard_method(database_file))
        #TODO: Compute Average Formula Length
        #TODO: Compute AUC statistic?

    return np.average(CLLs_hierarchical_clustering), np.average(CLLs_standard_method)

def write_log_file():
    pass

if __name__ == '__main__':
    print('Something at the beginnning....')
    query_predicates = get_query_predicates(info_file)
    #TODO: add random partitioning for automatically creating folds
    structure_learn_MLNs_from_database_files(database_file_names)
    remove_temporary_files_produced_by_structure_learning()
    run_inference_on_MLNs(database_file_names)
    CLL_hierarchical_clustering, CLL_standard_method = evaluate_MLNs(database_file_names)
    write_log_file()
    print('Something at the end...')


