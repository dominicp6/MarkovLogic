import numpy as np
from tqdm import tqdm
from collections import defaultdict
from MLNEvaluator2 import MLNEvaluator


class ExperimentRunner(object):
    def __init__(self, database, info_file):
        self.database = database
        self.info_file = info_file
        self.number_of_repeats = None
        self.config = {}

        # Hierarchical Clustering Parameters -----------------
        self.max_lambda2s = [0.8]  # [0.7, 0.8, 0.9]
        self.min_cluster_sizes = [10]  # [5, 10, 15]

        # Random Walk Parameters -----------------------------
        self.epsilons = [0.01, 0.10]
        self.theta_ps = [0.05, 0.10]
        self.number_of_random_walks = [1000, 5000]
        self.length_of_random_walks = [3, 6]
        self.theta_hits = [0.95, 1]
        self.theta_syms = [0.01, 0.2]
        self.theta_jss = [0.03, 3]
        self.num_tops = [2, 4]

        # Path Similarity Clustering Parameters --------------
        self.clustering_types = ['JS', 'kmeans', 'birch']  # , 'kmeans', 'birch']

        # Pruning Parameter ----------------------------------
        self.pruning_values = [None, 6]  # [None, 6]

        self.default_values = {
            'max_num_paths': 3,
            'pca_dim': 2,
            'clustering_method_threshold': 1000,
            'max_path_length': 5,
            'multiprocessing': True,
            'num_walks': 10000,
            'length_of_walks': 5,
            'theta_hit': 0.98,
            'theta_sym': 0.1,
            'theta_js': 1,
            'num_top': 3,
            'epsilon': 0.05,
            'theta_p': 0.01
        }

    def _calculate_number_of_experiments_to_run(self):
        number_of_experiments = ((len(self.min_cluster_sizes) * len(self.max_lambda2s) + 1) * \
                                len(self.clustering_types) * (len(self.epsilons) + len(self.theta_ps) +
                                len(self.number_of_random_walks) * len(self.length_of_random_walks) +
                                len(self.theta_hits) + len(self.theta_syms)+ len(self.num_tops)) * \
                                len(self.pruning_values) + 2*len(self.pruning_values))*self.number_of_repeats

        return number_of_experiments

    def _reset_config_with_default_params(self):
        for hyperparameter, hyperparameter_value in self.default_values.items():
            self.config[hyperparameter] = hyperparameter_value

    def _initialise_table(self, table_name, hierarchical_clustering=True):
        with open(f'{table_name}', 'w') as file:
            file.write('\\begin{longtable}{| p{0.2\linewidth} | p{0.10\linewidth}  p{0.10\linewidth}'
                       '  p{0.10\linewidth}  p{0.10\linewidth}  p{0.10\linewidth}  p{0.10\linewidth}} \n')
            if hierarchical_clustering:
                file.write(f'\\caption{{Structure learning {self.database} '
                           f'\\color{{red}} with Hierarchical Clustering \\color{{black}} and '
                           f'{self.number_of_repeats} repeats.'
                           f'Default hyperparameters: {self.default_values}}}')
            else:
                file.write(f'\\caption{{Structure learning {self.database} '
                           f'\\color{{red}} without Hierarchical Clustering \\color{{black}} and '
                           f'{self.number_of_repeats} repeats.'
                           f'Default hyperparameters: {self.default_values}}}')
            file.write('\centering \n')
            file.write('& & $N_{SN}$ & $N_{clust}$ & $t_{RW}$ (s) & $t_{SL}$ (s) & $\\bar{L}$ & $\\bar{N}$\\\\ \n')
            file.close()

        return table_name

    @staticmethod
    def _finish_table(table_name):
        with open(f'{table_name}', 'a') as file:
            file.write('\end{longtable} \n')

    def run_experiments_for_default_values(self, table_file):
        with open(table_file, 'a') as file:
            file.write(f'default\_parameters \\\\ \n')
        self.run_experiments_for_different_pruning_values(table_file)

    def run_experiments_for_different_pruning_values(self, table_file):
        for pruning_value in self.pruning_values:
            data_for_all_experiments = defaultdict(lambda: [])
            for repeat_number in range(self.number_of_repeats):
                self.config['pruning_value'] = pruning_value
                evaluator = MLNEvaluator(config=self.config)
                data = evaluator.evaluate(database=self.database, info_file=self.info_file)
                self.pbar.update(1)
                for key, value in data.items():
                    data_for_all_experiments[key].append(value)
            average_data = defaultdict(lambda: [])
            for key, value in data_for_all_experiments.items():
                average_data[key] = [np.mean(data_for_all_experiments[key]), np.std(data_for_all_experiments[key])]
            with open(table_file, 'a') as file:
                if average_data["time_structure_learning"][0] > 0:
                    file.write(
                        f'pruning\_value={pruning_value} & ${round(average_data["num_single_nodes"][0], 2)}\\pm '
                        f'{round(average_data["num_single_nodes"][1], 2)}$  & '
                        f'${round(average_data["num_clusters"][0], 2)}\\pm{round(average_data["num_clusters"][1], 2)}$ & '
                        f'${round(average_data["time_random_walks"][0], 2)}\\pm{round(average_data["time_random_walks"][1], 2)}$ '
                        f'& ${round(average_data["time_structure_learning"][0], 2)}\\pm {round(average_data["time_structure_learning"][1], 2)}$& '
                        f'${round(average_data["length_of_formulas"][0], 2)}\\pm{round(average_data["length_of_formulas"][1], 2)}$& '
                        f'${round(average_data["number_of_formulas"][0], 2)}\\pm{round(average_data["number_of_formulas"][1], 2)}$& \n')
                else:
                    file.write(
                        f'pruning\_value={pruning_value} & ${round(average_data["num_single_nodes"][0], 2)}\\pm '
                        f'{round(average_data["num_single_nodes"][1], 2)}$  & '
                        f'${round(average_data["num_clusters"][0], 2)}\\pm{round(average_data["num_clusters"][1], 2)}$ & '
                        f'${round(average_data["time_random_walks"][0], 2)}\\pm{round(average_data["time_random_walks"][1], 2)}$ '
                        f'& \\color{{red}} LONG \\color{{black}} & '
                        f'$\\color{{red}} LONG \\color{{black}}& '
                        f'$\\color{{red}} LONG \\color{{black}}& \n')

    def run_experiments_for_parameter(self,
                                      parameter_name,
                                      parameter_values,
                                      table_file
                                      ):
        for parameter in parameter_values:
            self.config[parameter_name] = parameter
            with open(table_file, 'a') as file:
                file.write(f'{parameter_name}={parameter} \\\\ \n')
            self.run_experiments_for_different_pruning_values(table_file)
        self._reset_config_with_default_params()

    def _run_experiments_for_random_walk_hyperparameters(self, table_file):
        self._reset_config_with_default_params()
        self.config['computed_hyperparameters'] = True
        with open(table_file, 'a') as file:
            file.write(f'new\_hypparams = True \\\\ \n')
        self.run_experiments_for_default_values(table_file)
        self.run_experiments_for_parameter('epsilon', self.epsilons, table_file)
        self.run_experiments_for_parameter('theta\\_p', self.theta_ps, table_file)
        self.config['computed_hyperparameters'] = False
        with open(table_file, 'a') as file:
            file.write(f'new\_hypparams = False \\\\ \n')
        self.run_experiments_for_default_values(table_file)
        self.run_experiments_for_parameter('num\\_walks', self.number_of_random_walks, table_file)
        self.run_experiments_for_parameter('length\\_of\\_walks', self.length_of_random_walks, table_file)
        self.run_experiments_for_parameter('theta\\_hit', self.theta_hits, table_file)
        self.run_experiments_for_parameter('theta\\_sym', self.theta_syms, table_file)
        self.run_experiments_for_parameter('theta\\_js', self.theta_jss, table_file)
        self.run_experiments_for_parameter('num\\_top', self.num_tops, table_file)

    def run_experiments(self, experiment_name='experiments', number_of_repeats=1):
        self.number_of_repeats = number_of_repeats
        with tqdm(total=self._calculate_number_of_experiments_to_run()) as self.pbar:
            for hc in [True, False]:
                self.config['hierarchical_clustering'] = hc
                if hc:
                    hc_table = self._initialise_table(f'{experiment_name}_hc.tex', hierarchical_clustering=True)
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
                    no_hc_table = self._initialise_table(f'{experiment_name}_no_hc.tex', hierarchical_clustering=False)
                    for clustering_type in self.clustering_types:
                        with open(no_hc_table, 'a') as file:
                            file.write(f'clustering\_type={clustering_type} \\\\ \n')
                        self.config['clustering_type'] = clustering_type
                        self._run_experiments_for_random_walk_hyperparameters(no_hc_table)
                    self._finish_table(no_hc_table)


if __name__ == "__main__":
    experiment_runner = ExperimentRunner(database='imdb4.db', info_file='imdb.info')
    experiment_runner.run_experiments(number_of_repeats=3)
