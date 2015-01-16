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

import automark
import random
import re
import plyjext.model as model
import os
import math
import comments
import indentation
import execcode

class Automark(automark.Automark):
    output_checks = 5

    def __init__(self, filename, credentials_file, build_dir):
        automark.Automark.__init__(self, filename, credentials_file, build_dir)

    def setup_inputs(self):
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
        ship_length = random.randint(20, 100)
        ship_width = random.randint(20, 100)
        ship_height= random.randint(20, 100)
        container_length = random.randint(3, 10)
        container_width = random.randint(3, 10)
        container_height = random.randint(3, 10)
        container_weight = random.randint(3, 20)
        ship_max_weight = (math.trunc ((
            ship_length * ship_width * ship_height) / (container_length * 
            container_width * container_height)) * container_weight) + 1

        if not os.path.exists(self._build_dir):
            os.makedirs(self._build_dir)

        input_contents = (
            '{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n').format(
            ship_length, ship_width, ship_height, container_length, 
            container_width, container_height, container_weight, 
            ship_max_weight)
        file_to_write = os.path.join(self._build_dir, "input.txt")
        with open(file_to_write, 'w') as input_file:
            input_file.write(input_contents)

        stdin = input_contents

        return [stdin, ship_length, ship_width, ship_height, container_length, 
            container_width, container_height, container_weight, 
            ship_max_weight]

    def check_output_correctness(self, output, inputs):
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

        output = re.sub("\n\s*\n*", "\n", output)
        lines = output.splitlines()
    
        ship_volume = ship_length * ship_height * ship_width
        container_volume = (
            container_length * container_height * container_width)
        container_max = math.trunc(ship_volume / container_volume)
        container_weight = container_max * container_weight
        legal = (container_weight <= ship_max_weight)

        execution_comments = ''

        ship_volume_found = False
        container_volume_found = False
        container_max_found = False
        container_weight_found = False
        for line in lines:
            if re.search(r'\d+', line) != None:
                number = int(re.search(r'\d+', line).group())
                if number == ship_volume:
                    ship_volume_found = True
                if number == container_volume:
                    container_volume_found = True
                if number == container_max:
                    container_max_found = True
                if number == container_weight:
                    container_weight_found = True

        # Check the last line
        legal_words = ['legal', 'under', 'less', 'below', 'safe', 'lighter']
        illegal_words = ['illegal', 'over', 'more', 'above', 'unsafe', 
            'heavier', 'greater', 'higher', 'too']

        found_legal = False
        legal_result = False

        if len(lines) > 0:
            line = lines[len(lines) - 1]
            found = self._find_keywords(line, legal_words)
            if len(lines) > 1:
                line = lines[len(lines) - 2]
                found |= self._find_keywords(line, legal_words)
            if found:
                legal_result = True
                found_legal = True

        if len(lines) > 0:
            line = lines[len(lines) - 1]
            found = self._find_keywords(line, illegal_words)
            if len(lines) > 1:
                line = lines[len(lines) - 2]
                found |= self._find_keywords(line, illegal_words)
            if found:
                legal_result = False
                found_legal = True

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
        output_score = 0
        if execcode.ExecCode.response_check_compiled(result):
            output_score += 1.7
        return output_score

    def check_indentation(self):
        result = indentation.check_indentation(self._program_structure, 1, 14)
        self._indentation_errors = result[0]
        indentation_score = result[1]
        self._error_list.extend(result[2])
        return indentation_score

    def check_comment_quality(self):
        result = comments.check_comment_quality(
            self._program_structure, 0.75, 0.75, 2.0, 6.0, 0.08)
        comment_score = result[0]
        self._comment_gap_average = result[1]
        self._comment_gap_sd = result[2]
        self._error_list.extend(result[3])
        return comment_score

    @staticmethod
    def _find_keywords(line, words):
        found = False
        for keyword in words:
            if re.search(re.escape(keyword), line) != None:
                found = True
        return found

# This doesn't confirm to PEP 8, but has been left to match 
# Java and the PLYJ API
class FileReader_Visitor(model.Visitor):
    def __init__(self, verbose=False):
        super(FileReader_Visitor, self).__init__()
        self.filename = []

    def leave_InstanceCreation(self, element):
        if element.type.name.value == 'FileReader':
            filename = [element.arguments[0].value, element.lineno]
            self.filename.append(filename)
        return True

