import os
import pandas as pd
from clusterLearn import generate_community_files

LSM_DIR = '/home/domphillips/MarkovLogic/lsmcode'
INFER_DIR = '/home/domphillips/MarkovLogic/alchemy-2/bin'
DATA_DIR = '/home/domphillips/MarkovLogic/lsmcode/data'
MLN_DIR = '/home/domphillips/MarkovLogic/HierarchicalClustering/MLNs'
RESULTS_DIR = '/home/domphillips/MarkovLogic/HierarchicalClustering/Results'

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
    }
}

database_file_names = ['imdb1.db', 'imdb2.db', 'imdb3.db', 'imdb4.db', 'imdb5.db']
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


if __name__ == '__main__':
    #Get Queries
    query_predicates = get_query_predicates(info_file)

    #Assemble Database Files
    #TODO: add random partitioning for automatically creating folds

    #Learn MLNs from Database Files
    for database_name in database_file_names:
        #Using Hierarchical Clustering
        #generate_community_files(database_name, config)
        #save_name = database_name.rstrip('.db')
        #os.system(f'./learnMLNfromCommunities.sh {save_name} {database_name} {info_file} {type_file} {LSM_DIR} {DATA_DIR} {MLN_DIR}')

        #Using Original Approach
        save_name = database_name.rstrip('.db')+'_old'
        os.system(f'./learnMLN.sh {save_name} {database_name} {info_file} {type_file} {LSM_DIR} {DATA_DIR} {MLN_DIR}')

    #Remove Temporary Files
    cwd = os.getcwd()
    files_in_directory = os.listdir(cwd)
    temp_files = [file for file in files_in_directory if file.endswith("_tmpalchemy.mln")]
    for temp_file in temp_files:
        path_to_file = os.path.join(cwd, temp_file)
        os.remove(path_to_file)

    #Evaluate the MLNs
    for test_database in database_file_names:
        mln_to_evaluate = os.path.join(MLN_DIR, test_database.rstrip('.db')+'-rules-out.mln')
        evidence_database_files = [os.path.join(DATA_DIR, database_file) for database_file in database_file_names if database_file != test_database]
        results_file = os.path.join(RESULTS_DIR, test_database.rstrip('.db')+'.results')
        os.system(f'{INFER_DIR}/infer -i {mln_to_evaluate} -r {results_file} -e {evidence_database_files} -q {query_predicates}')
        
        mln_to_evaluate = os.path.join(MLN_DIR, test_database.rstrip('.db')+'_old-rules-out.mln')
        results_file = os.path.join(RESULTS_DIR, test_database.rstrip('.db')+'_old.results')
        os.system(f'{INFER_DIR}/infer -i {mln_to_evaluate} -r {results_file} -e {evidence_database_files} -q {query_predicates}')


    #Compute the Conditional Log-Likelihood
    average_CLLs_new = []
    average_CLLs_old = []
    for database_file in database_file_names:
        results_new_file = database_file.rstrip('.db')+'.results'
        results_new_dataframe = pd.read_csv(os.path.join(RESULTS_DIR,results_new_file), delimiter='  ', names=['Ground_Atom', 'CLL'])
        average_CLLs_new.append(results_new_dataframe['CLL'].mean())

        results_old_file = database_file.rstrip('.db')+'_old.results'
        results_old_dataframe = pd.read_csv(os.path.join(RESULTS_DIR,results_old_file), delimiter='  ', names=['Ground_Atom', 'CLL'])
        average_CLLs_old.append(results_old_dataframe['CLL'].mean())
    

    print(average_CLLs_new)
    print(average_CLLs_old)


