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

database_file_names = ['imbd1.db', 'imdb2.db', 'imdb3.db', 'imdb4.db', 'imdb5.db']
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
        generate_community_files(database_name, config)
        save_name = database_name.rstrip('.db')
        os.system(f'./learnMLNfromCommunities.sh {save_name} {database_name} {info_file} {type_file} {LSM_DIR} {DATA_DIR} {MLN_DIR}')

        #Using Original Approach
        #save_name = database_name.rstrip('.db')+'_old'
        #os.system(f'./learnMLN.sh {save_name} {database_file} {info_file} {type_file} {LSM_DIR} {DATA_DIR} {MLN_DIR}')


    #Evaluate the MLNs
    for test_database in database_file_names:
        mln_to_evaluate = os.path.join(MLN_DIR, test_database.rstrip('.db')+'.mln')
        evidence_database_files = [os.path.join(DATA_DIR, database_file) for database_file in database_file_names if database_file != test_database]
        results_file = os.path.join(RESULTS_DIR, test_database.rstrip('.db')+'.results')
        os.system(f'{INFER_DIR}/infer -i {mln_to_evaluate} -r {results_file} -e {evidence_database_files} -q {query_predicates}')
        #TODO: also using original approach


    #Compute the Conditional Log-Likelihood
    average_CLLs = []
    for database_file in database_file_names:
        results_file = database_file.rstrip('.db')+'.results'
        results_dataframe = pd.read_csv(os.path.join(RESULTS_DIR,results_file), delimiter='  ', names=['Ground_Atom', 'CLL'])
        average_CLLs.append(results_dataframe['CLL'].mean())
        #TODO: also using original approach

    print(average_CLLs)

