# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Check a program against task requirements.

Implements the Automark interface for task 4 of the 4001COMP Java 
programming module in 2015 at LJMU.
"""

import os
import re

from random import randint
from plyjext.model import Visitor

import automark
from execcode import ExecCode
from comments import check_comment_quality
from indentation import check_indentation

__all__ = ('Automark')


class Automark(automark.Automark):
    """
    Check Java source against the task 4 requirements.
    """

    """
    OUTPUT_CHECKS represents the number of additional checks that are 
    performed by the marking process. These will be output individually 
    to the summary csv file.
    """
    OUTPUT_CHECKS = 0

    def __init__(self, filename, credentials_file, build_dir):
        """
        Initialise the Automark class.
        
        Attributes:
            filename: The Java source file to mark.
            credentials_file: File containing username and password on 
                separate lines. The contents are ignored if the execution is 
                to be done locally. If using Sphere Engine, these should be 
                ideone credentials.
            build_dir: Temporary folder to store build and execution files.
        """
        automark.Automark.__init__(self, filename, credentials_file, build_dir)

    def setup_inputs(self):
        """
        Set up the inputs needed for marking the code.
        
        Generates random values to pass via the input.txt file and stdin.
        """
        # Find the username, password and account name

        # Establish the name of the account input/output file
        # Establish the name of the transaction input/output file

        # Create the value to be passed on stdin
        stdin = '\n'

        return [stdin]

    def check_output_correctness(self, output, inputs):
        """
        Checks whether outputs generated conform to the task requirements.
        """
        output_score = 0
        execution_comments = ''
        output_check = []

        return [output_score, execution_comments, output_check]

    def check_execute_result(self, result):
        """
        Assigns marks based on execution results.
        """
        output_score = 0
        if ExecCode.response_check_compiled(result):
            # The code compiled without errors
            output_score += 1.0
        return output_score

    def check_indentation(self):
        """
        Assigns marks based on indentation quality.
        """
        result = check_indentation(self._program_structure, 7, 23)
        self._indentation_errors = result[0]
        indentation_score = result[1]
        self._error_list.extend(result[2])
        return indentation_score

    def check_comment_quality(self):
        """
        Assigns marks based on comment quality.
        """
        result = check_comment_quality(
            self._program_structure, 0.75, 0.75, 1.0, 4.0, 0.06)
        comment_score = result[0]
        self._comment_gap_average = result[1]
        self._comment_gap_sd = result[2]
        self._error_list.extend(result[3])
        return comment_score

# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class InstanceCreationParam_Visitor(Visitor):
    """
    Find parameter passed when creating instances in the AST.
    
    Visitor for checking the Java AST for any class instantiations of the 
    class specified. If they exist, the requested parameter passed to the 
    initialiser are recorded, along with the line number it occured on.
    """

    def __init__(self, class_name, param_num=0, verbose=False):
        """
        Initialise the InstanceCreationParam_Visitor class.
        
        Attributes:
        class_name: Name of the class to check for.
        param_num: Index of the parameter to record (default 0).
        verbose: True if the results are to be output directly.
        """
        super(InstanceCreationParam_Visitor, self).__init__()
        self._class_name = class_name
        self._param_num = param_num
        self._params = []

    def leave_InstanceCreation(self, element):
        """
        Record the details for the class instantiation.
        """
        if element.type.name.value == self._class_name:
            # Store the relevant parameter and the line number the code 
            # occurs
            param = [element.arguments[self._param_num].value, element.lineno]
            self._params.append(param)
        return True
        
    def get_param_list(self):
        """
        Return the parameters found when checking the AST.
        """
        return self._params


