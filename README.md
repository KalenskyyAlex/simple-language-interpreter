# Simple Interpreter For Self-written Language (MINIMUM)

## Summary

Hi, my name is Alex my goal is to develop my own programming language interpreter. 
My goals are next:
- understand better how programming language work from inside
- write my own working example
- become an inspiration for others, who can freely view, modify and experiment with my
future interpreter

### Disclaimer: this interpreter and language were made only for educational purpose and can not be as good, fast and complex as today's high-hierarchical programming languages with dozens of features.  

## Short overview

Interpreter(and language therefore) supports:
- *variable definition*
	- basic types (integer, string, boolean, float)
- *simple mathematical operations*
- *functions*
	- arguments 
	- return
- *loops*
	- break
- *if/else statements*
- *Language has **NO** strict indentation and **NO** semicolons to sign end of
command. Language follows rule "One Line - One Command" instead* 

Not really much, there's where the name comes from - MINIMUM language

## Syntax

### Comments

```~ this is a one-line comment```

Note: only one-line comments allowed

### Importing

```use io ~ basic input/output library```

Note: libraries can be written either with MINIMUM or Python. Basic libraries like
'io' are written with Python

### Declaring variables

```
new_variable is int
another_variable is str
```

Note: language does not support declaring and assigning in the same line
### Assigning variables and Mathematical operations
```
var1 is int ~ declaring
var2 is int ~ declaring

var1 = 3
var2 = (var1 * (var1 - 2) / (var1 + 3)) % 2 + 1
```
Note: MINIMUM supports brackets '()', '+', '-', '*', '/' and '%' operators making all
basic mathematical operations possible

### Function declaration

```
~ no arguments
start new_function
	~ function body
end

~ function with 2 arguments
start add | num1 is int, num2 is int
	return num1 + num2 ~ function returns a value
end
```

Note: start keyword does not define type of function's return. 
By default, it is ```nothing``` value
Note: each .min file should have main function with 0 arguments:

```
start main
	~ doing stuff
end
```

### If/Else 

```
	b is bool
	b = true
	
	if b
		write | "I'm happy"
	else
		write | "I'm sad"
	end
```

### While loop
MINIMUM has only one type of loops - while loop

```
index is int
index = 0

while index < 10
	write | index ~ basic output function
	index = index + 1
end 
```

or

```
index is int
index = 0

while true
	write | index ~ basic output function
	index = index + 1
	if index == 10
		break ~ while loop can have 'break' statement
	end
end
```



### Short syntax overview can be found in SYNTAX.min

### More program examples can be found in /examples folder

# Thanks for reading!