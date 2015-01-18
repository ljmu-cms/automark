# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Check a program against task requirements.

Implements the Automark interface for task 2 of the 4001COMP Java 
programming module in 2015 at LJMU.
"""

import os
import re

from math import trunc
from random import randint
from plyjext.model import Visitor

import automark
from execcode import ExecCode
from comments import check_comment_quality
from indentation import check_indentation

__all__ = ('Automark')


class Automark(automark.Automark):
    """
    Check Java source against the task 2 requirements.
    """

    """
    OUTPUT_CHECKS represents the number of additional checks that are 
    performed by the marking process. These will be output individually 
    to the summary csv file.
    """
    OUTPUT_CHECKS = 5

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
        
        Generates random values to store in the input.txt file.
        """
        # Establish the name of the input file
        find_file_input = FileReader_Visitor()
        if self._program_structure.program_tree != None:
            self._program_structure.program_tree.accept(find_file_input)

        # Replace the input file with "input.txt" so we can control it
        if len(find_file_input.filename) > 0:
            transformed = re.sub(
                r'(FileReader\s*\(\s*)(' + re.escape(
                find_file_input.filename[0][0]) + 
                ')(\s*\))', r'\1"input.txt"\3', 
                self._program_structure.program)
            self._program_structure = self._program_structure._replace(
                program = transformed)

        # Generate variables for the input file
        ship_length = randint(20, 100)
        ship_width = randint(20, 100)
        ship_height= randint(20, 100)
        container_length = randint(3, 10)
        container_width = randint(3, 10)
        container_height = randint(3, 10)
        container_weight = randint(3, 20)
        # Calculate the weight based on the number of ccontainers that
        # can be stored in the hold. Note that this value is incorrect, 
        # since it basically assumes containers are maleable. However, 
        # it's the method everyone seemed to use, and was given the 
        # marks in practice, so we go with it
        ship_max_weight = (trunc ((
            ship_length * ship_width * ship_height) / (container_length * 
            container_width * container_height)) * container_weight) + 1

        # If the build folder doesn't exist, create it
        if not os.path.exists(self._build_dir):
            os.makedirs(self._build_dir)

        # Create the file with the input values
        input_contents = (
            '{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n').format(
            ship_length, ship_width, ship_height, container_length, 
            container_width, container_height, container_weight, 
            ship_max_weight)
        file_to_write = os.path.join(self._build_dir, "input.txt")
        with open(file_to_write, 'w') as input_file:
            input_file.write(input_contents)

        # Replicate the file on stdin. We shouldn't really do this, but 
        # it provides an extra check in case the implementation missed
        # that an external file should be used
        stdin = input_contents

        return [stdin, ship_length, ship_width, ship_height, container_length, 
            container_width, container_height, container_weight, 
            ship_max_weight]

    def check_output_correctness(self, output, inputs):
        """
        Checks whether outputs generated conform to the task requirements.
        """
        ship_length = inputs[1]
        ship_width = inputs[2]
        ship_height= inputs[3]
        container_length = inputs[4]
        container_width = inputs[5]
        container_height = inputs[6]
        container_weight = inputs[7]
        ship_max_weight = inputs[8]

        output_check = [False, False, False, False, False]
        output_score = 0

        # Remove any blank lines from the output
        output = re.sub("\n\s*\n*", "\n", output)
        lines = output.splitlines()
    
        # Calculate the correct values (at least 'correct' for the
        # the purposes of the task)
        ship_volume = ship_length * ship_height * ship_width
        container_volume = (
            container_length * container_height * container_width)
        container_max = trunc(ship_volume / container_volume)
        container_weight = container_max * container_weight
        legal = (container_weight <= ship_max_weight)

        execution_comments = ''

        # Search for the correct values in the output 
        ship_volume_found = False
        container_volume_found = False
        container_max_found = False
        container_weight_found = False
        for line in lines:
            # Find any number sequences in the outputs
            if re.search(r'\d+', line) != None:
                number = int(re.search(r'\d+', line).group())
                if number == ship_volume:
                    # The number matches the ship volume
                    ship_volume_found = True
                if number == container_volume:
                    # The number matches the container volume
                    container_volume_found = True
                if number == container_max:
                    # The number matches the number of containers
                    container_max_found = True
                if number == container_weight:
                    # The number matches the final weight of cargo
                    container_weight_found = True

        # Check the last line to establish whether the ship was determined
        # to be seaworthy or not
        legal_words = ['legal', 'under', 'less', 'below', 'safe', 'lighter']
        illegal_words = ['illegal', 'over', 'more', 'above', 'unsafe', 
            'heavier', 'greater', 'higher', 'too']

        found_legal = False
        legal_result = False

        # Check for words indicating that the ship was deemed seaworthy
        if len(lines) > 0:
            line = lines[len(lines) - 1]
            found = self._find_keywords(line, legal_words)
            if len(lines) > 1:
                line = lines[len(lines) - 2]
                found |= self._find_keywords(line, legal_words)
            if found:
                legal_result = True
                found_legal = True

        # Check for words indicating the ship was deemed to be too heavy
        if len(lines) > 0:
            line = lines[len(lines) - 1]
            found = self._find_keywords(line, illegal_words)
            if len(lines) > 1:
                line = lines[len(lines) - 2]
                found |= self._find_keywords(line, illegal_words)
            if found:
                legal_result = False
                found_legal = True

        # Generate feedback and accumulate marks depending on which values 
        # were found in the output
        if ship_volume_found:
            output_score += 0.2
            output_check[0] = True
            execution_comments += (
                'You correctly output the ship volume of {:d}.\n').format(
                ship_volume)
        else:
            execution_comments += ("You didn't output the correct ship "
                "volume of {:d}.\n").format(ship_volume)

        if container_volume_found:
            output_score += 0.7
            output_check[1] = True
            execution_comments += ('You correctly output the container '
                'volume of {:d}.\n').format(container_volume)
        else:
            execution_comments += ("You didn't output the correct container "
                "volume of {:d}.\n").format(container_volume)

        if container_max_found:
            output_score += 1.9
            output_check[2] = True
            execution_comments += ('You correctly output that the ship '
                'could hold {:d} containers.\n').format(container_max)
        else:
            execution_comments += ("You didn't output that the ship could "
                "hold {:d} containers.\n").format(container_max)

        if container_weight_found:
            output_score += 1.0
            output_check[3] = True
            execution_comments += ('You correctly output {:d} as the total '
                'weight of the containers.\n').format(container_weight)
        else:
            execution_comments += ("You didn't output the total weight of "
                "the containers as {:d}.\n").format(container_weight)

        if found_legal:
            if legal_result == legal:
                output_score += 0.9
                output_check[4] = True
                if legal:
                    execution_comments += ('You correctly determined that the '
                        'ship was safe to sail.\n')
                else:
                    execution_comments += ("You correctly determined that the "
                        "ship wasn't safe to sail.\n")
            else:
                if legal:
                    execution_comments += ('You incorrectly said the ship was '
                        'unsafe to sail.\n')
                else:
                    execution_comments += ('You incorrectly said the ship was '
                        'safe to sail.\n')
        else:
            execution_comments += ("You didn't output whether the ship was "
                "safe to sail.\n")

        return [output_score, execution_comments, output_check]

    def check_execute_result(self, result):
        """
        Assigns marks based on execution results.
        """
        output_score = 0
        if ExecCode.response_check_compiled(result):
            # The code compiled without errors
            output_score += 1.7
        return output_score

    def check_indentation(self):
        """
        Assigns marks based on indentation quality.
        """
        result = check_indentation(self._program_structure, 1, 14)
        self._indentation_errors = result[0]
        indentation_score = result[1]
        self._error_list.extend(result[2])
        return indentation_score

    def check_comment_quality(self):
        """
        Assigns marks based on comment quality.
        """
        result = check_comment_quality(
            self._program_structure, 0.75, 0.75, 2.0, 6.0, 0.08)
        comment_score = result[0]
        self._comment_gap_average = result[1]
        self._comment_gap_sd = result[2]
        self._error_list.extend(result[3])
        return comment_score

    @staticmethod
    def _find_keywords(line, words):
        """
        Search a line for any of the keywords in a list.
        
        Return True if any of the keywords are there, False otherwise.
        """
        # Cycle through every keyword and check whether each occurs
        found = False
        for keyword in words:
            if re.search(re.escape(keyword), line) != None:
                found = True
        return found


# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class FileReader_Visitor(Visitor):
    """
    Find filenames passed to FileReader in the AST.
    
    Visitor for checking the Java AST for any instantiations of the 
    FileReader class. If they exist, the filename passed to the 
    initialiser is recorded, along with the line number it occured on.
    """
    
    def __init__(self, verbose=False):
        """
        Initialise the FileReader_Visitor class.
        
        Attributes:
        verbose: True if the results are to be output directly.
        """
        super(FileReader_Visitor, self).__init__()
        self.filename = []

    def leave_InstanceCreation(self, element):
        """
        Record the details of the FileReader instantiation.
        """
        if element.type.name.value == 'FileReader':
            # Store the first parameter (filename) and the line number
            # the code occurs
            filename = [element.arguments[0].value, element.lineno]
            self.filename.append(filename)
        return True

