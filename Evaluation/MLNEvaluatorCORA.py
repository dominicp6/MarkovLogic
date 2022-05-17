import os
import pandas as pd
import numpy as np
import subprocess
import time
import itertools
from multiprocessing import Pool, cpu_count


class MLNEvaluator(object):
    def __init__(self, lsm_dir='/home/dominic/PycharmProjects/MarkovLogic/lsmcode',
                 faster_dir='/home/dominic/CLionProjects/FASTER',
                 infer_dir='/home/dominic/PycharmProjects/MarkovLogic/alchemy-2/bin',
                 data_dir='/home/dominic/CLionProjects/FASTER/Databases/old_imdb',
                 mln_dir='/home/dominic/CLionProjects/FASTER/Experiments/old_imdb',
                 log_dir='/home/dominic/CLionProjects/FASTER/Experiments/old_imdb',
                 results_dir='/home/dominic/CLionProjects/FASTER/Experiments/old_imdb',
                 inference_calculations_dir='/home/dominic/CLionProjects/FASTER/Experiments/old_imdb',
                 database_files=None,
                 info_file=None,
                 type_file=None,
                 delete_generated_files=False,
                 parallel_structure_learning=False,
                 only_FASTER=False,
                 only_ALCHEMY=False,
                 number_to_run=None,
                 combined_database_evaluation=False,
                 FASTER_parameters=None,
                 master_results_file=None,
                 individual_query_predicates=False,
                 FASTER_timeout=5):

        assert not (only_FASTER and only_ALCHEMY), "only_FASTER and only_ALCHEMY cannot both be True!"

        self.database_files = database_files
        # specifies whether onto to run the pipeline on the first N mlns rather than all possible MLNs
        if number_to_run is None:
            self.number_to_run = len(self.database_files)
        else:
            self.number_to_run = number_to_run
        self.info_file = info_file
        self.type_file = type_file
        if self.database_files is None or self.info_file is None or self.type_file is None:
            raise ValueError('database_files, info_file and type_file must be specified!')

        self.lsm_dir = lsm_dir
        self.faster_dir = faster_dir
        self.infer_dir = infer_dir
        self.data_dir = data_dir
        self.mln_dir = mln_dir
        self.log_dir = log_dir
        self.results_dir = results_dir
        self.inference_calculations_dir = inference_calculations_dir
        self.only_FASTER = only_FASTER
        self.only_ALCHEMY = only_ALCHEMY
        self.combined_database_evaluation = combined_database_evaluation
        self.parallel_structure_learning = parallel_structure_learning
        self.master_results_file = master_results_file
        # epsilon, alpha, multiprocessing, lambda, min clust size
        if FASTER_parameters is None:
            self.FASTER_parameters = [0.1, 0.001, 1, 0.8, 10]
        else:
            self.FASTER_parameters = FASTER_parameters
        self.individual_query_predicates = individual_query_predicates

        self.delete_generated_files = delete_generated_files
        self.FASTER_timeout = FASTER_timeout

        self.FASTER_suffix = '_FASTER'  # file suffix used when running FASTER
        self.alchemy_suffix = '_alchemy'  # file suffix used when running alchemy

        self.config = {
            'num_walks': 10000,
            'max_length': 5,
            'theta_hit': 4.9,
            'theta_sym': 0.1,
            'theta_js': 1,
            'num_top': 3
        }

    def execute_experiments(self, skip_structure_learning=False, skip_inference=False, skip_evaluation=False):
        # 1) STRUCTURE LEARN #############################################
        if not skip_structure_learning:
            print("")
            print(" 1. Structure Learn")
            self.structure_learn_MLNs()

        # 2) INFERENCE ###################################################
        if not skip_inference:
            print("")
            print(" 2. Run Inference")
            self.run_inference_on_MLNs()

        # 3) EVALUATE ####################################################
        if not skip_evaluation:
            print("")
            print(" 3. Evaluate")
            self.evaluate_MLNs()
            print("")

    def structure_learn_MLNs(self):
        if not self.only_FASTER:
            self._structure_learn_with_alchemy()
        if not self.only_ALCHEMY:
            self._structure_learn_with_FASTER()

    def _structure_learn_with_alchemy(self):
        self._run_alchemy_random_walks()
        print("Alchemy Random Walks Finished")
        self._run_rest_of_structure_learning_pipeline('alchemy')
        print(".", end="")

    def _run_alchemy_random_walks(self):
        motif_times = []
        for database in self.database_files:
            save_name = database.rstrip('.db') + self.alchemy_suffix
            random_walks_command = f'{self.lsm_dir}/rwl/rwl {self.data_dir}/{self.info_file} {self.data_dir}/' \
                                   f'{database} {self.data_dir}/{self.type_file} {self.config["num_walks"]} ' \
                                   f'{self.config["max_length"]} 0.05 0.1 {self.config["theta_hit"]} ' \
                                   f'{self.config["theta_sym"]} {self.config["theta_js"]} {self.config["num_top"]} 1 ' \
                                   f'{self.results_dir}/{save_name}.ldb {self.results_dir}/{save_name}.uldb {self.results_dir}/' \
                                   f'{save_name}.srcnclusts > {self.log_dir}/{save_name}-rwl.log'
            time0 = time.time()
            subprocess.call(random_walks_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
            time1 = time.time()
            motif_times.append(time1 - time0)
            self._log_to_master_file(method='alchemy', quantity='motif_time', database=database, result=time1 - time0)
            print('.', end="")

        self._log_to_master_file(method='alchemy', quantity='motif_time',
                                 database='database average and std:',
                                 result=f'{round(float(np.mean(motif_times)), 4)} +/- {round(float(np.std(motif_times)), 4)}')


    def _structure_learn_with_FASTER(self):
        self._run_FASTER_random_walks()
        print("FASTER Random Walks Finished")
        self._run_rest_of_structure_learning_pipeline('FASTER')
        print(".", end="")

    def _run_FASTER_random_walks(self):
        motif_times = []
        for database in self.database_files:
            save_name = database.rstrip('.db') + self.FASTER_suffix
            FASTER_command = f'{self.faster_dir}/cmake-build-debug/FASTER {self.data_dir}/{database} {self.data_dir}/' \
                             f'{self.info_file} {self.results_dir}/{save_name} {self.FASTER_parameters[0]} ' \
                             f'{self.FASTER_parameters[1]} {self.FASTER_parameters[2]} ' \
                             f'{self.FASTER_parameters[3]} {self.FASTER_parameters[4]}'
            time0 = time.time()
            try:
                subprocess.call(FASTER_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True,
                               timeout=self.FASTER_timeout)
            except:
                self._log_to_master_file(method='FASTER',
                                         quantity='errors',
                                         database=database,
                                         result=f"FASTER timed out running "
                                                f"motif finding on this database after {self.FASTER_timeout}s")

            time1 = time.time()
            motif_times.append(time1-time0)
            self._log_to_master_file(method='FASTER', quantity='motif_time', database=database, result=time1-time0)
            print('.', end="")

        self._log_to_master_file(method='FASTER', quantity='motif_time',
                                 database='database average and std:',
                                 result=f'{round(float(np.mean(motif_times)), 4)} +/- {round(float(np.std(motif_times)), 4)}')


    def run_inference_on_MLNs(self):
        query_predicates = self.get_query_predicates()
        if self.only_FASTER:
            algorithms = [('FASTER')]
        else:
            algorithms = ('alchemy', 'FASTER')


        if not self.individual_query_predicates:
            inference_exp_params = itertools.product(self.database_files[:self.number_to_run], algorithms)

            pool = Pool(processes=cpu_count())
            pool.starmap(self.run_inference_on_MLN_by_method,
                         [(test_database.rstrip('.db'), test_database, query_predicates, algorithm)
                          for (test_database, algorithm)
                          in inference_exp_params])
            pool.close()
        else:
            query_predicate_list = query_predicates.split(',')
            inference_exp_params = itertools.product(self.database_files[:self.number_to_run], algorithms, query_predicate_list)
            print(inference_exp_params)
            pool = Pool(processes=cpu_count())
            pool.starmap(self.run_inference_on_MLN_by_method,
                         [(test_database.rstrip('.db'), test_database, query_predicate, algorithm)
                          for (test_database, algorithm, query_predicate)
                          in inference_exp_params])
            pool.close()


    def run_inference_on_MLN_by_method(self, mln: str, test_database: str,
                                       query_predicates: str, method: str):
        mln += self._get_file_suffix_from_method(method)
        prefixed_mln = "NOT"+mln
        self.run_inference_on_MLN(prefixed_mln, test_database, query_predicates)

    def evaluate_MLNs(self):
        if not self.only_FASTER:
            self.evaluate_MLNs_by_method('alchemy')
        self.evaluate_MLNs_by_method('FASTER')

    def evaluate_MLNs_by_method(self, method):
        pool = Pool(processes=cpu_count())
        pool.starmap(self._evaluate_MLN, [(database, method) for database in self.database_files[:self.number_to_run]])

    def _evaluate_MLN(self, test_database, method):
        print(f' Evaluating {method} on {test_database}...')
        CLL = self.compute_CLL_on_test_database(method, test_database)
        self._log_to_master_file(method=method, quantity='inference_result', database='NOT'+test_database, result=CLL, test_database=test_database)
        print(".", end="")

        average_formula_length, max_formula_length, number_of_formulas = self.compute_average_formula_length_and_number_of_formulas(test_database, method)
        self._log_to_master_file(method=method,
                                 quantity='mln_statistics',
                                 database='NOT'+test_database,
                                 result=f"#formulas {number_of_formulas} "
                                        f"avg formula length {average_formula_length} "
                                        f"max formula length {max_formula_length}",
                                 )

    def _run_rest_of_structure_learning_pipeline(self, method):
        alchemy_structure_learning_times = []
        FASTER_structure_learning_times = []

        if not self.parallel_structure_learning:
            for database in self.database_files[:self.number_to_run]:
                self._rest_of_pipeline_on_single_dataset(database, method)
        else:
            pool = Pool(processes=cpu_count())
            pool.starmap(self._rest_of_pipeline_on_single_dataset,
                             [(database, method)
                              for database in self.database_files[:self.number_to_run]])

        self._log_to_master_file(method='alchemy', quantity='structure_learning_time', database='average all others',
                                 result=f'{round(float(np.mean(alchemy_structure_learning_times)), 4)} +/- {round(float(np.std(alchemy_structure_learning_times)), 4)}', test_database='leave one out')

        self._log_to_master_file(method='FASTER', quantity='structure_learning_time', database='average all others',
                                 result=f'{round(float(np.mean(FASTER_structure_learning_times)), 4)} +/- {round(float(np.std(FASTER_structure_learning_times)), 4)}',
                                 test_database='leave one out')

    def _rest_of_pipeline_on_single_dataset(self, database, algorithm):
        if algorithm == 'alchemy':
            save_name = database.rstrip('.db') + self.alchemy_suffix
            suffix = self.alchemy_suffix
        elif algorithm == 'FASTER':
            save_name = database.rstrip('.db') + self.FASTER_suffix
            suffix = self.FASTER_suffix
        time0 = time.time()
        print(f' Getting Communities ({algorithm})...')
        self._run_get_communities(database, save_name, suffix)
        print(f' Getting Paths ({algorithm})...')
        self._run_path_finding(save_name)
        print(f' Finding formulas ({algorithm})...')
        self._run_create_MLN_rules(database, save_name, suffix)
        print(f' Calculating weights ({algorithm})...')
        self._run_learn_MLN_weights(database, save_name)
        time1 = time.time()

        self._log_to_master_file(method=algorithm, quantity='structure_learning_time', database='all others',
                                 result=time1-time0, test_database=database)

        return algorithm, time1-time0, database

    def _remove_temporary_files_produced_during_structure_learning(self):
        cwd = os.getcwd()
        files_in_cwd = os.listdir(cwd)
        temp_files = [file for file in files_in_cwd if file.endswith("_tmpalchemy.mln")]
        self._delete_files(temp_files, parent_directory=cwd)
        if self.delete_generated_files:
            files_in_data_dir = os.listdir(self.data_dir)
            generated_files = [file for file in files_in_data_dir if
                               file.endswith((".ldb", ".uldb", '.srcnclusts'))]
            self._delete_files(generated_files, parent_directory=self.data_dir)

    def run_inference_on_MLN(self, mln: str, test_database: str, query_predicates: str):
        """
        Runs the Alchemy inference program on a specified MLN, given evidence databases.
        """
        mln_to_evaluate = os.path.join(self.mln_dir, mln + '-rules-out.mln')
        inference_file = os.path.join(self.inference_calculations_dir, mln + "." + test_database.strip('.db') + '.results')
        inference_command_negative = f'{self.infer_dir}/infer -i {mln_to_evaluate} -r {inference_file}.negative -e ' \
                                     f'{os.path.join(self.data_dir, test_database)} -q {query_predicates} -maxSteps 300'
        inference_command_positive = f'{self.infer_dir}/infer -i {mln_to_evaluate} -r {inference_file}.positive -e ' \
                                     f'{os.path.join(self.data_dir, test_database)} -q {query_predicates} -maxSteps 300 -queryEvidence 1'
        print(f' Running +ve inference on {mln}...')
        subprocess.call(inference_command_positive, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        print(".", end="")
        print(f' Running -ve inference on {mln}...')
        subprocess.call(inference_command_negative, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)
        print(".", end="")

    def get_query_predicates(self):
        """
        Reads from an info file a list of predicates to be used as queries for inference.

                smoking.info
                ----------------------
                Friends(person, person)
        e.g.    Smokes(person)             returns    'Friends, Smokes, Cancer'
                Cancer(person)
        """
        file = open(os.path.join(self.data_dir, self.info_file), 'r')
        query_atoms = []
        for line in file.readlines():
            comment_symbol = '//'
            if line[0:2] == comment_symbol:
                continue
            atom_name = line.split('(')[0]
            query_atoms.append(atom_name)

        query_atom_string = ','.join(query_atoms)
        return query_atom_string

    def compute_CLL_on_test_database(self, method, test_database):
        file_suffix = self._get_file_suffix_from_method(method)
        results_new_file = 'NOT'+test_database.rstrip('.db') + f'{file_suffix}.{test_database.strip(".db")}.results'
        negative_results = pd.read_csv(os.path.join(self.inference_calculations_dir, results_new_file + '.negative'), delimiter=' ',
                                       names=['Ground_Atom', 'prob'])

        positive_results = pd.read_csv(os.path.join(self.inference_calculations_dir, results_new_file + '.positive'), delimiter=' ',
                                       names=['Ground_Atom', 'prob'])
        negative_probability_values = []
        positive_probability_values = []
        for ground_atom in negative_results['Ground_Atom']:
            negative_probability_values.append(
                1 - negative_results.loc[negative_results['Ground_Atom'] == ground_atom].iloc[0]['prob'])
        for ground_atom in positive_results['Ground_Atom']:
            positive_probability_values.append(
                positive_results.loc[positive_results['Ground_Atom'] == ground_atom].iloc[0]['prob'])

        probability_values = negative_probability_values + positive_probability_values
        average_CLL = np.log(np.mean(probability_values))

        return average_CLL

    def compute_average_formula_length_and_number_of_formulas(self, database_file, method):
        file_suffix = self._get_file_suffix_from_method(method)
        mln_file_name = 'NOT'+database_file.rstrip('.db') + f'{file_suffix}-rules-out.mln'
        with open(os.path.join(self.mln_dir, mln_file_name), 'r') as mln_file:
            formula_lengths = []
            for line in mln_file.readlines():
                split_line = line.split('  ')
                try:
                    float(split_line[0])  # Line corresponds to a formula if it starts with a floating point number (formula weight)
                    formula = split_line[1]
                    formula_length = len(formula.split(' v '))
                    formula_lengths.append(formula_length)
                except:
                    continue  # Line was not a formula
            number_of_formulas = len(formula_lengths)

        try:
            return sum(formula_lengths) / len(formula_lengths), max(formula_lengths), number_of_formulas
        except:
            return -1, -1, -1

    def _run_get_communities(self, database, save_name, suffix):
        ldb_training_files = ','.join([os.path.join(self.results_dir, database_file.rstrip('.db')+suffix+'.ldb')
                                       for database_file in self.database_files
                                       if database_file != database])
        uldb_training_files = ','.join([os.path.join(self.results_dir, database_file.rstrip('.db')+suffix+'.uldb')
                                        for database_file in self.database_files if
                                        database_file != database])
        srcnclusts_training_files = ','.join([os.path.join(self.results_dir, database_file.rstrip('.db')+suffix+'.srcnclusts')
                                              for database_file in self.database_files if
                                              database_file != database])
        training_files_string = ldb_training_files + " " + uldb_training_files + " " + srcnclusts_training_files

        get_communities_command = f'{self.lsm_dir}/getcom/getcom {training_files_string} {self.data_dir}/' \
                                  f'{self.info_file} 10 {self.results_dir}/NOT{save_name}.comb.ldb NOOP true 1 > ' \
                                  f'{self.log_dir}/NOT{save_name}-getcom.log '
        subprocess.call(get_communities_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    def _run_path_finding(self, save_name):
        path_finding_command = f'{self.lsm_dir}/pfind2/pfind {self.results_dir}/NOT{save_name}.comb.ldb 5 0 5 -1.0 ' \
                               f'{self.data_dir}/{self.info_file} {self.results_dir}/NOT{save_name}.rules > ' \
                               f'{self.log_dir}/NOT{save_name}-findpath.log'
        subprocess.call(path_finding_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    def _run_create_MLN_rules(self, database, save_name, suffix):
        db_training_files = ','.join([os.path.join(self.data_dir, database_file)
                                      for database_file in self.database_files
                                      if database_file != database])
        uldb_training_files = ','.join([os.path.join(self.results_dir, database_file.rstrip('.db')+suffix+ '.uldb')
                                        for database_file in self.database_files if
                                        database_file != database])

        create_mln_rules_command = f'{self.lsm_dir}/createrules/createrules {self.results_dir}/NOT{save_name}.rules 0 ' \
                                   f'{db_training_files} {self.results_dir}/NOT{save_name}.comb.ldb ' \
                                   f'{uldb_training_files} {self.data_dir}/{self.info_file} ' \
                                   f'{self.lsm_dir}/alchemy30/bin/learnwts ' \
                                   f'{self.lsm_dir}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 5 {self.mln_dir}/' \
                                   f'NOT{save_name}-rules.mln 1 - - true false 40 > {self.log_dir}/' \
                                   f'NOT{save_name}-createrules.log'
        subprocess.call(create_mln_rules_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    def _run_learn_MLN_weights(self, database, test_database):
        db_training_files = ','.join([os.path.join(self.data_dir, database_file)
                                       for database_file in self.database_files
                                       if database_file != test_database])
        learn_mln_weights_command = f'{self.lsm_dir}/alchemy30/bin/learnwts -g -i {self.mln_dir}/' \
                                    f'NOT{test_database}-rules.mln -o {self.mln_dir}/NOT{test_database}-rules-out.mln -t ' \
                                    f'{db_training_files}'
        subprocess.call(learn_mln_weights_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)

    def _get_file_suffix_from_method(self, method):
        if method == 'alchemy':
            return self.alchemy_suffix
        elif method == 'FASTER':
            return self.FASTER_suffix
        else:
            raise ValueError('method variable must be either "alchemy" or "FASTER"')

    @staticmethod
    def _delete_files(file_names, parent_directory):
        """
        Deletes every file in a given list of file_names found in the directory parent_directory.
        """
        for file in file_names:
            path_to_file = os.path.join(parent_directory, file)
            try:
                os.remove(path_to_file)
            except:
                print(f'Warning: File Not Found {path_to_file}')

    def _log_to_master_file(self, method, quantity, database, result, test_database=None):
        # quantity can be "motif_time", "structure_learning_time", "mln_statistics", "inference_results" or "errors"
        if self.master_results_file is not None:
            with open(self.master_results_file+f"_{method}_{quantity}", "a") as f:
                if test_database is not None:
                    print(f"{database} MLN on {test_database}, {result}", file=f)
                else:
                    print(f"{database}, {result}", file=f)

    # TODO remove after debug
    def print_commands(self, database, test_database):
        save_name = database.rstrip('.db') + self.FASTER_suffix
        mln = database.rstrip('.db')
        inference_file = os.path.join(self.inference_calculations_dir,mln + "." + test_database.strip('.db') + '.results')
        query_predicates = self.get_query_predicates()
        print('FASTER')
        print('Random Walks')
        print(f'{self.faster_dir}/cmake-build-debug/FASTER {self.data_dir}/{database} {self.data_dir}/' \
        f'{self.info_file} {self.results_dir}/{save_name} {self.FASTER_parameters[0]} ' \
        f'{self.FASTER_parameters[1]} {self.FASTER_parameters[2]} ' \
        f'{self.FASTER_parameters[3]} {self.FASTER_parameters[4]}')
        print('Get Communities')
        print(f'{self.lsm_dir}/getcom/getcom {self.results_dir}/{save_name}.ldb {self.results_dir}/' \
        f'{save_name}.uldb {self.results_dir}/{save_name}.srcnclusts {self.data_dir}/' \
        f'{self.info_file} 10 {self.results_dir}/{save_name}.comb.ldb NOOP true 1 > ' \
        f'{self.log_dir}/{save_name}-getcom.log ')
        print('Find Paths')
        print(f'{self.lsm_dir}/pfind2/pfind {self.results_dir}/{save_name}.comb.ldb 5 0 5 -1.0 ' \
        f'{self.data_dir}/{self.info_file} {self.results_dir}/{save_name}.rules > ' \
        f'{self.log_dir}/{save_name}-findpath.log')
        print('Make MLN')
        print(f'{self.lsm_dir}/createrules/createrules {self.results_dir}/{save_name}.rules 0 ' \
        f'{self.data_dir}/{database} {self.results_dir}/{save_name}.comb.ldb ' \
        f'{self.results_dir}/{save_name}.uldb {self.data_dir}/{self.info_file} ' \
        f'{self.lsm_dir}/alchemy30/bin/learnwts ' \
        f'{self.lsm_dir}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 {self.mln_dir}/' \
        f'{save_name}-rules.mln 1 - - true false 40 > {self.log_dir}/' \
        f'{save_name}-createrules.log')
        print('Learn Weights')
        print(f'{self.lsm_dir}/alchemy30/bin/learnwts -g -i {self.mln_dir}/' \
        f'{save_name}-rules.mln -o {self.mln_dir}/{save_name}-rules-out.mln -t ' \
        f'{self.data_dir}/{database}')
        print('Run Inference Positive')
        mln_to_evaluate = os.path.join(self.mln_dir, mln + '-rules-out.mln')
        print(f'{self.infer_dir}/infer -i {mln_to_evaluate} -r {inference_file}.positive -e ' \
        f'{os.path.join(self.data_dir, test_database)} -q {query_predicates} -maxSteps 300 -queryEvidence 1')
        print('Run Inference Negative')
        print(f'{self.infer_dir}/infer -i {mln_to_evaluate} -r {inference_file}.negative -e ' \
        f'{os.path.join(self.data_dir, test_database)} -q {query_predicates} -maxSteps 300')

        save_name = database.rstrip('.db') + self.alchemy_suffix
        print("")
        print('Alchemy')
        print('Random Walks')
        print(f'{self.lsm_dir}/rwl/rwl {self.data_dir}/{self.info_file} {self.data_dir}/' \
        f'{database} {self.data_dir}/{self.type_file} {self.config["num_walks"]} ' \
        f'{self.config["max_length"]} 0.05 0.1 {self.config["theta_hit"]} ' \
        f'{self.config["theta_sym"]} {self.config["theta_js"]} {self.config["num_top"]} 1 ' \
        f'{self.results_dir}/{save_name}.ldb {self.results_dir}/{save_name}.uldb {self.results_dir}/' \
        f'{save_name}.srcnclusts > {self.log_dir}/{save_name}-rwl.log')
        print('Get Communities')
        print(f'{self.lsm_dir}/getcom/getcom {self.results_dir}/{save_name}.ldb {self.results_dir}/' \
        f'{save_name}.uldb {self.results_dir}/{save_name}.srcnclusts {self.data_dir}/' \
        f'{self.info_file} 10 {self.results_dir}/{save_name}.comb.ldb NOOP true 1 > ' \
        f'{self.log_dir}/{save_name}-getcom.log ')
        print('Find Paths')
        print(f'{self.lsm_dir}/pfind2/pfind {self.results_dir}/{save_name}.comb.ldb 5 0 5 -1.0 ' \
        f'{self.data_dir}/{self.info_file} {self.results_dir}/{save_name}.rules > ' \
        f'{self.log_dir}/{save_name}-findpath.log')
        print('Make MLN')
        print(f'{self.lsm_dir}/createrules/createrules {self.results_dir}/{save_name}.rules 0 ' \
        f'{self.data_dir}/{database} {self.results_dir}/{save_name}.comb.ldb ' \
        f'{self.results_dir}/{save_name}.uldb {self.data_dir}/{self.info_file} ' \
        f'{self.lsm_dir}/alchemy30/bin/learnwts ' \
        f'{self.lsm_dir}/createrules/tmpdir 0.5 0.1 0.1 100 5 100 1000 1 {self.mln_dir}/' \
        f'{save_name}-rules.mln 1 - - true false 40 > {self.log_dir}/' \
        f'{save_name}-createrules.log')
        print('Learn Weights')
        print(f'{self.lsm_dir}/alchemy30/bin/learnwts -g -i {self.mln_dir}/' \
        f'{save_name}-rules.mln -o {self.mln_dir}/{save_name}-rules-out.mln -t ' \
        f'{self.data_dir}/{database}')
        print('Run Inference Positive')
        mln_to_evaluate = os.path.join(self.mln_dir, mln + '-rules-out.mln')
        print(f'{self.infer_dir}/infer -i {mln_to_evaluate} -r {inference_file}.positive -e ' \
        f'{os.path.join(self.data_dir, test_database)} -q {query_predicates} -maxSteps 300 -queryEvidence 1')
        print('Run Inference Negative')
        print(f'{self.infer_dir}/infer -i {mln_to_evaluate} -r {inference_file}.negative -e ' \
        f'{os.path.join(self.data_dir, test_database)} -q {query_predicates} -maxSteps 300')



if __name__ == "__main__":
    # CHECKLIST FOR GETTING EXPERIMENTS WORKING
    # 1) Install and compile Alchemy
    # 2) Install and compile FASTER
    # 3) Download datasets
    # 4) Create correct directory structure
    # 5) Modify this .py file to make sure that the paths are all correct
    # 6) Check the code by running this file on dummy datasets that are quick to structure learn
    # 6) Run it on the real dataset!

    cora_evaluator = MLNEvaluator(data_dir='/home/dominic/CLionProjects/FASTER/Databases/cora.ie',
                                    mln_dir='/home/dominic/CLionProjects/FASTER/Experiments/cora/mlns',
                                    results_dir='/home/dominic/CLionProjects/FASTER/Experiments/cora/results',
                                    log_dir='/home/dominic/CLionProjects/FASTER/Experiments/cora',
                                    inference_calculations_dir='/home/dominic/CLionProjects/FASTER/Experiments/cora/results/inference',
                                    database_files=['micro1.db', 'micro2.db'],
                                    delete_generated_files=False,
                                    info_file='micro.info',
                                    type_file='micro.type',
                                    FASTER_parameters=[0.2, 0.01, 1, 0.8, 10],
                                    only_FASTER=False,
                                    only_ALCHEMY=False,
                                    parallel_structure_learning=True,
                                    combined_database_evaluation=False,
                                    master_results_file='/home/dominic/CLionProjects/FASTER/Experiments/cora',
                                    individual_query_predicates=True,
                                    FASTER_timeout=1800)
    cora_evaluator.execute_experiments(skip_structure_learning=False, skip_inference=False, skip_evaluation=False)