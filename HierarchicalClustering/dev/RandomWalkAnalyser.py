from collections import defaultdict
import matplotlib.pyplot as plt
import hypernetx as hnx
import numpy as np


class RandomWalkAnalyser(object):

    def __init__(self, hypergraph=None,
                 repeats=1,
                 walk_lengths=None,
                 walk_sizes=None,
                 theta_hits=None,
                 theta_syms=None,
                 theta_jss=None,
                 n_tops=None, ):

        assert hypergraph is not None
        self.hypergraph = hypergraph
        self.repeats = repeats

        self.default_config = {'num_walks': 10000,
                               'max_length': 5,
                               'walk_scaling_param': 5,
                               'theta_hit': 4.9,
                               'theta_sym': 0.1,
                               'theta_js': 1,
                               'num_top': 3}

        if n_tops is None:
            n_tops = [5, 4, 3]
        if theta_jss is None:
            theta_jss = [2, 1, 0.6, 0.3, 0.1, 0.05, 0.01]
        if theta_syms is None:
            theta_syms = [2, 1, 0.3, 0.1, 0.05, 0.01]
        if theta_hits is None:
            theta_hits = [4.9]#, 4.95, 4.975, 5, 5.01, 5.1, 5.5, 6]
        if walk_sizes is None:
            walk_sizes = [3, 5, 7, 9]
        if walk_lengths is None:
            walk_lengths = [100, 1000, 3000]

        self.walk_lengths = walk_lengths
        self.walk_sizes = walk_sizes
        self.theta_hits = theta_hits
        self.theta_syms = theta_syms
        self.theta_jss = theta_jss
        self.n_tops = n_tops

        print('Default Config')
        print(self.default_config)

        self.analyse_random_walker()

    def plot_hypergraph(self):
        hnx.draw(self.hypergraph)

    def analyse_random_walker(self):
        # rw_length_results = self.run_number_of_walks_experiments()
        # self.pretty_plot_results(rw_length_results, 'Changing number of random walks', log_plot=True)
        #
        # rw_size_results = self.run_walk_length_experiments()
        # self.pretty_plot_results(rw_size_results, 'Changing length of random walks')

        theta_hit_results = self.run_theta_hit_experiments()
        self.pretty_plot_results(theta_hit_results, 'Changing theta hit parameter')

        # theta_sys_results = self.run_theta_sym_experiments()
        # self.pretty_plot_results(theta_sys_results, 'Changing theta sym parameter')
        #
        # theta_js_results = self.run_theta_js_experiments()
        # self.pretty_plot_results(theta_js_results, 'Changing theta js parameter')
        #
        # n_top_results = self.run_n_top_experiments()
        # self.pretty_plot_results(n_top_results, 'Changing n top parameter')

    def pretty_plot_results(self, results, experiment_name, log_plot=False):
        self.print_experiment_statistics(results, experiment_name)
        #self.print_local_statistics(results['local'])
        #self.plot_global_trends(results['global'], experiment_name, log_plot)
        #self.plot_local_trends(results['local'], experiment_name, log_plot)

    @staticmethod
    def print_local_statistics(local_results):
        for param, values1 in local_results.items():
            print(f'Parameter Value {param}')
            print("-" * 30)
            for node, values2 in values1.items():
                print(f"Node {node}")
                for label, mean_and_std_data in values2.items():
                    print(f"{label} : {round(mean_and_std_data[0], 3)}+/-{round(mean_and_std_data[1], 3)}")
                print('')

    @staticmethod
    def plot_global_trends(global_results, exp_name, log_plot):
        x = []
        labels = set()
        y_data = defaultdict(lambda: [])
        for param, values in global_results.items():
            x.append(param)
            for label, data in values.items():
                labels.add(label)
                y_data[label].append(data)

        for label, data in y_data.items():
            plt.errorbar(x, [mean_std[0] for mean_std in data], yerr=[mean_std[1] for mean_std in data], linestyle='',
                         ecolor='k', marker='o')
            plt.title(exp_name + ' (database statistics)')
            plt.ylabel(label)
            if log_plot:
                plt.xscale('log')
            plt.savefig(f'figures/{exp_name}_{label}_global.pdf')
            plt.show()

    def plot_local_trends(self, local_results, exp_name, log_plot):
        x = []
        labels = set()
        y_data = defaultdict(lambda: [])
        for param, values in local_results.items():
            x.append(param)
            averaged_values = self.calculate_local_average_std(values)
            for label, data in averaged_values.items():
                labels.add(label)
                y_data[label].append(data)

        for label, data in y_data.items():
            plt.errorbar(x, [mean_std[0] for mean_std in data], yerr=[mean_std[1] for mean_std in data], linestyle='',
                         ecolor='k', marker='o')
            plt.title(exp_name + ' (node statistics)')
            plt.ylabel('std in ' + label)
            if log_plot:
                plt.xscale('log')
            plt.savefig(f'figures/{exp_name}_{label}_local.pdf')
            plt.show()

    @staticmethod
    def convert_local_summary_stats_to_global_summary_stats(local_results):
        global_results = defaultdict(lambda: [])
        for node, node_data in local_results.items():
            for label, quantity in node_data.items():
                mean_quantity = quantity[0]
                if not np.isnan(mean_quantity):
                    global_results[label].append(mean_quantity)
        average_global_results = defaultdict(lambda: [])
        for label, quantity_list in global_results.items():
            average_global_results[label] = [np.mean(global_results[label]), np.std(global_results[label])]

        return average_global_results

    @staticmethod
    def calculate_local_average_std(local_results):
        std_dict = defaultdict(lambda: [])
        labels = next(iter(local_results.values())).keys()
        for node, values in local_results.items():
            for label in labels:
                std_dict[label].append(values[label][1])

        ave_std_dict = {}
        for label in labels:
            ave_std_dict[label] = [np.mean(std_dict[label]), np.std(std_dict[label])]

        return ave_std_dict

    def print_experiment_statistics(self, results, experiment_name):
        print("=" * 50)
        print(f"EXPERIMENT : {experiment_name}")
        print("=" * 50)
        print(f"Global statistics:")
        print("- -" * 25)
        for label, values in results['global'].items():
            print(f'Parameter Value : {label}')
            print("-" * 30)
            for sub_label, mean_and_std_data in values.items():
                print(f"{sub_label} : {round(mean_and_std_data[0], 3)}+/-{round(mean_and_std_data[1], 3)}")
            print('')
        print(f"Local statistics:")
        print("- -" * 25)
        for label, values in results['local'].items():
            print(f'Parameter Value : {label}')
            print("-" * 30)
            for sub_label, mean_and_std_data in self.calculate_local_average_std(values).items():
                print(f"{sub_label} : {round(mean_and_std_data[0], 3)}+/-{round(mean_and_std_data[1], 3)}")
            print('')

    def run_experiments(self, exp_param_name, exp_params):
        results = {'global': {}, 'local': {}}
        for exp_param in exp_params:
            config = self.default_config.copy()
            config[exp_param_name] = exp_param
            data_dictionary = defaultdict(lambda: {'num_single_nodes': [], 'num_clusters': [], 'ave_cluster_size': []})
            for run in range(self.repeats):
                communities = self.hypergraph.generate_communities(config)
                for community in communities:
                    source = community.source_node.name
                    num_single_nodes = len(community.single_nodes)
                    num_clusters = len(community.node_clusters)
                    data_dictionary[source]['num_single_nodes'].append(num_single_nodes)
                    data_dictionary[source]['num_clusters'].append(num_clusters)
                    if num_clusters > 0:
                        ave_cluster_size = np.mean([len(node_cluster) for node_cluster in community.node_clusters])
                        data_dictionary[source]['ave_cluster_size'].append(ave_cluster_size)

            run_averaged_data_dictionary = defaultdict(
                lambda: {'num_single_nodes': [], 'num_clusters': [], 'ave_cluster_size': []})
            for node in data_dictionary.keys():
                run_averaged_data_dictionary[node]['num_single_nodes'] = [
                    np.mean(data_dictionary[node]['num_single_nodes'])
                    , np.std(data_dictionary[node]['num_single_nodes'])]
                run_averaged_data_dictionary[node]['num_clusters'] = [np.mean(data_dictionary[node]['num_clusters'])
                    , np.std(data_dictionary[node]['num_clusters'])]

                if len(data_dictionary[node]['ave_cluster_size']) > 0:
                    run_averaged_data_dictionary[node]['ave_cluster_size'] = [
                        np.mean(data_dictionary[node]['ave_cluster_size'])
                        , np.std(data_dictionary[node]['ave_cluster_size'])]
                else:
                    run_averaged_data_dictionary[node]['ave_cluster_size'] = [0,0]

            results['local'][exp_param] = run_averaged_data_dictionary
            results['global'][exp_param] = self.convert_local_summary_stats_to_global_summary_stats(
                run_averaged_data_dictionary)


        return results

    def run_number_of_walks_experiments(self):
        return self.run_experiments(exp_param_name='num_walks', exp_params=self.walk_lengths)

    def run_walk_length_experiments(self):
        return self.run_experiments(exp_param_name='max_length', exp_params=self.walk_sizes)

    def run_theta_hit_experiments(self):
        return self.run_experiments(exp_param_name='theta_hit', exp_params=self.theta_hits)

    def run_theta_sym_experiments(self):
        return self.run_experiments(exp_param_name='theta_sym', exp_params=self.theta_syms)

    def run_theta_js_experiments(self):
        return self.run_experiments(exp_param_name='theta_js', exp_params=self.theta_jss)

    def run_n_top_experiments(self):
        return self.run_experiments(exp_param_name='n_tops', exp_params=self.n_tops)

    def run_k_test_experiments(self):
        pass
        # return self.run_experiments(exp_param_name='walk_scaling_param', exp_params=self.walk_lengths)
