# takes array of lines: ["line1", "line2" ...];
# delete tabs, eol, comments;
# returns array of 'cleared' lines : ["clearedline1", "clearedline2" ...] and line number for each line
def clearLines(lines_raw):
	lines = []
	line_numbers = []

	# removing comments, tabs, eol symbols
	for index in range(len(lines_raw)):
		line  = lines_raw[index]

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
def getTokens(file_name):
	file = open(file_name, 'r')

	raw_lines = file.readlines()
	lines, line_numbers = clearLines(raw_lines)

	tokens_raw = [] # separated, but no types

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

			# when we hit " it's time to count all text as string till we hit other ", however it MUSTN'T be a " in the text 
			if line[index] == '"' and not line[index - 1] == '\\':
				in_string = not in_string
				# don't 'continue', cause we need " to recognize token as string

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
				continue # we've already added token
			# till here


			# when we're not in string things are easier
			if line[index] in special_symbols and not in_string:
				# several special symbols in raw creates '' tokens
				if token != '': 
					line_of_tokens.append(token)

				token = ''
				if line[index] != ' ':
					line_of_tokens.append(line[index]) # we count operators as tokens as well, except spaces

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


	tokens = recognizeTokens(tokens_raw) # differentiate tokens

	return tokens, line_numbers

special_symbols = ['=', '|', ' ', '+', '-', '/', '*', '%', '(', ')', '>', '<', ','] # when we 'hit' them, we add tokens

# takes array of lines represented as tokens;
# returns array of dicts: [ [ ["token" , "type"] ... ] ... ]
def recognizeTokens(tokens_raw):
	prev_token = ''

	tokens = []

	for line in tokens_raw:
		recognized_line = []

		for token in line:
			if recognizeKeyword(token):
				recognized_line.append([token, 'kwd'])
			elif recognizeOpeator(token):
				if token == '|':
					recognized_line[-1][1] = 'fnc'
				recognized_line.append([token, 'opr'])
			elif recognizeSeparator(token):
				recognized_line.append([token, 'sep'])
			elif recognizeType(token):
				recognized_line.append([token, 'typ'])
			elif recognizeBoolean(token):
				recognized_line.append([token, 'bln'])
			elif recognizeInteger(token):
				recognized_line.append([token, 'int'])
			elif recognizeFloat(token):
				recognized_line.append([token, 'flt'])
			elif recognizeString(token):
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
def recognizeKeyword(token):
	return token in keywords

# takes token as string;
# returns True if token is an operator, otherwise False
def recognizeOpeator(token):
	return token in operators

# takes token as string;
# returns True if token is an operator, otherwise False
def recognizeType(token):
	return token in types

# takes token as string;
# returns True if token is a boolean, otherwise False
def recognizeBoolean(token):
	return token in booleans

# takes token as string;
# returns True if token is an integer, otherwise False
def recognizeInteger(token):
	if token[0] == '-':
		token = token[1:]

	for numeral in token:
		if not numeral in numbers:
			return False

	return True 

# takes token as string;
# returns True if token is a floating point number, otherwise False
def recognizeFloat(token):
	parts = token.split('.')
	
	# if string has NO point '.', it isn't a floating point number
	if len(parts) == 1: 
		return False

	return recognizeInteger(parts[0]) and recognizeInteger(parts[1]) 

# takes token as string;
# returns True if token is a string, otherwise False
def recognizeString(token):
	return token[0] == '"' and token[-1] == '"' 

def recognizeSeparator(token):
	return token == ','