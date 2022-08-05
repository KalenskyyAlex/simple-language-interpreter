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

		for index in range(length):
			if line[index] == "\"":
				in_string = not in_string

			if line[index] in special_symbols and not in_string:
				line_of_tokens.append(token)
				token = ''
				if line[index] != ' ':
					line_of_tokens.append(line[index])
			else:
				token += line[index]

		if token != '':
			line_of_tokens.append(token)

		print(line_of_tokens)

special_symbols = ['=', '|', ' ', '+', '-', '/', '*', '%']



getTokens('../examples/hello-world-example.shc')


'''
	* * * * * *   awful lexer example   * * * * * * 
	* doesn't mind about commets, tabs, spaces etc*

def checkNum(s):
	if '-' in s:
		s = s[1:]

	has_coma = False
	for i in s:
		if not (i == '0' or i == '1' or i == '2' or i == '3' or i == '4' or i == '5' or i == '6' or i == '7' or i == '8' or i == '9'):
			if i == '.':
				if has_coma:
					return False
				else:
					has_coma = True
			else:
				return False

		return True

def checkString(s):
	return s[0] == "\"" and s[-1] == "\""

def checkBool(s):
	return s == "true" or s == "false"

file = open("test.gc", "r")

raw_lines_list = file.readlines()

lines_list = []

for line in raw_lines_list:
	line = line.replace('\n', '')
	line = line.replace('\t', '')

	if not line == '':
		lines_list.append(line)

all_lines = []

for line in lines_list:
	tokens = line.split()

	arr = []

	index = 0

	for token in tokens:
		if token == "/" or token == "*" or token == "+" or token == "-" or token == "=":
			arr.append({token : ["op", index]})
		elif checkNum(token):
			arr.append({token : ["num", index]})
		elif checkBool(token):
			arr.append({token : ["bool", index]})
		elif checkString(token):
			arr.append({token : ["str", index]})
		else: 
			arr.append({token : ["var", index]})

		index += 1
	all_lines.append(arr)

pprint(all_lines)
'''