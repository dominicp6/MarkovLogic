import subprocess
import signal
import os
import errno
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from functools import wraps
from collections import defaultdict


def timeout(seconds=7, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator


class InferenceRunner(object):

    def __init__(self,
                 info_file,
                 evidence_databases,
                 data_dir='Evaluation/Data',
                 mln_dir='Evaluation/MLNs',
                 infer_dir='alchemy-2/bin',
                 results_dir='Evaluation/Results',
                 ):
        self.info_file = info_file
        self.evidence_databases = evidence_databases
        self.infer_dir = infer_dir
        self.mln_dir = mln_dir
        self.results_dir = results_dir
        self.data_dir = data_dir

        self.inference_results = defaultdict(lambda: defaultdict(lambda: []))

        self.evaluation_statistics = defaultdict(lambda: defaultdict(lambda: []))

    def run_inference_on_MLNs(self, mln_files: list[str], experiment_name):
        self.experiment_name=experiment_name
        self.mln_files = mln_files

        for mln in mln_files:
            print(f'Running inference on {mln}')
            self.run_inference_on_MLN(mln)
            self._remove_temporary_files_produced_during_structure_learning()

        self._evaluate_CLL_of_MLNs()
        self._write_CLL_log_file()
        print(self.evaluation_statistics)

    def _write_CLL_log_file(self):
        self.log_file_name = f'{self.experiment_name}.log'
        with open(self.log_file_name, 'w') as log_file:
            log_file.write('CLL EVALUTATION ------------------------------ \n')
            log_file.write(f'mlns = {self.mln_files}\n')
            log_file.write(f'evidence_databases = {self.evidence_databases}\n')
            log_file.write('\n')
            json.dump(self.evaluation_statistics, log_file, indent=4)

    def _remove_temporary_files_produced_during_structure_learning(self):
        cwd = os.getcwd()
        pard = os.path.dirname(cwd)
        files_in_cwd = os.listdir(cwd)
        temp_files = [file for file in files_in_cwd if file.endswith("_tmpalchemy.mln")]
        self._delete_files(temp_files, parent_directory=cwd)
        self._delete_files(temp_files, parent_directory=pard)

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
                pass

    def run_inference_on_MLN(self, mln: str):
        """
        Runs the Alchemy inference program on a specified MLN, given evidence databases.
        """
        for evidence_database in self.evidence_databases:
            print(f"... {evidence_database} as evidence database")
            self.run_inference_on_database(evidence_database, mln)

        return None

    def run_inference_on_database(self, evidence_database, mln):
        with open(f'{self.data_dir}/{evidence_database}') as evidence_file:
            file_lines = evidence_file.readlines()
            for line in tqdm(file_lines):
                if line != "\n":
                    temp_database = \
                        self._create_evidence_database_with_line_removed(evidence_database, file_lines, line)

                    try:
                        CLL = self.run_inference_on_literal(literal=line.rstrip(),
                                                            mln=mln,
                                                            trimmed_evidence_database=temp_database)
                    except:
                        CLL = None
                        print(f'TimeOut Error on {line.rstrip()}')

                    os.remove(temp_database)

                    if CLL is not None:
                        predicate = line.split('(')[0]
                        self._update_CLL_dict(predicate, CLL, mln)

    @timeout()
    def run_inference_on_literal(self, literal, mln, trimmed_evidence_database):
        mln = self.mln_dir+'/'+mln
        results_file = os.path.join(self.results_dir, 'temp.results')

        inference_command = f'{self.infer_dir}/infer -i {mln} -r {results_file} -e ' \
                            f'{trimmed_evidence_database} -q "{literal}"'
        subprocess.call(inference_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        shell=True)
        CLL = self._get_CLL_from_file(results_file)

        return CLL

    def _evaluate_CLL_of_MLNs(self):
        """
        Computes average conditional log likelihoods from the inference results.
        """
        average_CLL_dict = defaultdict(lambda: [])
        for mln in self.inference_results.keys():
            for predicate in self.inference_results[mln].keys():
                self.evaluation_statistics[mln][predicate] = [np.mean(self.inference_results[mln][predicate]),
                                                              np.std(self.inference_results[mln][predicate]) / np.sqrt(
                                                                  len(self.inference_results[mln][predicate]))]
                average_CLL_dict[predicate].extend(self.inference_results[mln][predicate])

        for predicate in average_CLL_dict.keys():
            mean = np.mean(average_CLL_dict[predicate])
            std = np.std(average_CLL_dict[predicate]) / np.sqrt(len(average_CLL_dict[predicate]))
            average_CLL_dict[predicate] = [mean, std]

        self.evaluation_statistics['average'] = average_CLL_dict

    @staticmethod
    def _create_evidence_database_with_line_removed(evidence_database: str,
                                                    lines_of_evidence_database: list[str],
                                                    line: str):
        literal_string = line.replace("(", "").replace(")", "").replace(",", "").rstrip()
        file_lines_without_target_literal = lines_of_evidence_database.copy()
        file_lines_without_target_literal.remove(line)
        temp_evidence_db = f"{evidence_database.split('/')[-1].strip('.db')}_minus_{literal_string}.db"
        with open(temp_evidence_db, "w") as trimmed_evidence_database:
            for evidence_atom in file_lines_without_target_literal:
                trimmed_evidence_database.write(evidence_atom)

        return temp_evidence_db

    @staticmethod
    def _get_CLL_from_file(file):
        results_new_dataframe = pd.read_csv(file,
                                            delimiter=' ',
                                            names=['Ground_Atom', 'probability'])
        try:
            probability = results_new_dataframe['probability'][0]
            if probability > 0:
                CLL = np.log(probability)
            else:
                CLL = None
        except:
            CLL = None

        return CLL

    def _update_CLL_dict(self, predicate, CLL, mln):
        self.inference_results[mln][predicate].append(CLL)
        self.inference_results[mln]['average'].append(CLL)

    def _get_query_predicates(self):
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


if __name__ == "__main__":
    inference_runner = InferenceRunner('imdb.info', ['imdb2.db', 'imdb3.db', 'imdb4.db', 'imdb5.db'])


    # Experiment 2
    # exp_2_mlns = ['imdb1.db_2_0-rules-out.mln',
    #               'imdb1.db_2_1-rules-out.mln',
    #               'imdb1.db_2_2-rules-out.mln',
    #               'imdb1.db_2_3-rules-out.mln',
    #               'imdb1.db_2_4-rules-out.mln']
    # inference_runner.run_inference_on_MLNs(mln_files=exp_2_mlns, experiment_name='experiment_2')
    #
    # Experiment 3
    # exp_3_mlns = ['imdb1.db_3_0-rules-out.mln',
    #               'imdb1.db_3_1-rules-out.mln',
    #               'imdb1.db_3_2-rules-out.mln',
    #               'imdb1.db_3_3-rules-out.mln',
    #               'imdb1.db_3_4-rules-out.mln']
    # inference_runner.run_inference_on_MLNs(mln_files=exp_3_mlns, experiment_name='experiment_3')


    # # Experiment 4
    # exp_4_mlns = ['imdb1.db_4_0-rules-out.mln',
    #               'imdb1.db_4_1-rules-out.mln',
    #               'imdb1.db_4_2-rules-out.mln',
    #               'imdb1.db_4_3-rules-out.mln',
    #               'imdb1.db_4_4-rules-out.mln']
    # inference_runner.run_inference_on_MLNs(mln_files=exp_4_mlns, experiment_name='experiment_4')


    # Experiment 5
    exp_5_mlns = ['imdb1.db_5_0-rules-out.mln',
                  'imdb1.db_5_1-rules-out.mln',
                  'imdb1.db_5_2-rules-out.mln',
                  'imdb1.db_5_3-rules-out.mln',
                  'imdb1.db_5_4-rules-out.mln']
    inference_runner.run_inference_on_MLNs(mln_files=exp_5_mlns, experiment_name='experiment_5')

    # Experiment 6
    exp_6_mlns = ['imdb1.db_6_0-rules-out.mln',
                  'imdb1.db_6_1-rules-out.mln',
                  'imdb1.db_6_2-rules-out.mln',
                  'imdb1.db_6_3-rules-out.mln',
                  'imdb1.db_6_4-rules-out.mln']
    inference_runner.run_inference_on_MLNs(mln_files=exp_6_mlns, experiment_name='experiment_6')
