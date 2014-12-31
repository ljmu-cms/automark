#!/usr/bin/env python 
"""
automark

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Check a program against task requirements

This script allows a program to be checked using the ideone api.
"""
import plyjext.model as model
import re

def checkVariableNameQuality(program, threshold):
	findVars = VariableVisitor()
	program.programTree.accept(findVars)
	variableShort = 0
	variableEnumeration = 0
	
	errorList = []
	strike = 0
	name = ''
	for variable in findVars.variables:
		name = variable[0]
		if len(name) > 0:
			if len(name) < 3:
				variableShort += 1
				strike += 1
				if (strike == threshold):
					errorList.append([variable[1], 'Use variable names that represent what they\'re being used for'])
			if re.search(r'\d+', name) != None:
				if int(re.search(r'\d+', name).group()) > 0:
					variableEnumeration += 1
					strike += 1
					if (strike == threshold):
						errorList.append([variable[1], 'Avoid using sequentially numbered variables names'])
	variablesScore = 1
	if strike >= threshold:
		variablesScore = 0
	return [variablesScore, variableShort, variableEnumeration, errorList]

class VariableVisitor(model.Visitor):
	def __init__(self, verbose=False):
		super(VariableVisitor, self).__init__()
		self.variables = []

	def leave_VariableDeclaration(self, element):
		#msg = 'Variable type ({}); name ({}); line no ({})'
		#print msg.format(element.type, element.variable_declarators[0].variable.name, element.variable_declarators[0].variable.lineno)
		self.variables.append([element.variable_declarators[0].variable.name, element.variable_declarators[0].variable.lineno])
		return True

