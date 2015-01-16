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

def check_variable_name_quality(program, threshold):
	find_vars = Variable_Visitor()
	if program.program_tree != None:
		program.program_tree.accept(find_vars)
	variable_short = 0
	variable_enumeration = 0
	
	error_list = []
	strike = 0
	name = ''
	for variable in find_vars.variables:
		name = variable[0]
		if len(name) > 0:
			if len(name) < 3:
				variable_short += 1
				strike += 1
				if (strike == threshold):
					error_list.append([variable[1], 'Use variable names that represent what they\'re being used for'])
			if re.search(r'\d+', name) != None:
				if int(re.search(r'\d+', name).group()) > 0:
					variable_enumeration += 1
					strike += 1
					if (strike == threshold):
						error_list.append([variable[1], 'Avoid using sequentially numbered variables names'])
	variables_score = 1
	if strike >= threshold:
		variables_score = 0
	return [variables_score, variable_short, variable_enumeration, error_list]

# This doesn't confirm to PEP 8, but has been left to match Java and the PLYJ API
class Variable_Visitor(model.Visitor):
	def __init__(self, verbose=False):
		super(Variable_Visitor, self).__init__()
		self.variables = []

	def leave_VariableDeclaration(self, element):
		#msg = 'Variable type ({}); name ({}); line no ({})'
		#print msg.format(element.type, element.variable_declarators[0].variable.name, element.variable_declarators[0].variable.lineno)
		self.variables.append([element.variable_declarators[0].variable.name, element.variable_declarators[0].variable.lineno])
		return True

