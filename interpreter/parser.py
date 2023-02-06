from lexer import get_tokens

from pprint import pprint

tokens = []
line_numbers = []

tree = []

def valid_use_syntax(line):
    """
     :param line: takes line of tokens as array
     :return: True if syntax with 'use' is correct, otherwise False
    """
    if len(line) == 2:
        if line[0][0] == 'use':
            if line[1][1] == "lib":
                return True

    return False


function_tree_element = None

def valid_start_syntax(line, line_number):
    """
    takes line of tokens as array + line number

    forms 'function' element of tree
    :return: returns True if syntax with 'start' is correct, otherwise False + SYNTAX ERROR
    """
    global function_tree_element

    function_tree_element = {}

    if line[0][0] == "start" and line[1][1] == "fnc":
        name = line[1][0]

        function_tree_element['line'] = line_number
        function_tree_element['name'] = name
        function_tree_element['args'] = []
        function_tree_element['body'] = []

        # check if we have arguments to fill 'args'
        if len(line) > 2:
            if line[2][0] == '|' and len(line) > 3:
                line = line[3:]

                split = []

                valid = True

                for token in line:
                    # arguments are separated by coma
                    if token[1] == 'sep':
                        if valid_is_syntax(split, line_number):
                            function_tree_element['args'].append(variable_tree_element)
                            split = []
                        else:
                            valid = False
                            break
                    else:
                        split.append(token)

                # we check and add last argument block
                if valid_is_syntax(split, line_number):
                    function_tree_element['args'].append(variable_tree_element)
                else:
                    valid = False

                return valid

        else:
            return True

    return False


# default values of types;
variable_tree_element = None


def valid_is_syntax(block, line_number):

    """
    takes line of tokens as array

    forms 'variable' element of tree
    :return: True if syntax with 'is' is correct, otherwise False + SYNTAX ERROR
    """
    global variable_tree_element

    variable_tree_element = {}

    if len(block) == 3:
        if block[1][0] == "is":
            if block[0][1] == "var":
                if block[2][1] == "typ":
                    variable_tree_element['line'] = line_number
                    variable_tree_element['left'] = block[0]
                    variable_tree_element['operation'] = ['is', 'opr']
                    variable_tree_element['right'] = block[2]

                    return True

    print('INVALID SYNTAX ERROR AT LINE', line_number, ': INVALID VARIABLE ASSIGN')
    return False


return_tree_element = None

def valid_return_syntax(block, line_number):
    """
    takes line of tokens as array

    forms 'return' element of tree
    :return: True if syntax with 'return' is correct, otherwise False + SYNTAX ERROR
    """
    global return_tree_element

    return_tree_element = {}

    if len(block) == 2:
        if block[0] == ['return', 'kwd'] and block[1][1] == 'var':
            return_tree_element['line'] = line_number
            return_tree_element['left'] = None
            return_tree_element['operation'] = ['return', 'kwd']
            return_tree_element['right'] = block[1]

            return True

    print('INVALID SYNTAX ERROR AT LINE', line_number, ': INVALID KEY AFTER \'return\'. VARIABLE EXPECTED')
    return False


break_tree_element = None

def valid_break_syntax(block, line_number):
    """
    takes line of tokens as array

    forms 'break' element of tree
    :return: True if syntax with 'break' is correct, otherwise False + SYNTAX ERROR
    """
    global break_tree_element

    break_tree_element = {}

    if len(block) == 1:
        if block[0] == ['break', 'kwd']:
            break_tree_element['line'] = line_number
            break_tree_element['left'] = None
            break_tree_element['operation'] = block[0]
            break_tree_element['right'] = None

            return True

    print('INVALID SYNTAX ERROR AT LINE', line_number, ': INVALID KEY AFTER \'return\'. VARIABLE EXPECTED')
    return False


# takes line of tokens as array with line_number and adds it to body;
# forms body tree element
body_tree_element = []

def fill_body(line, line_number):
    global body_tree_element

    if ['is', 'opr'] in line:
        if valid_is_syntax(line, line_number):
            body_tree_element.append(variable_tree_element)
        else:
            return
    elif ['return', 'kwd'] in line:
        if valid_return_syntax(line, line_number):
            body_tree_element.append(return_tree_element)
        else:
            return
    elif ['break', 'kwd'] in line:
        if valid_break_syntax(line, line_number):
            body_tree_element.append(break_tree_element)
        else:
            return
    else:
        if not line == ['end', 'kwd']:
            line = nest(line, line_number)
            if line is None:
                body_tree_element = []
                return

            line = operate_calls(line, line_number)

            line = operate_1_helper(line, line_number)

            line = operate_2_helper(line, line_number)

            line = operate_3_helper(line, line_number)

            if isinstance(line, dict):
                line['line'] = line_number

            body_tree_element.append(line)


def has_nesting(line):
    """
    :return: True if line has nesting, otherwise False
    """
    if ['(', 'opr'] in line or [')', 'opr'] in line:
        return True

    return False


def nest(line, line_number):
    """
    nest given line recursively
    """
    # base case - no nesting
    if not has_nesting(line):
        return line
    else:
        nested_line = []
        nested_ = 0
        nested_segment = []
        for token in line:
            if token == ['(', 'opr']:
                nested_ += 1

                if nested_ == 1:
                    continue

            if token == [')', 'opr']:
                nested_ -= 1

            if not nested_ == 0:
                nested_segment.append(token)

            if nested_ == 0:
                if len(nested_segment) == 0:
                    nested_line.append(token)
                else:
                    nested_segment = nest(nested_segment, line_number)
                    nested_line.append(nested_segment)
                    nested_segment = []

        if not nested_ == 0:
            print("INVALID SYNTAX ERROR AT LINE", line_number, ": INVALID NESTING")
            return None

        return nested_line


def operate_separators(segment, line_number):
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment
        for index in range(len(segment)):
            token = segment[index]
            if isinstance(token[0], str):
                if token[1] == 'sep':
                    if token[0] == ',':
                        left = operate_separators(segment[:index], line_number)

                        if len(left) == 1 and isinstance(left[0], dict):
                            left = left[0]

                        right = operate_separators(segment[index + 1:], line_number)

                        if len(right) == 1 and isinstance(right[0], dict):
                            right = right[0]

                        operated_segment = {
                            'left': left[0] if len(left) == 1 else left,
                            'operation': token,
                            'right': right
                        }
                        break

        return operated_segment


def operate_calls(segment, line_number):
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment
        if isinstance(segment, dict):
            operated_segment['right'] = operate_calls(segment['right'], line_number)
            operated_segment['left'] = operate_calls(segment['left'], line_number)
        else:
            for index in range(len(segment)):
                token = segment[index]
                if isinstance(token[0], str):
                    if token[1] == 'opr':
                        if token[0] == '|':
                            left = operate_calls(segment[:index], line_number)

                            if len(left) == 1 and isinstance(left[0], dict):
                                left = left[0]

                            right = operate_separators(segment[index + 1:], line_number)

                            if len(right) == 1 and isinstance(right[0], dict):
                                right = right[0]

                            right = operate_calls(right, line_number)

                            if len(right) == 1 and isinstance(right[0], dict):
                                right = right[0]

                            operated_segment = {
                                'left': left[0] if len(left) == 1 else left,
                                'operation': token,
                                'right': right
                            }
                            break
                else:
                    segment[index] = operate_calls(token, line_number)

        return operated_segment


def operate_1_helper(line, line_number):
    if isinstance(line, dict):
        line['left'] = operate_1_helper(line['left'], line_number)
        line['right'] = operate_1_helper(line['right'], line_number)
        return line
    else:
        line = operate_1(line, line_number)
        return line


def operate_1(segment, line_number):
    """
    nests tree by '=' operator
    """
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment
        for index in range(len(segment)):
            token = segment[index]
            if isinstance(token[0], str):
                if token[1] == 'opr':
                    if token[0] == '=':
                        left = operate_1(segment[:index], line_number)

                        if len(left) == 1 and isinstance(left[0], dict):
                            left = left[0]

                        right = operate_1(segment[index + 1:], line_number)

                        if len(right) == 1 and isinstance(right[0], dict):
                            right = right[0]

                        operated_segment = {
                            'left': left[0] if len(left) == 1 else left,
                            'operation': token,
                            'right': right[0] if len(right) == 1 else right
                        }
                        break
            else:
                segment[index] = operate_1(token, line_number)

        return operated_segment


def operate_2_helper(line, line_number):
    """
        used to handle already nested segments
    """
    if isinstance(line, dict):
        line['left'] = operate_2_helper(line['left'], line_number)
        line['right'] = operate_2_helper(line['right'], line_number)
        return line
    else:
        line = operate_2(line, line_number)
        return line


def operate_2(segment, line_number):
    """
        nests tree by '+' or(and) '-' operators
    """
    if len(segment) == 1 and isinstance(segment[0], str):
        return segment
    else:
        operated_segment = segment

        for index in range(len(segment)):
            token = segment[index]
            if isinstance(token[0], str):
                if len(token) >= 2:
                    if token[1] == 'opr':
                        if token[0] == '+' or token[0] == '-':
                            left = operate_2(segment[:index], line_number)

                            if len(left) == 1 and isinstance(left[0], dict):
                                left = left[0]

                            right = operate_2(segment[index + 1:], line_number)

                            if len(right) == 1 and isinstance(right[0], dict):
                                right = right[0]

                            operated_segment = {
                                'left': left[0] if len(left) == 1 else left,
                                'operation': token,
                                'right': right[0] if len(right) == 1 else right
                            }
                            break
            else:
                segment[index] = operate_2(token, line_number)

        return operated_segment


def operate_3_helper(line, line_number):
    """
        used to handle already nested segments recursively
    """
    if isinstance(line, dict):
        line['left'] = operate_3_helper(line['left'], line_number)
        line['right'] = operate_3_helper(line['right'], line_number)
        return line
    else:
        line = operate_3(line, line_number)
        return line


def operate_3(segment, line_number):
    """
        nests tree by '*' or(and) '/' or(and) '%' operators
    """
    if not ['*', 'opr'] in segment and not ['/', 'opr'] in segment and not ['%', 'opr'] in segment:
        return segment
    else:
        operated_segment = segment

        for index in range(len(segment)):
            token = segment[index]

            if isinstance(token[0], str):
                if token[1] == 'opr':
                    if token[0] == '*' or token[0] == '/' or token[0] == '%':
                        left = operate_3(segment[:index], line_number)

                        if len(left) == 1 and isinstance(left[0], dict):
                            left = left[0]

                        right = operate_3(segment[index + 1:], line_number)

                        if len(right) == 1 and isinstance(right[0], dict):
                            right = right[0]

                        operated_segment = {
                            'left': left[0] if len(left) == 1 else left,
                            'operation': token,
                            'right': right[0] if len(right) == 1 else right
                        }
                        break
            else:
                segment[index] = operate_3(token, line_number)

        return operated_segment


nested = 0


def nest_vertical(block, line_number):
    new_block = []
    writing_inner_block = False
    block_nesting = 0
    inner_block = {}
    writing_else = False

    for index in range(len(block)):
        line = block[index]

        if not writing_inner_block:
            if not isinstance(line, dict):
                if ['while', 'kwd'] in line:
                    operation = line[0]
                    condition = line[1:]
                    inner_block = {
                        'left': condition,
                        'operation': operation,
                        'right': [],
                        'line': line_number
                    }

                    block_nesting += 1
                    writing_inner_block = True
                elif ['if', 'kwd'] in line:
                    operation = line[0]
                    condition = line[1:]
                    inner_block = {
                        'left': condition,
                        'operation': operation,
                        'right': [],
                        'else': [],
                        'line': line_number
                    }
                    block_nesting += 1
                    writing_inner_block = True
                else:
                    new_block.append(line)
            else:
                new_block.append(line)
        else:
            if not isinstance(line, dict):
                if ['if', 'kwd'] in line or \
                        ['while', 'kwd'] in line:
                    block_nesting += 1
                elif ['end', 'kwd'] in line:
                    block_nesting -= 1
                elif block_nesting == 1 and ['else', 'kwd'] in line:
                    writing_else = True
                    continue

                if block_nesting == 0:
                    writing_inner_block = False
                    writing_else = False
                    inner_block['right'] = nest_vertical(inner_block['right'], line_number)
                    new_block.append(inner_block)
                elif writing_else:
                    inner_block['else'].append(line)
                else:
                    inner_block['right'].append(line)
            else:
                inner_block['right'].append(line)

        line_number += 1
    return new_block


in_function_body = False


def make_tree(file_name):
    global in_function_body
    global nested
    global body_tree_element

    global tokens
    global line_numbers

    tokens, line_numbers = get_tokens(file_name)

    for index in range(len(tokens)):

        line = tokens[index]
        line_number = line_numbers[index]

        if in_function_body:
            if ['start', 'kwd'] in line:
                print('INVALID SYNTAX ERROR AT LINE', line_number, ': CAN NOT ASSIGN FUNCTION IN FUNCTION\'S BODY')
                break

            if ['if', 'kwd'] in line:
                nested += 1
            if ['while', 'kwd'] in line:
                nested += 1
            if ['end', 'kwd'] in line:
                nested -= 1

            fill_body(line, line_number)
            if len(body_tree_element) == 0:
                return
        else:
            if ['use', 'kwd'] in line:
                if valid_use_syntax(line):
                    tree.append({
                        'line': line_number,
                        'left': None,
                        'operation': 'use',
                        'right': line[1][0]
                    })
                else:
                    print('INVALID SYNTAX ERROR AT LINE', line_number, ': INVALID LIBRARY CALL')
                    break
            if ['start', 'kwd'] in line:
                if valid_start_syntax(line, line_number):
                    tree.append(function_tree_element)
                    nested += 1
                    body_tree_element = []
                    in_function_body = True
                else:
                    print('INVALID SYNTAX ERROR AT LINE', line_number, ': INVALID FUNCTION ASSIGN')
                    break

            if ['if', 'kwd'] in line or\
                    ['else', 'kwd'] in line or\
                    ['elif', 'kwd'] in line or\
                    ['loop', 'kwd'] in line or\
                    ['end', 'kdw'] in line:
                print('INVALID SYNTAX ERROR AT LINE', line_number, ': CAN NOT USE KEYWORD OUTSIDE OF FUNCTION\'S BODY')
                break

        if nested == 0 and in_function_body:
            in_function_body = False
            body_tree_element = nest_vertical(body_tree_element, tree[-1]['line'])
            if body_tree_element[-1] == [['end', 'kwd']]:
                body_tree_element = body_tree_element[:-1]
            tree[-1]['body'] = body_tree_element

    return tree


def print_tree(file_name):
    print("Produced tree:")

    pprint(make_tree(file_name),
           width=140)

    print("-" * 70)


if __name__ == "__main__":
    filename = input("Enter path to .min file you want to parse: ")
    print_tree(filename)
