from pprint import *


# returns array of lines represented as array of tokens.
def clearLines(lines_raw):
	lines = []

	# removing comments, tabs, eol symbols
	for line in lines_raw:
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

		lines.append(line)

	pprint(lines)

	return lines

def getTokens(file_name):
	file = open(file_name, 'r')

	raw_lines = file.readlines()
	lines = clearLines(raw_lines)

	tokens = []
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

			if line[index] == '"' and not line[index - 1] == '\\':
				in_string = not in_string
				continue

			# when we are in string we don't care about any operators, spaces, but care about '\'
			if in_string and line[index] == '\\':
				if line[index + 1] == 'n':
					token += '\n'
				elif line[index + 1] == '\'':
					token += '\''
				elif line[index + 1] == '\"':
					token += '\"'
				elif line[index + 1] == '\\':
					tokem += '\\'

				skip_next = True
				continue
			# till here


			# when we're not in string things are easier
			if line[index] in special_symbols and not in_string:
				line_of_tokens.append(token)
				token = ''
				if line[index] != ' ':
					line_of_tokens.append(line[index]) # we count operators as tokens as well, except spaces
			else:
				token += line[index]

		if token != '':
			line_of_tokens.append(token)

		print(line_of_tokens)

special_symbols = ['=', '|', ' ', '+', '-', '/', '*', '%'] #when we 'hit' them, we add tokens


# Test
getTokens('../examples/hello-world-example.shc')
