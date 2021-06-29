
class InvalidLineSyntaxError(Exception):
    def __init__(self, line, line_number, file_name):
        self.line = line
        self.line_number = line_number
        self.file_name = file_name

    def __str__(self):
        return f'Line {self.line_number} "{self.line}" of {self.file_name} has incorrect syntax. Make sure that each ' \
               f'predicate is correctly formatted with braces and commas e.g. Friends(person, person)'


class InvalidArgumentType(Exception):
    def __init__(self, argument_name, argument_type, expected_argument_type):
        self.argument_name = argument_name
        self.argument_type = argument_type
        self.expected_argument_type = expected_argument_type

    def __str__(self):
        return f'Argument {self.argument_name} is of type {self.argument_type} but should be of type ' \
               f'{self.expected_argument_type}'


class InvalidArgumentValue(Exception):
    def __init__(self, argument_name, argument_value, lower_bound=-float('inf'), upper_bound=float('inf'), strict=True):
        self.argument_name = argument_name
        self.argument_value = argument_value
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.strict = strict

    def __str__(self):
        if self.lower_bound is not -float('inf') and self.upper_bound is not float('inf'):
            if self.strict:
                return f'Argument {self.argument_name} = {self.argument_value} but should be between ' \
                       f'{self.lower_bound} and {self.upper_bound}'
            else:
                return f'Argument {self.argument_name} = {self.argument_value} but should be between ' \
                       f'{self.lower_bound} and {self.upper_bound} inclusive'
        elif self.lower_bound is not -float('inf'):
            if self.strict:
                return f'Argument {self.argument_name} = {self.argument_value} but should be bigger than ' \
                       f'{self.lower_bound}'
            else:
                return f'Argument {self.argument_name} = {self.argument_value} but should be bigger than or equal to' \
                       f'{self.lower_bound}'
        elif self.upper_bound is not float('inf'):
            if self.strict:
                return f'Argument {self.argument_name} = {self.argument_value} but should be less than ' \
                       f'{self.upper_bound}'
            else:
                return f'Argument {self.argument_name} = {self.argument_value} but should be less than or equal to' \
                       f'{self.upper_bound}'


def check_argument(arg_name, arg_value, expected_type, lower_bound=-float('inf'), upper_bound=+float('inf'),
                   strict_inequalities=True):
    if isinstance(arg_value, expected_type):
        pass
    else:
        raise InvalidArgumentType(arg_name, type(arg_value), expected_type)

    if strict_inequalities:
        if arg_value <= lower_bound or arg_value >= upper_bound:
            raise InvalidArgumentValue(arg_name, arg_value, lower_bound, upper_bound)
        else:
            pass
    else:
        if arg_value < lower_bound or arg_value > upper_bound:
            raise InvalidArgumentValue(arg_name, arg_value, lower_bound, upper_bound, strict=False)
        else:
            pass
