from collections import defaultdict
from MarkovLogic.HierarchicalClustering.database import parse_line, is_empty_or_comment


def get_global_distribution(path_to_db_file):
    with open(path_to_db_file, 'r') as database_file:
        lines_in_db = database_file.readlines()
        # for large databases, use multiprocessing to speed-up line imports
        predicates_and_node_names = [parse_line(line, line_idx, path_to_db_file)
                                     for line_idx, line in enumerate(lines_in_db)
                                     if not is_empty_or_comment(line)]

    predicate_counts = defaultdict(lambda: 0)
    for predicate, node_names in predicates_and_node_names:
        predicate_counts[predicate] += 1

    database_size = len(predicates_and_node_names)
    predicate_probabilities = {predicate: count / database_size for predicate, count in predicate_counts.items()}

    return predicate_probabilities


if __name__ == "__main__":
    get_global_distribution('imdb1.db')
