#!/usr/bin/env python 
"""
automark

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Check a program against task requirements

This script allows a program to be checked using the ideone api.
"""

def substring(line, tab, start):
	match = True
	if (len(tab) + start) <= len(line):
		for position in range(0, len(tab)):
			if line[start + position] != tab[position]:
				match = False
	else:
		match = False
	return match

def checkIndentationType(program, tab):
	programLines = program.splitlines()
	indentationErrors = 0
	tabsize = len(tab)
	indent = 0
	lineNum = 0
	firstError = 0
	for line in programLines:
		add = line.count('{') * tabsize
		sub = line.count('}') * tabsize
		tabs = 0
		#while line[tabs] == '\t':
		while substring(line, tab, tabs):
			tabs += tabsize
		indent -= sub
		if (indent != tabs) or ((len(line) > tabs) and (line[tabs] == ' ')):
			indentationErrors += 1
			if indentationErrors <= 1:
				firstError = lineNum
			indent = tabs
		indent += add
		lineNum += 1
	return [indentationErrors, firstError]

def checkIndentation(program, threshold):
	indentErrors = []
	indentErrors.append(checkIndentationType(program, '\t'))
	indentErrors.append(checkIndentationType(program, '  '))
	indentErrors.append(checkIndentationType(program, '   '))
	indentErrors.append(checkIndentationType(program, '    '))

	minError, minErrorIndex = min((val, idx) for (idx, val) in enumerate(indentErrors))
	indentationErrors = minError[0]

	errorList = []
	if indentationErrors > threshold:
		errorList.append([minError[1], 'Indentation error'])
		indentatinoScore = 0
	else:
		indentatinoScore = 1
	return [indentationErrors, indentatinoScore, errorList]

