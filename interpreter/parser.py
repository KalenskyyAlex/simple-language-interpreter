from lexer import getTokens

# ON DEBUG
from pprint import *

tokens, line_numbers = getTokens('../SYNTAX.shc')

# ON DEBUG
# pprint(tokens)

tree = []

def valid_use_syntax(line):
	if len(line) == 2:
		if line[0][0] == 'use':
			if line[1][1] == "lib":
				return True

	return False

function_tree_element = None
def valid_start_syntax(line, line_number):
	global function_tree_element

	function_tree_element = {}

	if line[0][0] == "start" and line[1][1] == "fnc":
		name = line[1][0]

		function_tree_element['line'] = line_number 
		function_tree_element['name'] = name
		function_tree_element['args'] = []
		function_tree_element['vars'] = []
		function_tree_element['body'] = []

		if len(line) > 2:
			if line[2][0] == '|' and len(line) > 3:
				line = line[3:]

				split = []

				valid = True;

				for token in line:
					if token[1] == 'sep': 
						if valid_is_syntax(split, line_number):
							function_tree_element['args'].append(variable_tree_element)
							split = []
						else:
							valid = False
							break;
					else:
						split.append(token)

				if valid_is_syntax(split, line_number):
					function_tree_element['args'].append(variable_tree_element)
					split = []

				return valid

		else:
			return True 


	return False


default_value = {'bool' : False, 'int' : 0, 'str' : '""', 'float' : 0.0}

variable_tree_element = None
def valid_is_syntax(block, line_number):
	global variable_tree_element

	variable_tree_element = {}

	if len(block) == 3:
		if block[1][0] == "is":
			if block[0][1] == "var":
				if block[2][1] == "typ":
					type = block[2][0]
					name = block[0][0]
					value = default_value[type]

					variable_tree_element['line'] = line_number
					variable_tree_element['name'] = name
					variable_tree_element['type'] = type
					variable_tree_element['value'] = value

					return True


	print("INVALID SYNTAX ERROR AT LINE", line_number, ": INVALID VARIABLE ASSIGN")
	return False	

for index in range(len(tokens)):
	line = tokens[index]
	line_number = line_numbers[index]

	if ['use', 'kwd'] in line:
		if valid_use_syntax(line):
			tree.append({
				"line" : line_number,
				"operation" : "use",
				"lib": line[1][0]
				})
		else:
			print("INVALID SYNTAX ERROR AT LINE", line_number, ": INVALID LIBRARY CALL")
			break

	if ['start', 'kwd'] in line:
		if valid_start_syntax(line, line_number):
			tree.append(function_tree_element)
		else:
			print("INVALID SYNTAX ERROR AT LINE", line_number, ": INVALID FUNCTION ASSIGN")
			break
			


print(tree)