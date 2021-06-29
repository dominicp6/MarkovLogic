import re
from errors import InvalidLineSyntaxError


def parse_line(line: str, line_idx: int, file_name: str):
    """
    Parses a correctly-formatted predicate. e.g. Friends(Alice, Bob) returns 'Friends', ['Alice', 'Bob'].
    Returns None, None if the predicate is incorrectly formatted.
    """
    line = line.strip()

    if not is_good_line_syntax(line):
        return None, None

    line_fragments = line.split('(')
    # the predicate name e.g. 'Friends'
    predicate = line_fragments[0]
    # a string of predicate arguments separated by commas e.g. 'Alice, Bob'
    predicate_argument_string = line_fragments[1].split(')')[0]
    # a list of predicate arguments e.g. ['Alice', 'Bob']
    predicate_arguments = [predicate_argument.strip() for predicate_argument in
                           predicate_argument_string.split(',')]

    if predicate is None or predicate_arguments is None:
        raise InvalidLineSyntaxError(line, line_idx, file_name)

    return predicate, predicate_arguments


def is_good_line_syntax(line: str):
    """
    Checks for correct line syntax, returning either True or False.

    For the database and info files, examples of correct line syntax are e.g. Friends(Alice, Bob),
    Family(Jane, Edward, Steve), Smokes(John) - i.e. alpha-numeric characters followed by an open parenthesis
    followed by comma-separated alpha-numeric characters followed by a closed parenthesis.
    """
    correct_syntax = re.match("(\w|-|')+\(((\w|-|')+|((\w|-|')+,\s*)+(\w|-|')+)\)$", line)
    is_correct_syntax = bool(correct_syntax)

    return is_correct_syntax


def is_empty_or_comment(line: str):
    if line is None or line.isspace() or line.lstrip()[0:2] == '//':
        return True
    else:
        return False
