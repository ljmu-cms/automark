# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Check a program against task requirements.

Implements the Automark interface for task 1 of the 4001COMP Java 
programming module in 2015 at LJMU.
"""

import re

from random import randint

import automark
from execcode import ExecCode
from comments import check_comment_quality
from indentation import check_indentation

__all__ = ('Automark')


class Automark(automark.Automark):
    """
    Check Java source against the task 1 requirements.
    """

    """
    OUTPUT_CHECKS represents the number of additional checks that are 
    performed by the marking process. These will be output individually 
    to the summary csv file.
    """
    OUTPUT_CHECKS = 2

    def __init__(self, filename, credentialsFile, build_dir):
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
        automark.Automark.__init__(self, filename, credentialsFile, build_dir)

    def setup_inputs(self):
        """
        Set up the inputs needed for marking the code.
        
        Generates random values to pass via stdin.
        """
        width = randint(1, 100)
        height = randint(1, 100)
        depth = randint(1, 100)
        stdin = "{}\n{}\n{}\n".format(width, height, depth)
        return [stdin, width, height, depth]

    # Prints output and gives result
    # True - Success; the output appears correct
    # False - Failure; the output looks incorrect
    def check_output_correctness(self, output, inputs):
        """
        Checks whether outputs generated conform to the task requirements.
        """
        width = inputs[1]
        height = inputs[2]
        depth = inputs[3]
        output_check = [False, False]
        output_score = 0
        output = re.sub("\n\s*\n*", "\n", output)
        lines = output.splitlines()
        volume = -1
        concat = ''
        execution_comments = ''

        correct_volume = (width * height * depth)
        correct_concat = '{:d}{:d}{:d}'.format(width, height, depth)
        volume_found = False
        concat_found = False
        for line in lines:
            if re.search(r'\d+', line) != None:
                volume = int(re.search(r'\d+', line).group())
                if (volume == correct_volume):
                    volume_found = True
            if re.search(r'\d+', line) != None:
                concat = re.search(r'\d+', line).group()
                if (concat == correct_concat):
                    concat_found = True

        if volume_found:
            output_score += 1
            output_check[0] = True
        else:
            execution_comments += (
                'Volume calculated incorrectly '
                '(should be {:d} for these inputs).\n').format(correct_volume)

        if concat_found:
            output_score += 1
            output_check[1] = True
        else:
            execution_comments += (
                'Number strings concatenated incorrectly '
                '(should be {} for these inputs).\n').format(correct_concat)

        return [output_score, execution_comments, output_check]

    def check_execute_result(self, result):
        """
        Assigns marks based on execution results.
        """
        output_score = 0
        if ExecCode.response_check_compiled(result):
            output_score += 2.5
        return output_score

    def check_indentation(self):
        """
        Assigns marks based on indentation quality.
        """
        result = check_indentation(self._program_structure, 1, 5)
        self._indentation_errors = result[0]
        indentation_score = result[1]
        self._error_list.extend(result[2])
        return indentation_score

    def check_comment_quality(self):
        """
        Assigns marks based on comment quality.
        """
        result = check_comment_quality(
            self._program_structure, 0.75, 0.75, 1.0, 3.0, 0.01)
        comment_score = result[0]
        self._comment_gap_average = result[1]
        self._comment_gap_sd = result[2]
        self._error_list.extend(result[3])
        return comment_score


