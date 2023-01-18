# takes array of lines: ["line1", "line2" ...];
# delete tabs, eol, comments;
# returns array of 'cleared' lines : ["cleared line 1", "cleared line 2" ...] and line number for each line
def clear_lines(lines_raw):
	lines = []
	line_numbers = []

	# removing comments, tabs, eol symbols
	for index in range(len(lines_raw)):
		line = lines_raw[index]

		line = line.split('~')[0]

		if line == '':
			continue

		if line[-1] == '\n':
			line = line[:-1]

		if line == '':
			continue

		line = line.replace('\t', '')

		if line == '':
			continue

		line_numbers.append(index + 1)
		lines.append(line)

	return lines, line_numbers

# takes 'file_name' (WITH extension) of .shc file;
# separates lines on tokens, with types;
# returns array of dicts: [ [ ["token" , "type"] ... ] ... ] and line numbers to each line
def get_tokens(file_name):
	file = open(file_name, 'r')

	raw_lines = file.readlines()
	lines, line_numbers = clear_lines(raw_lines)

	tokens_raw = []  # separated, but no types

	for line in lines:
		line_of_tokens = []

		length = len(line)

		token = ""

		in_string = False
		skip_next = False

		for index in range(length):	
			# next 3 if's cares about special symbols (\', \\, \", \n) and how to add them, properly, cause
			# in string it doesn't recognize '\ + symbol' as special symbol, but as '\\ + \ + symbol'
			
			# we added special symbol in the previous iteration, so we must skip it
			if skip_next:
				skip_next = False
				continue

			# when we hit " it's time to count all text as string till we hit other ", however it MUSTN'T be an " in the text
			if line[index] == '"' and not line[index - 1] == '\\':
				in_string = not in_string
				# don't 'continue', because we need " to recognize token as string

			# when we are in string we don't care about any operators, spaces, but care about '\'
			if in_string and line[index] == '\\':
				if line[index + 1] == 'n':
					token += '\n'
				elif line[index + 1] == '\'':
					token += '\''
				elif line[index + 1] == '\"':
					token += '\"'
				elif line[index + 1] == '\\':
					token += '\\'

				skip_next = True
				continue  # we've already added token
			# till here

			# when we're not in string things are easier
			if line[index] in special_symbols and not in_string:
				# several special symbols in raw creates '' tokens
				if token != '': 
					line_of_tokens.append(token)

				token = ''
				if line[index] != ' ':
					line_of_tokens.append(line[index])  # we count operators as tokens as well, except spaces

					# for 2-symbol operators, like '++', '--', '>=', '<=' or '==' 
					if index + 1 < length:
						if line[index + 1] == '+' and line[index] == '+':
							line_of_tokens[-1] += '+'
							skip_next = True
						elif line[index + 1] == '-' and line[index] == '-':
							line_of_tokens[-1] += '-'
							skip_next = True
						elif line[index + 1] == '=':
							if line[index] in ['>', '<', '=']:
								line_of_tokens[-1] += '='
								skip_next = True
			else:
				token += line[index]

		# using previous method we don't recognize last token, so we add it manually
		if token != '':
			line_of_tokens.append(token)

		# extra cautiousness
		if not line_of_tokens == []:
			tokens_raw.append(line_of_tokens)

	tokens = recognize_tokens(tokens_raw)  # differentiate tokens

	return tokens, line_numbers


special_symbols = ['=', '|', ' ', '+', '-', '/', '*', '%', '(', ')', '>', '<', ',']  # when we 'hit' them, we add tokens

# takes array of lines represented as tokens;
# returns array of dicts: [ [ ["token" , "type"] ... ] ... ]
def recognize_tokens(tokens_raw):
	prev_token = ''

	tokens = []

	for line in tokens_raw:
		recognized_line = []

		for token in line:
			if recognize_keyword(token):
				recognized_line.append([token, 'kwd'])
			elif recognize_operator(token):
				if token == '|':
					recognized_line[-1][1] = 'fnc'
				recognized_line.append([token, 'opr'])
			elif recognize_separator(token):
				recognized_line.append([token, 'sep'])
			elif recognize_type(token):
				recognized_line.append([token, 'typ'])
			elif recognize_boolean(token):
				recognized_line.append([token, 'bln'])
			elif recognize_integer(token):
				recognized_line.append([token, 'int'])
			elif recognize_float(token):
				recognized_line.append([token, 'flt'])
			elif recognize_string(token):
				recognized_line.append([token, 'str'])
			else:
				if prev_token == 'start':
					recognized_line.append([token, 'fnc'])
				elif prev_token == 'use':
					recognized_line.append([token, 'lib'])
				else:
					recognized_line.append([token, 'var'])

			prev_token = token

		tokens.append(recognized_line)

	return tokens


keywords = ['start', 'end', 'use', 'return', 'break', 'while', 'if', 'else', 'elif']
operators = ['+', '-', '*', '/', '%', '(', ')', 'is', 'and', 'or', 'not', '>', '<', '<=', '>=', '==', '|', '=']
booleans = ['true', 'false']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
types = ['int', 'float', 'str', 'bool']

# takes token as string;
# returns True if token is a keyword, otherwise False
def recognize_keyword(token):
	return token in keywords

# takes token as string;
# returns True if token is an operator, otherwise False
def recognize_operator(token):
	return token in operators

# takes token as string;
# returns True if token is an operator, otherwise False
def recognize_type(token):
	return token in types

# takes token as string;
# returns True if token is a boolean, otherwise False
def recognize_boolean(token):
	return token in booleans

# takes token as string;
# returns True if token is an integer, otherwise False
def recognize_integer(token):
	if token[0] == '-':
		token = token[1:]

	for numeral in token:
		if numeral not in numbers:
			return False

	return True 

# takes token as string;
# returns True if token is a floating point number, otherwise False
def recognize_float(token):
	parts = token.split('.')
	
	# if string has NO point '.', it isn't a floating point number
	if len(parts) == 1: 
		return False

	return recognize_integer(parts[0]) and recognize_integer(parts[1])

# takes token as string;
# returns True if token is a string, otherwise False
def recognize_string(token):
	return token[0] == '"' and token[-1] == '"' 

def recognize_separator(token):
	return token == ','
