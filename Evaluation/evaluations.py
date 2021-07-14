import numpy as np
from collections import defaultdict
from MLNEvaluator2 import MLNEvaluator

number_of_repeats = 2


clustering_types = ['JS']#, 'kmeans', 'birch']
max_lambda2s = [0.8] #[0.7, 0.8, 0.9]
min_cluster_sizes = [10] #[5, 10, 15]
epsilons = [0.05] #[0.01, 0.05, 0.10]
pruning_values = [None] #, 7, 6, 5]
theta_ps = [0.01] #[0.01, 0.05, 0.10]
number_of_random_walks = [10000] #[1000, 10000, 20000]
length_of_random_walks = [5] #[4, 5, 6]
theta_hits = [0.98] #[0.95, 0.98, 1] #TODO: implement this
theta_syms = [0.1] #[0.01, 0.1, 0.2]
theta_jss = [1] #[0.01, 0.1, 1] #TODO: fix this
num_tops = [3] #[3, 4, 5]

config = {}


def set_defaults(config):
    config['max_num_paths'] = 3
    config['pca_dim'] = 2
    config['clustering_method_threshold'] = 1000
    config['max_path_length'] = 5
    config['multiprocessing'] = True
    config['num_walks'] = 10000
    config['length_of_walks'] = 5
    config['theta_hit'] = 0.98
    config['theta_sym'] = 0.1
    config['theta_js'] = 1
    config['num_top'] = 3
    config['epsilon'] = 0.05
    config['theta_p'] = 0.1
    return config


def initialise_table(table_name):
    with open(f'{table_name}', 'w') as file:
        file.write('\\begin{table}[hbt] \n')
        file.write('\centering\makegapedcells \n')
        file.write(
            '\\begin{tabular}{ | p{0.25\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} |} \n')
        file.write('\hhline{~|-------|} \n')
        file.write(
            '\multicolumn{1}{c|}{}& $N_{SN}$ & $N_{clust}$ & $t_{RW}$ (s) & $t_{SL}$ (s) & $\\bar{L}$ & $\\bar{N}$\\\\ \n')
        file.write('\hhline{|--------|} \n')
        file.close()

    return table_name

def finish_table(table_name):
    with open(f'{table_name}', 'a') as file:
        file.write('\hhline{|--------|} \n')
        file.write('\end{tabular} \n')
        file.write('\end{table} \n')


def run_experiments_for_parameter(parameter_name, parameter_values, config, table_file, number_of_repeats):
    for parameter in parameter_values:
        config[parameter_name] = parameter
        with open(table_file, 'a') as file:
            file.write(f'{parameter_name}={parameter} \\\\ \n')
        for pruning_value in pruning_values:
            data_for_all_experiments = defaultdict(lambda: [])
            for repeat_number in range(number_of_repeats):
                config['pruning_value'] = pruning_value
                evaluator = MLNEvaluator(config=config)
                data = evaluator.evaluate(database='imdb4.db', info_file='imdb.info')
                for key, value in data.items():
                    data_for_all_experiments[key].append(value)
            average_data = defaultdict(lambda: [])
            for key, value in data_for_all_experiments.items():
                average_data[key] = [np.mean(data_for_all_experiments[key]), np.std(data_for_all_experiments[key])]
            with open(table_file, 'a') as file:
                file.write(
                    f'pruning\_value={pruning_value} & ${round(average_data["num_single_nodes"][0],2)}\\pm '
                    f'{round(average_data["num_single_nodes"][1],2)}$  & '
                    f'${round(average_data["num_clusters"][0],2)}\\pm{round(average_data["num_clusters"][1],2)}  & '
                    f'${round(average_data["time_random_walks"][0],2)}\\pm{round(average_data["time_random_walks"][1],2)}$ '
                    f'& ${round(average_data["time_structure_learning"][0],2)}\\pm {round(average_data["time_structure_learning"][1],2)}$& '
                    f'${round(average_data["length_of_formulas"][0],2)}\\pm{round(average_data["length_of_formulas"][1],2)}$& '
                    f'${round(average_data["number_of_formulas"][0],2)}\\pm{round(average_data["number_of_formulas"][1],2)}$&  \\\\ \n')




for hc in [True, False]:
    config['hierarchical_clustering'] = hc
    if hc:
        latex_hc_table_file = initialise_table('experiments_hierarchical_clustering.tex')
        for min_cluster_size in min_cluster_sizes:
            with open(latex_hc_table_file, 'a') as file:
                file.write(f'min\_cluster\_size={min_cluster_size} \\\\ \n')
            config['min_cluster_size'] = min_cluster_size
            for max_lambda2 in max_lambda2s:
                with open(latex_hc_table_file, 'a') as file:
                    file.write(f'max\_lambda2={max_lambda2} \\\\ \n')
                config['max_lambda2'] = max_lambda2
                for clustering_type in clustering_types:
                    with open(latex_hc_table_file, 'a') as file:
                        file.write(f'clustering\_type={clustering_type} \\\\ \n')
                    config = set_defaults(config)
                    config['clustering_type'] = clustering_type
                    config['computed_hyperparameters'] = True
                    run_experiments_for_parameter('epsilon', epsilons, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta\\_p', theta_ps, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
                    config['computed_hyperparameters'] = False
                    run_experiments_for_parameter('num\\_walks', number_of_random_walks, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
                    run_experiments_for_parameter('length\\_of\\_walks', length_of_random_walks, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta\\_hit', theta_hits, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta\\_sym', theta_syms, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta\\_js', theta_jss, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
                    run_experiments_for_parameter('num\\_top', num_tops, config, table_file=latex_hc_table_file, number_of_repeats=number_of_repeats)
                    config = set_defaults(config)
        finish_table(latex_hc_table_file)

    else:
        latex_no_hc_table_file = initialise_table('experiments_no_hc.tex')
        for clustering_type in clustering_types:
            with open(latex_no_hc_table_file, 'a') as file:
                file.write(f'clustering\_type={clustering_type} \\\\ \n')
            config = set_defaults(config)
            config['clustering_type'] = clustering_type
            config['computed_hyperparameters'] = True
            run_experiments_for_parameter('epsilon', epsilons, config, table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
            run_experiments_for_parameter('theta\\_p', theta_ps, config, table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
            config['computed_hyperparameters'] = False
            run_experiments_for_parameter('num\\_walks', number_of_random_walks, config, table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
            run_experiments_for_parameter('length\\_of\\_walks', length_of_random_walks, config,
                                          table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
            run_experiments_for_parameter('theta\\_hit', theta_hits, config, table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
            run_experiments_for_parameter('theta\\_sym', theta_syms, config, table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
            run_experiments_for_parameter('theta\\_js', theta_jss, config, table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
            run_experiments_for_parameter('num\\_top', num_tops, config, table_file=latex_no_hc_table_file, number_of_repeats=number_of_repeats)
            config = set_defaults(config)
        finish_table(latex_no_hc_table_file)

