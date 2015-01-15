#!/usr/bin/env python
# vim: et:ts=4:textwidth=80
"""
automark

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Check a program against task requirements

This script allows a program to be checked using the ideone api.
"""

import re
import plyjext.parser as plyj
import os
import collections

Program = collections.namedtuple('Program', ['program', 'programLines', 'fullProgram', 'programTree', 'lineNumber', 'lineCharacterStart'])

def loadsource(filename):
	# Load in the program from file
	fullProgram = ''
	with open(filename) as file:
		fullProgram = file.read()

	program = ""
	lineNumber = []
	lineCharacterStart = []
	foundMain = True
	linesRead = 1
	linesAdded = 0
	characterPos = 0
	with open(filename) as file:
		for line in file.xreadlines():
			if not line.startswith('package '):
				if (not foundMain) and (line.find('public class') >= 0):
					line = re.sub(r'(class\s*).*?($|\s|{)', r'\1Main\2', line)
					foundMain = True
				line = re.sub(r'(import\s*)javax.swing.', r'\1uk.ac.ljmu.automark.', line)
				if not (line.isspace() or (len(line) == 0)):
					program += line
					lineNumber.append(linesRead)
					lineCharacterStart.append(characterPos)
					linesAdded += 1
					characterPos += len(line)
			linesRead += 1

	# Store a line-delimited version of the program 
	programLines = program.splitlines()
	
	# Store a AST version of the program
	parser = plyj.Parser()
	programTree = parser.parse_string(fullProgram)

	programStructure = Program(program, programLines, fullProgram, programTree, lineNumber, lineCharacterStart)

	return programStructure

