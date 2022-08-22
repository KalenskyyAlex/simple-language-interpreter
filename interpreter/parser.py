from lexer import getTokens

# ON DEBUG
from pprint import *

tokens, line_numbers = getTokens('../SYNTAX.shc')

# ON DEBUG
# pprint(tokens)

tree = []

# takes line of tokens as array;
# returns True if syntax with 'use' is correct, otherwise False 
def valid_use_syntax(line):
	if len(line) == 2:
		if line[0][0] == 'use':
			if line[1][1] == "lib":
				return True

	return False

# takes line of tokens as array + line number;
# forms 'function' element of tree; 
# returns True if syntax with 'start' is correct, otherwise False + SYNTAX ERROR
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

		# check if we have arguments to fill 'args'
		if len(line) > 2:
			if line[2][0] == '|' and len(line) > 3:
				line = line[3:]

				split = []

				valid = True;

				for token in line:
					# argunents are separated by coma
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
					split = []
				else:
					valid = False

				return valid

		else:
			return True 

	return False

# takes line of tokens as array with line_number and adds it to body;
# forms body tree element
body_tree_element = None;
def fill_body(line, line_number):
	global body_tree_elementc

	if ['is', 'opr'] in line:
		if valid_is_syntax(line, line_number):
			body_tree_element.append(variable_tree_element)
		else:
			return
	else:
		pass



# default values of types;
default_value = {'bool' : False, 'int' : 0, 'str' : '', 'float' : 0.0}

# takes line of tokens as array;
# forms 'variable' element of tree;
# returns True if syntax with 'is' is correct, otherwise False + SYNTAX ERROR
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

nested = 0

in_function_body = False

def make_tree():
	global in_function_body
	global nested
	global body_tree_element

	for index in range(len(tokens)):


		line = tokens[index]
		line_number = line_numbers[index]

		

		if in_function_body:
			if ['start', 'kwd'] in line:
				print("INVALID SYNTAX ERROR AT LINE", line_number, ": CAN NOT ASSIGN FUNCTION IN FUNCTION'S BODY")
				break

			if ['if', 'kwd'] in line:
				nested += 1
			if ['loop', 'kwd'] in line:
				nested += 1
			if ['end', 'kwd'] in line:
				nested -= 1

			fill_body(line, line_number)
		else:
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
					nested += 1
					body_tree_element = []
					in_function_body = True
				else:
					print("INVALID SYNTAX ERROR AT LINE", line_number, ": INVALID FUNCTION ASSIGN")
					break

			if ['if', 'kwd'] in line or ['else', 'kwd'] in line or ['elif', 'kwd'] in line or ['loop', 'kwd'] in line or ['end', 'kdw'] in line:
				print("INVALID SYNTAX ERROR AT LINE", line_number, ": CAN NOT USE KEYWORD OUTSIDE OF FUNCTION'S BODY")
				break

		if nested == 0 and in_function_body:
			in_function_body = False
			tree[-1]['body'] = body_tree_element


	print(tree)


make_tree()