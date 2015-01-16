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
import comments
import indentation
import execcode

class Automark(automark.Automark):
    output_checks = 2

    def __init__(self, filename, credentialsFile, build_dir):
        automark.Automark.__init__(self, filename, credentialsFile, build_dir)

    def setup_inputs(self):
        width = random.randint(1, 100)
        height = random.randint(1, 100)
        depth = random.randint(1, 100)
        stdin = "{}\n{}\n{}\n".format(width, height, depth)
        return [stdin, width, height, depth]

    # Prints output and gives result
    # True - Success; the output appears correct
    # False - Failure; the output looks incorrect
    def check_output_correctness(self, output, inputs):
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
        output_score = 0
        if execcode.ExecCode.response_check_compiled(result):
            output_score += 2.5
        return output_score

    def check_indentation(self):
        result = indentation.check_indentation(self._program_structure, 1, 5)
        self._indentation_errors = result[0]
        indentation_score = result[1]
        self._error_list.extend(result[2])
        return indentation_score

    def check_comment_quality(self):
        result = comments.check_comment_quality(
            self._program_structure, 0.75, 0.75, 1.0, 3.0, 0.01)
        comment_score = result[0]
        self._comment_gap_average = result[1]
        self._comment_gap_sd = result[2]
        self._error_list.extend(result[3])
        return comment_score


