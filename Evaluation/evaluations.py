from MLNEvaluator2 import MLNEvaluator

clustering_types = ['JS', 'kmeans', 'birch']
max_lambda2s = [0.7, 0.8, 0.9]
min_cluster_sizes = [5, 10, 15]
epsilons = [0.005, 0.01, 0.05, 0.10]
pruning_values = [None, 9, 8, 7, 6, 5]
theta_ps = [0.01, 0.05, 0.10]
number_of_random_walks = [1000, 10000, 20000]
length_of_random_walks = [3, 4, 5, 6]
theta_hits = [0.8, 0.9, 0.95]
theta_syms = [0.01, 0.1, 0.2]
theta_jss = [0.01, 0.1, 1]
num_tops = [3, 4, 5]

config = {}


def set_defaults(config):
    config['max_num_paths'] = 3
    config['pca_dim'] = 2
    config['clustering_method_threshold'] = 1000
    config['max_path_length'] = 5
    config['multiprocessing'] = True
    config['num_walks'] = 10000
    config['length_of_walks'] = 5
    config['theta_hit'] = 0.8
    config['theta_sym'] = 0.1
    config['theta_js'] = 1
    config['num_top'] = 3
    config['epsilon'] = 0.05
    config['theta_p'] = 0.1
    return config


def initialise_table(table_name):
    latex_table_file = open(f'{table_name}', 'w')
    latex_table_file.write('\begin{table}[hbt] \n')
    latex_table_file.write('\centering\makegapedcells \n')
    latex_table_file.write(
        '\begin{tabular}{ | p{0.08\linewidth} | p{0.035\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.10\linewidth} |} \n')
    latex_table_file.write('\hhline{~|--------|} \n')
    latex_table_file.write(
        '\multicolumn{1}{c|}{}& $\vert \mathcal{D} \vert $ & $N_{SN}$ & $N_{clust}$ & $t_{RW}$ (s) & $t_{SL}$ (s) & $\bar{L}$ & $\bar{N}$ & $CLL$ \\ \n')
    latex_table_file.write('\hhline{|---------|} \n')
    latex_table_file.close()

    return table_name


def run_experiments_for_parameter(parameter_name, parameter_values, config, table_file):
    for parameter in parameter_values:
        config[parameter_name] = parameter
        with open(table_file, 'a') as file:
            file.write(f'\multirow{{9}}{{*}}{{{parameter_name}={parameter}}} \n')
        for pruning_value in pruning_values:
            config['pruning_value'] = pruning_value
            evaluator = MLNEvaluator(config=config)
            data = evaluator.evaluate(database='imdb4.db', info_file='imdb.info')
            with open(table_file, 'a') as file:
                file.write(
                    f'\multirow{{2}}{{*}}{{pruning_value={pruning_value}}} & {data["num_single_nodes"]} & '
                    f'{data["num_clusters"]} & {data["time_random_walks"]} & {data["time_structure_learning"]} & '
                    f'{data["num_single_nodes"]} & {data["length_of_formulas"]} & {data["number_of_formulas"]} &  \\ \n')

# \end{tabular}
# \end{table}


for hc in [True, False]:
    config['hierarchical_clustering'] = hc
    if hc:
        latex_hc_table_file = initialise_table('experiments_hierarchical_clustering.tex')
        for min_cluster_size in min_cluster_sizes:
            with open(latex_hc_table_file, 'a') as file:
                file.write(f'\multirow{{9}}{{*}}{{min_cluster_size={min_cluster_size}}} \n')
            config['min_cluster_size'] = min_cluster_size
            for max_lambda2 in max_lambda2s:
                with open(latex_hc_table_file, 'a') as file:
                    file.write(f'\multirow{{9}}{{*}}{{max_lambda2={max_lambda2}}} \n')
                config['max_lambda2'] = max_lambda2
                for clustering_type in clustering_types:
                    with open(latex_hc_table_file, 'a') as file:
                        file.write(f'\multirow{{9}}{{*}}{{clustering_type={clustering_type}}} \n')
                    config = set_defaults(config)
                    config['clustering_type'] = clustering_type
                    config['computed_hyperparameters'] = True
                    run_experiments_for_parameter('epsilon', epsilons, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta_p', theta_ps, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)
                    config['computed_hyperparameters'] = False
                    run_experiments_for_parameter('num_walks', number_of_random_walks, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)
                    run_experiments_for_parameter('length_of_walks', length_of_random_walks, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta_hit', theta_hits, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta_sym', theta_syms, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)
                    run_experiments_for_parameter('theta_js', theta_jss, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)
                    run_experiments_for_parameter('num_top', num_tops, config, table_file=latex_hc_table_file)
                    config = set_defaults(config)

    else:
        latex_no_hc_table_file = initialise_table('experiments_no_hc.tex')
        for clustering_type in clustering_types:
            with open(latex_no_hc_table_file, 'a') as file:
                file.write(f'\multirow{{9}}{{*}}{{clustering_type={clustering_type}}} \n')
            config = set_defaults(config)
            config['clustering_type'] = clustering_type
            config['computed_hyperparameters'] = True
            run_experiments_for_parameter('epsilon', epsilons, config, table_file=latex_no_hc_table_file)
            config = set_defaults(config)
            run_experiments_for_parameter('theta_p', theta_ps, config, table_file=latex_no_hc_table_file)
            config = set_defaults(config)
            config['computed_hyperparameters'] = False
            run_experiments_for_parameter('num_walks', number_of_random_walks, config, table_file=latex_no_hc_table_file)
            config = set_defaults(config)
            run_experiments_for_parameter('length_of_walks', length_of_random_walks, config,
                                          table_file=latex_no_hc_table_file)
            config = set_defaults(config)
            run_experiments_for_parameter('theta_hit', theta_hits, config, table_file=latex_no_hc_table_file)
            config = set_defaults(config)
            run_experiments_for_parameter('theta_sym', theta_syms, config, table_file=latex_no_hc_table_file)
            config = set_defaults(config)
            run_experiments_for_parameter('theta_js', theta_jss, config, table_file=latex_no_hc_table_file)
            config = set_defaults(config)
            run_experiments_for_parameter('num_top', num_tops, config, table_file=latex_no_hc_table_file)
            config = set_defaults(config)
