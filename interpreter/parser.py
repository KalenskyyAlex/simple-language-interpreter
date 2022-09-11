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
	global body_tree_element

	if ['is', 'opr'] in line:
		if valid_is_syntax(line, line_number):
			body_tree_element.append(variable_tree_element)
		else:
			return
	else:
		line = nest(line, line_number)
		if line == None:
			body_tree_element = None
			return

		line = operate_1(line, line_number)

		line = operate_2_helper(line, line_number)

		line = operate_3_helper(line, line_number)
		
		body_tree_element.append({'line' : line_number, 'content' : line})


# returns True if line has nesting, otherwise False
def has_nesting(line):
	if ['(', 'opr'] in line or [')', 'opr'] in line:
		return True

	return False 

# nest given line recursively
def nest(line, line_number):
	#base case - no nesting
	if not has_nesting(line):
		return line
	else:
		nested_line = []
		nested = 0;
		nested_segment = [];
		for token in line:
			if token == ['(', 'opr']:
				nested += 1

				if nested == 1:
					continue

			if token == [')', 'opr']:
				nested -= 1

			if not nested == 0:
				nested_segment.append(token);

			if nested == 0:
				if len(nested_segment) == 0:
					nested_line.append(token)
				else:
					nested_segment = nest(nested_segment, line_number)
					nested_line.append(nested_segment)
					nested_segment = []

		if not nested == 0:
			print("INVALID SYNTAX ERROR AT LINE", line_number, ": INVALID NESTING")
			return None

		return nested_line

def operate_1(segment, line_number):
	if len(segment) == 1:
		return segment
	else:
		operated_segment = segment
		for index in range(len(segment)):
			token = segment[index]
			if type(token[0]) == type(str()):
				if token[1] == 'opr':
					if token[0] == '=':
						left = operate_1(segment[:index], line_number)
						right = operate_1(segment[index + 1:], line_number)
						operated_segment = {
							'left' : left,
							'operation' : token,
							'right' : right
						}
						break
			else:
				token = operate_1(token, line_number)

		return operated_segment
					
def operate_2_helper(line, line_number):
	if type(line) == type(dict()):
		line['left'] = operate_2(line['left'], line_number)
		line['right'] = operate_2(line['right'], line_number)
	else:
		line = operate_2(line, line_number)

	return line

def operate_2(segment, line_number):
	if len(segment) == 1:
		return segment
	else:
		operated_segment = segment 

		for index in range(len(segment)):
			token = segment[index]
			if type(token[0]) == type(str()):
				if token[1] == 'opr':
					if token[0] == '+' or token[0] == '-':
						left = operate_2(segment[:index], line_number)
						right = operate_2(segment[index + 1:], line_number)
						operated_segment = {
							'left' : left,
							'operation' : token,
							'right' : right
						}
						break
			else:
				token = operate_2(token, line_number)

		return operated_segment

def operate_3_helper(line, line_number):
	if type(line) == type(dict()):
		line['left'] = operate_3_helper(line['left'], line_number)
		line['right'] = operate_3_helper(line['right'], line_number)

		return line
	else:
		line = operate_3(line, line_number)
		return line

def operate_3(segment, line_number):
	if len(segment) == 1:
		return segment
	else:
		operated_segment = segment 

		for index in range(len(segment)):
			token = segment[index]
			if type(token[0]) == type(str()):
				if token[1] == 'opr':
					if token[0] == '*' or token[0] == '/':
						left = operate_3(segment[:index], line_number)
						right = operate_3(segment[index + 1:], line_number)
						operated_segment = {
							'left' : left,
							'operation' : token,
							'right' : right
						}
						break
			else:
				print(token)
				token = operate_3(token, line_number)

		return operated_segment

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
			if body_tree_element == None:
				return

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
			body_tree_element = body_tree_element [:-1]
			tree[-1]['body'] = body_tree_element


	pprint(tree)


make_tree()