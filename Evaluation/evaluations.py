from MLNEvaluator import MLNEvaluator

parameters = {
    'defaults': {
        'number_of_random_walks': 10000,
        'length_of_random_walks': 5,
        'theta_hit': 0.8,
        'theta_sym': 0.1,
        'theta_js': 1,
        'num_top': 3,
        'hierarchical_clustering': False,
        'pruning': None,
    },
}

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
    config['num_walks'] = 10000
    config['length_of_walks'] = 5
    config['theta_hit'] = 0.8
    config['theta_sym'] = 0.1
    config['theta_js'] = 1
    config['num_top'] = 3
    config['epsilon'] = 0.05
    config['theta_p'] = 0.1
    return config

#hc true
    # for clustering type
for hc in [True, False]:
    config['hierarchical_clustering'] = hc
    if hc:
        for min_cluster_size in min_cluster_sizes:
            for max_lambda2 in max_lambda2s:
                for clustering_type in clustering_types:
                    config = set_defaults(config)
                    config['clustering_type'] = clustering_type
                    config['computed_hyperparameters'] = True
                    for epsilon in epsilons:
                        config['epsilon'] = epsilon
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)
                    for theta_p in theta_ps:
                        config['theta_p'] = theta_p
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)

                    config['computed_hyperparameters'] = False
                    for number_of_walks in number_of_random_walks:
                        config['num_walks'] = number_of_walks
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)

                    for length_of_walks in length_of_random_walks:
                        config['length_of_walk'] = length_of_walks
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)

                    for theta_hit in theta_hits:
                        config['theta_hit'] = theta_hit
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)


                    for theta_sym in theta_syms:
                        config['theta_sym'] = theta_sym
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)


                    for theta_js in theta_jss:
                        config['theta_JS'] = theta_js
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)


                    for num_top in num_tops:
                        config['num_top'] = num_top
                        for pruning_value in pruning_values:
                            config['pruning_value'] = pruning_value
                            # run code
                    config = set_defaults(config)

    else:
        for clustering_type in clustering_types:
            config = set_defaults(config)
            config['clustering_type'] = clustering_type
            config['computed_hyperparameters'] = True
            for epsilon in epsilons:
                config['epsilon'] = epsilon
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)
            for theta_p in theta_ps:
                config['theta_p'] = theta_p
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)

            config['computed_hyperparameters'] = False
            for number_of_walks in number_of_random_walks:
                config['num_walks'] = number_of_walks
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)

            for length_of_walks in length_of_random_walks:
                config['length_of_walk'] = length_of_walks
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)

            for theta_hit in theta_hits:
                config['theta_hit'] = theta_hit
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)

            for theta_sym in theta_syms:
                config['theta_sym'] = theta_sym
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)

            for theta_js in theta_jss:
                config['theta_JS'] = theta_js
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)

            for num_top in num_tops:
                config['num_top'] = num_top
                for pruning_value in pruning_values:
                    config['pruning_value'] = pruning_value
                    # run code
            config = set_defaults(config)