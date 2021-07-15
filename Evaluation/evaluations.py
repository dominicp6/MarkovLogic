import numpy as np
from collections import defaultdict
from MLNEvaluator2 import MLNEvaluator


class ExperimentRunner(object):
    def __init__(self, database, info_file):
        self.database = database
        self.info_file = info_file
        self.number_of_repeats = None
        self.config = {}

        self.clustering_types = ['JS']  # , 'kmeans', 'birch']
        self.max_lambda2s = [0.8]  # [0.7, 0.8, 0.9]
        self.min_cluster_sizes = [10]  # [5, 10, 15]
        self.epsilons = [0.05]  # [0.01, 0.05, 0.10]
        self.pruning_values = [None]  # , 7, 6, 5]
        self.theta_ps = [0.01]  # [0.01, 0.05, 0.10]
        self.number_of_random_walks = [10000]  # [1000, 10000, 20000]
        self.length_of_random_walks = [5]  # [4, 5, 6]
        self.theta_hits = [0.98]  # [0.95, 0.98, 1]
        self.theta_syms = [0.1]  # [0.01, 0.1, 0.2]
        self.theta_jss = [1]  # [0.01, 0.1, 1] #TODO: fix this
        self.num_tops = [3]  # [3, 4, 5]

    def _reset_config_with_default_params(self):
        self.config['max_num_paths'] = 3
        self.config['pca_dim'] = 2
        self.config['clustering_method_threshold'] = 1000
        self.config['max_path_length'] = 5
        self.config['multiprocessing'] = True
        self.config['num_walks'] = 10000
        self.config['length_of_walks'] = 5
        self.config['theta_hit'] = 0.98
        self.config['theta_sym'] = 0.1
        self.config['theta_js'] = 1
        self.config['num_top'] = 3
        self.config['epsilon'] = 0.05
        self.config['theta_p'] = 0.1

    @staticmethod
    def _initialise_table(table_name):
        with open(f'{table_name}', 'w') as file:
            file.write('\\begin{table}[hbt] \n')
            file.write('\centering\makegapedcells \n')
            file.write(
                '\\begin{tabular}{ | p{0.25\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth}'
                ' | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} | p{0.105\linewidth} |} \n')
            file.write('\hhline{~|-------|} \n')
            file.write(
                '\multicolumn{1}{c|}{}& $N_{SN}$ & $N_{clust}$ & $t_{RW}$ (s) & $t_{SL}$ (s) & $\\bar{L}$ & '
                '$\\bar{N}$\\\\ \n')
            file.write('\hhline{|--------|} \n')
            file.close()

        return table_name

    @staticmethod
    def _finish_table(table_name):
        with open(f'{table_name}', 'a') as file:
            file.write('\hhline{|--------|} \n')
            file.write('\end{tabular} \n')
            file.write('\end{table} \n')

    def run_experiments_for_parameter(self,
                                      parameter_name,
                                      parameter_values,
                                      table_file
                                      ):
        for parameter in parameter_values:
            self.config[parameter_name] = parameter
            with open(table_file, 'a') as file:
                file.write(f'{parameter_name}={parameter} \\\\ \n')
            for pruning_value in self.pruning_values:
                data_for_all_experiments = defaultdict(lambda: [])
                for repeat_number in range(self.number_of_repeats):
                    self.config['pruning_value'] = pruning_value
                    evaluator = MLNEvaluator(config=self.config)
                    data = evaluator.evaluate(database=self.database, info_file=self.info_file)
                    for key, value in data.items():
                        data_for_all_experiments[key].append(value)
                average_data = defaultdict(lambda: [])
                for key, value in data_for_all_experiments.items():
                    average_data[key] = [np.mean(data_for_all_experiments[key]), np.std(data_for_all_experiments[key])]
                with open(table_file, 'a') as file:
                    file.write(
                        f'pruning\_value={pruning_value} & ${round(average_data["num_single_nodes"][0], 2)}\\pm '
                        f'{round(average_data["num_single_nodes"][1], 2)}$  & '
                        f'${round(average_data["num_clusters"][0], 2)}\\pm{round(average_data["num_clusters"][1], 2)}  & '
                        f'${round(average_data["time_random_walks"][0], 2)}\\pm{round(average_data["time_random_walks"][1], 2)}$ '
                        f'& ${round(average_data["time_structure_learning"][0], 2)}\\pm {round(average_data["time_structure_learning"][1], 2)}$& '
                        f'${round(average_data["length_of_formulas"][0], 2)}\\pm{round(average_data["length_of_formulas"][1], 2)}$& '
                        f'${round(average_data["number_of_formulas"][0], 2)}\\pm{round(average_data["number_of_formulas"][1], 2)}$&  \\\\ \n')
        self._reset_config_with_default_params()

    def _run_experiments_for_random_walk_hyperparameters(self, table_file):
        self._reset_config_with_default_params()
        self.config['computed_hyperparameters'] = True
        self.run_experiments_for_parameter('epsilon', self.epsilons, table_file)
        self.run_experiments_for_parameter('theta\\_p', self.theta_ps, table_file)
        self.config['computed_hyperparameters'] = False
        self.run_experiments_for_parameter('num\\_walks', self.number_of_random_walks, table_file)
        self.run_experiments_for_parameter('length\\_of\\_walks', self.length_of_random_walks, table_file)
        self.run_experiments_for_parameter('theta\\_hit', self.theta_hits, table_file)
        self.run_experiments_for_parameter('theta\\_sym', self.theta_syms, table_file)
        self.run_experiments_for_parameter('theta\\_js', self.theta_jss, table_file)
        self.run_experiments_for_parameter('num\\_top', self.num_tops, table_file)

    def run_experiments(self, experiment_name='experiments', number_of_repeats=1):
        self.number_of_repeats = number_of_repeats
        for hc in [True, False]:
            self.config['hierarchical_clustering'] = hc
            if hc:
                hc_table = self._initialise_table(f'{experiment_name}_hc.tex')
                for min_cluster_size in self.min_cluster_sizes:
                    with open(hc_table, 'a') as file:
                        file.write(f'min\_cluster\_size={min_cluster_size} \\\\ \n')
                    self.config['min_cluster_size'] = min_cluster_size
                    for max_lambda2 in self.max_lambda2s:
                        with open(hc_table, 'a') as file:
                            file.write(f'max\_lambda2={max_lambda2} \\\\ \n')
                        self.config['max_lambda2'] = max_lambda2
                        for clustering_type in self.clustering_types:
                            with open(hc_table, 'a') as file:
                                file.write(f'clustering\_type={clustering_type} \\\\ \n')
                            self.config['clustering_type'] = clustering_type
                            self._run_experiments_for_random_walk_hyperparameters(hc_table)

                self._finish_table(hc_table)

            else:
                no_hc_table = self._initialise_table(f'{experiment_name}_no_hc.tex')
                for clustering_type in self.clustering_types:
                    with open(no_hc_table, 'a') as file:
                        file.write(f'clustering\_type={clustering_type} \\\\ \n')
                    self.config['clustering_type'] = clustering_type
                    self._run_experiments_for_random_walk_hyperparameters(no_hc_table)
                self._finish_table(no_hc_table)


if __name__ == "__main__":
    experiment_runner = ExperimentRunner(database='imdb4.db', info_file='imdb.info')
    experiment_runner.run_experiments(number_of_repeats=1)
