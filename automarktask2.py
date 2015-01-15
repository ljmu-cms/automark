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
    outputChecks = 5

    def __init__(self, filename, credentialsFile, build_dir):
        automark.Automark.__init__(self, filename, credentialsFile, build_dir)

    def setupInputs(self):
        # Establish the name of the input file
        findFileInput = FileReaderVisitor()
        if self.programStructure.programTree != None:
            self.programStructure.programTree.accept(findFileInput)

        # Replace the input file with "input.txt" so we can control it
        if len(findFileInput.filename) > 0:
            transformed = re.sub(r'(FileReader\s*\(\s*)(' + re.escape(findFileInput.filename[0][0]) + ')(\s*\))', r'\1"input.txt"\3', self.programStructure.program)
            self.programStructure = self.programStructure._replace(program = transformed)

        # Generate variables for the input file
        ship_length = random.randint(20, 100)
        ship_width = random.randint(20, 100)
        ship_height= random.randint(20, 100)
        container_length = random.randint(3, 10)
        container_width = random.randint(3, 10)
        container_height = random.randint(3, 10)
        container_weight = random.randint(3, 20)
        ship_max_weight = (math.trunc ((ship_length * ship_width * ship_height) / (container_length * container_width * container_height)) * container_weight) + 1

        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)

        inputContents = '{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n{:d}\n'.format(ship_length, ship_width, ship_height, container_length, container_width, container_height, container_weight, ship_max_weight)
        fileToWrite = os.path.join(self.build_dir, "input.txt")
        with open(fileToWrite, 'w') as inputFile:
            inputFile.write(inputContents)

        stdin = inputContents

        return [stdin, ship_length, ship_width, ship_height, container_length, container_width, container_height, container_weight, ship_max_weight]

    @staticmethod
    def find_keywords(line, words):
        found = False
        for keyword in words:
            if re.search(re.escape(keyword), line) != None:
                found = True
        return found

    def checkOutputCorrectness(self, output, inputs):
        ship_length = inputs[1]
        ship_width = inputs[2]
        ship_height= inputs[3]
        container_length = inputs[4]
        container_width = inputs[5]
        container_height = inputs[6]
        container_weight = inputs[7]
        ship_max_weight = inputs[8]

        outputCheck = [False, False, False, False, False]
        outputScore = 0

        output = re.sub("\n\s*\n*", "\n", output)
        lines = output.splitlines()
    
        ship_volume = ship_length * ship_height * ship_width
        container_volume = container_length * container_height * container_width
        container_max = math.trunc(ship_volume / container_volume)
        container_weight = container_max * container_weight
        legal = (container_weight <= ship_max_weight)

        executionComments = ''

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
        illegal_words = ['illegal', 'over', 'more', 'above', 'unsafe', 'heavier', 'greater', 'higher', 'too']

        found_legal = False
        legal_result = False

        if len(lines) > 0:
            line = lines[len(lines) - 1]
            found = self.find_keywords(line, legal_words)
            if len(lines) > 1:
                line = lines[len(lines) - 2]
                found |= self.find_keywords(line, legal_words)
            if found:
                legal_result = True
                found_legal = True

        if len(lines) > 0:
            line = lines[len(lines) - 1]
            found = self.find_keywords(line, illegal_words)
            if len(lines) > 1:
                line = lines[len(lines) - 2]
                found |= self.find_keywords(line, illegal_words)
            if found:
                legal_result = False
                found_legal = True

        if ship_volume_found:
            outputScore += 0.2
            outputCheck[0] = True
            executionComments += 'You correctly output the ship volume of {:d}.\n'.format(ship_volume)
        else:
            executionComments += 'You didn\'t output the correct ship volume of {:d}.\n'.format(ship_volume)

        if container_volume_found:
            outputScore += 0.7
            outputCheck[1] = True
            executionComments += 'You correctly output the container volume of {:d}.\n'.format(container_volume)
        else:
            executionComments += 'You didn\'t output the correct container volume of {:d}.\n'.format(container_volume)

        if container_max_found:
            outputScore += 1.9
            outputCheck[2] = True
            executionComments += 'You correctly output that the ship could hold {:d} containers.\n'.format(container_max)
        else:
            executionComments += 'You didn\'t output that the ship could hold {:d} containers.\n'.format(container_max)

        if container_weight_found:
            outputScore += 1.0
            outputCheck[3] = True
            executionComments += 'You correctly output {:d} as the total weight of the containers.\n'.format(container_weight)
        else:
            executionComments += 'You didn\'t output the total weight of the containers as {:d}.\n'.format(container_weight)

        if found_legal:
            if legal_result == legal:
                outputScore += 0.9
                outputCheck[4] = True
                if legal:
                    executionComments += 'You correctly determined that the ship was safe to sail.\n'
                else:
                    executionComments += 'You correctly determined that the ship wasn\'t safe to sail.\n'
            else:
                if legal:
                    executionComments += 'You incorrectly said the ship was unsafe to sail.\n'
                else:
                    executionComments += 'You incorrectly said the ship was safe to sail.\n'
        else:
            executionComments += 'You didn\'t output whether the ship was safe to sail.\n'

        return [outputScore, executionComments, outputCheck]

    def checkExecuteResult(self, result):
        outputScore = 0
        if execcode.ExecCode.responseCheckCompiled(result):
            outputScore += 1.7
        return outputScore

    def checkIndentation(self):
        result = indentation.checkIndentation(self.programStructure, 1, 14)
        self.indentationErrors = result[0]
        indentationScore = result[1]
        self.errorList.extend(result[2])
        return indentationScore

    def checkCommentQuality(self):
        result = comments.checkCommentQuality(self.programStructure, 0.75, 0.75, 2.0, 6.0, 0.08)
        commentScore = result[0]
        self.commentGapAverage = result[1]
        self.commentGapSD = result[2]
        self.errorList.extend(result[3])
        return commentScore


class FileReaderVisitor(model.Visitor):
    def __init__(self, verbose=False):
        super(FileReaderVisitor, self).__init__()
        self.filename = []

    def leave_InstanceCreation(self, element):
        if element.type.name.value == 'FileReader':
            filename = [element.arguments[0].value, element.lineno]
            self.filename.append(filename)
        return True

