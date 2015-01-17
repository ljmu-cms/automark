# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Test the quality of the variable names in a Java source file.

All variables declarations are found using the AST of the source file. 
Their quality is then checked using length and numerical increment checks. 
In other words, variables must be at least 3 characters long, and should 
not be of the form <name><int> (e.g. myVar1).
"""

from re import search
from plyjext.model import Visitor

__all__ = ('check_variable_name_quality')


def check_variable_name_quality(program, threshold):
    """
    Check the qualtiy of variable names.
    
    Checks whether variable names are too short, or appear to be enumerated 
    names (e.g. var1, var2, etc.).
    
    Args:
        program: The code to check.
        threshold: The threshold for the number of poor variables, after 
            which marks will be lost.
            
    Returns:
        List containing the mark obtained, the number of variables that were 
        too short, the number of variables that look enumerated, and a list 
        of errors to offer as feedback.
    """
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
					error_list.append(
					    [variable[1], 'Use variable names that represent '
					    'what they\'re being used for'])
			if search(r'\d+', name) != None:
				if int(search(r'\d+', name).group()) > 0:
					variable_enumeration += 1
					strike += 1
					if (strike == threshold):
						error_list.append(
						    [variable[1], 'Avoid using sequentially '
						    'numbered variables names'])
	variables_score = 1
	if strike >= threshold:
		variables_score = 0
	return [variables_score, variable_short, variable_enumeration, error_list]


# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class Variable_Visitor(Visitor):
    """
    Find names of variales declared in the AST.
    
    Visitor for checking the Java AST for any variable declarations. 
    If they exist, the name of the variable is recorded, along with the 
    line number it was declared on.
    """

	def __init__(self, verbose=False):
        """
        Initialise the Variable_Visitor class.
        
        Attributes:
        verbose: True if the results are to be output directly.
        """
		super(Variable_Visitor, self).__init__()
		self.variables = []

	def leave_VariableDeclaration(self, element):
        """
        Record the details of the variable declaration.
        """
		#msg = 'Variable type ({}); name ({}); line no ({})'
		#print msg.format(
		#   element.type, element.variable_declarators[0].variable.name, 
		#   element.variable_declarators[0].variable.lineno)
		self.variables.append(
		    [element.variable_declarators[0].variable.name, 
		    element.variable_declarators[0].variable.lineno])
		return True

