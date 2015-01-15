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

from SOAPpy import WSDL
import time
import re
import random
import execcode
import os
import collections
import indentation
import variables
import comments
import srctransform

class Automark:
    output_checks = 0

    def __init__(self, filename, credentialsFile, build_dir):
        # Read in the credentials from file
        with open(credentialsFile) as file:
            self.user = file.readline().rstrip('\n')
            self.password = file.readline().rstrip('\n')
            self.score = 0
            self.filename = filename
            self.classname = os.path.splitext(os.path.split(filename)[1])[0]

        # Load in the program file
        self.programStructure = srctransform.loadsource(filename)

        # Initialise the inputs
        self.stdin = ''
        self.executionComments = ''

        # Initialise the scoring state
        self.commentScore = 0
        self.variablesScore = 0
        self.indentationScore = 0
        self.executionScore = 0

        # Initialise the internal stats
        self.errorList = []
        self.inputs = []
        self.commentGapAverage = 0.0
        self.commentGapSD = 0.0
        self.variableShort = 0
        self.variableEnumeration = 0
        self.indentationErrors = 0
        self.executionTime = 0.0
        self.memoryUsed = 0
        self.executionResult = 0
        self.programOutput = ''
        self.outputCheck = []
        self.outputCheck.append(False)
        self.outputCheck.append(False)
        self.build_dir = build_dir
        self.extraProgramInput = []
        self.extraProgramOutput = []

        self.commentScore = self.check_comment_quality()
        self.variablesScore = self.check_variable_name_quality()
        self.indentationScore = self.check_indentation()
        self.executionScore = self.check_execution()
        
        print 'Final score: {:g}\n'.format(self.get_total_score())

    def get_full_program(self):
        return self.programStructure.fullProgram

    def get_total_score(self):
        totalScore = self.commentScore + self.variablesScore + self.indentationScore + self.executionScore
        return totalScore

    def get_comment_score(self):
        return self.commentScore
    
    def get_variables_score(self):
        return self.variablesScore
        
    def get_indentation_score(self):
        return self.indentationScore

    def get_execution_score(self):
        return self.executionScore

    def get_extra_program_inputs(self):
        return self.extraProgramInput

    def get_extra_program_outputs(self):
        return self.extraProgramOutput

    @staticmethod
    def get_scores_structure():
        return ['Execution', 'Indentation', 'Variables', 'Comments', 'Total']

    def getScores(self):
        # Execution score
        # Indentation
        # Variable names
        # Comments
        # Total
        scores = [self.executionScore, self.indentationScore, self.variablesScore, self.commentScore, self.get_total_score()]
        return scores

    @staticmethod
    def get_internal_stats_structure():
        return ['Gap average', 'Gap SD', 'Variables short', 'Variables enumerated', 'Indentation errors', 'Execution time', 'Memory used', 'Execution input', 'Execution result',  'Execution output']

    @classmethod
    def get_output_checks_structure(cls):
        structure = []
        count = 0
        for output in range(0, cls.output_checks):
            structure.append('Output check {:d}'.format(count))
            count += 1
        return structure

    def get_internal_stats(self):
        # Comment gap average
        # Comment gap SD
        # Variables short
        # Variables enumerated
        # Indentation errors
        # Execution time
        # Memory used
        # Execution input
        # Execution result
        # Execution output
        stats = [self.commentGapAverage, self.commentGapSD, self.variableShort, self.variableEnumeration, self.indentationErrors, self.executionTime, self.memoryUsed, self.stdin, self.executionResult, Automark.clean_text(self.programOutput)]
        return stats

    def get_output_checks(self):
        return self.outputCheck

    @staticmethod
    def get_error_status(response):
        error = 'OK'
        for item in response['item']:
            if item.key == 'error' and item.value != 'OK':
                error = item.value
        return error

    @staticmethod
    def get_value(response, key):
        value = ''
        for item in response['item']:
            if item.key == key:
                value = item.value
        return value

    @staticmethod
    def check_error_status(response):
        error = Automark.get_error_status(response)
        if error != 'OK':
            print 'Error: ' + error

    @staticmethod
    def check_submissions_status(status):
        if status < 0:
            print 'Waiting for compilation'
        elif status == 1:
            print 'Compiling'
        elif status == 3:
            print 'Running'
            
    def get_input(self):
        return self.stdin

    def get_output(self):
        return Automark.clean_text(self.programOutput)
        
    def get_execution_comments(self):
        return self.executionComments
        
    def get_error_list(self):
        return self.errorList

    @staticmethod
    def print_error_list(errorList):
        errorText = ''
        for error in errorList:
            errorText += str(error[0]) + ' : ' + error[1] + '\n'
        print errorText

    def setup_inputs(self):
        stdin = ""
        return [stdin]

    # coding: utf-8
    # from http://stackoverflow.com/questions/16469318/convert-raw-byte-string-to-unicode-without-knowing-the-codepage-beforehand/16469811#16469811
    @staticmethod
    def clean_text(s):
        if isinstance(s, unicode): return s.encode('ascii', 'replace')

        from locale import getpreferredencoding
        try:
            return unicode(s, getpreferredencoding()).encode('ascii', 'replace')
        except UnicodeDecodeError:
            pass
        return unicode(s, getpreferredencoding(), "replace").encode('ascii', 'replace')


    # Prints output and gives result
    # True - Success; the output appears correct
    # False - Failure; the output looks incorrect
    def check_output_correctness(self, output, inputs):
        outputCheck = []
        outputScore = 0
        output = re.sub("\n\s*\n*", "\n", output)
        lines = output.splitlines()
        executionComments = ''

        return [outputScore, executionComments, outputCheck]

    def check_execute_result(self, result):
        outputScore = 0
        if execcode.ExecCode.response_check_compiled(result):
            outputScore += 1
        return outputScore

    def check_comment_quality(self):
        result = comments.check_comment_quality(self.programStructure, 0.75, 0.75, 5.0, 2.0, 0.5)
        commentScore = result[0]
        self.commentGapAverage = result[1]
        self.commentGapSD = result[2]
        self.errorList.extend(result[3])
        return commentScore

    def check_variable_name_quality(self):
        result = variables.check_variable_name_quality(self.programStructure, 3)
        variablesScore = result[0]
        self.variableShort = result[1]
        self.variableEnumeration = result[2]
        self.errorList.extend(result[3])
        return variablesScore

    def check_indentation(self):
        result = indentation.check_indentation(self.programStructure, 3, 3)
        self.indentationErrors = result[0]
        indentationScore = result[1]
        self.errorList.extend(result[2])
        return indentationScore

    def check_execution(self):
        executionScore = 0
        #return executionScore
        # Creating wsdl client
        #wsdlObject = WSDL.Proxy('http://ideone.com/api/1/service.wsdl')
        wsdlObject = execcode.ExecCode(self.build_dir, self.classname)

        # Check the available languages
        #response = wsdlObject.getLanguages(self.user, self.password);
        #print response['item'][1].value['item']
        #    We don't need to check the languages every time
        #    Just use:
        #        {'value': 'Java (sun-jdk-1.7.0_25)', 'key': 10}
        #        {'value': 'C++11 (gcc-4.8.1)', 'key': 44}

        # Choose random input variables
        self.inputs = self.setup_inputs()
        self.stdin = self.inputs[0]

        error = 'OK'
        response = wsdlObject.createSubmission(self.user, self.password, self.programStructure.program, 10, self.stdin, True, True)
        error = Automark.get_error_status(response)
        if error != 'OK':
            print 'Error: ' + error
        else:
            link = Automark.get_value(response, 'link')

            # Periodically check the submission status
            status = -1;
            waitTime = 1
            while status != 0:
                time.sleep(waitTime)
                waitTime = 3
                response = wsdlObject.getSubmissionStatus(self.user, self.password, link)
                Automark.check_error_status(response)
                status = Automark.get_value(response, 'status')
                Automark.check_submissions_status (status)

            # Find out what happened to the program
            result = Automark.get_value(response, 'result')
            self.executionResult = result
            executionScore += self.check_execute_result(result)
            if result == 11:
                print 'Compilation error'
                response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, True)
                compInfo = Automark.get_value(response, 'cmpinfo')
                #print 'Compilation output: ' + compInfo
                self.programOutput = compInfo
                self.executionComments = 'Program failed to compile.'
            elif result == 12:
                print 'Runtime error'
                response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
                stdErrOutput = Automark.get_value(response, 'stderr')
                #print 'Runtime error: ' + stdErrOutput
                self.programOutput = stdErrOutput
                self.executionComments = 'Runtime error occurred during execution.'
            elif result == 13:
                print 'Time limit exceeded'
                response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, True, False, False)
                self.executionTime = Automark.get_value(response, 'time')
                output = Automark.get_value(response, 'output')
                self.programOutput = output
                result = self.check_output_correctness(output, self.inputs)
                executionScore += result[0]
                self.executionComments += result[1]
                self.outputCheck = result[2]
                if result[0] > 0:
                    executionScore -= 1
                self.executionComments = 'Execution failed to complete (time limit exceeded).'
            elif result == 17:
                print 'Memory limit exceeded'
                response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, False)
                self.memoryUsed = Automark.get_value(response, 'memory')
                print 'Memory used: {} bytes'.format(self.memoryUsed)
                self.executionComments = 'Execution failed to complete (ran out of memory).'
            elif result == 19:
                print 'Illegal system call'
                response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
                stdErrOutput = Automark.get_value(response, 'stderr')
                print 'Error output: ' + stdErrOutput
                self.programOutput = stdErrOutput
                self.executionComments = 'Execution failed to complete (illegal system call).'
            elif result == 15:
                response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, True, False, False)
                Automark.check_error_status(response)
                self.executionTime = Automark.get_value(response, 'time')
                self.memoryUsed = Automark.get_value(response, 'memory')
                date = Automark.get_value(response, 'date')
                output = Automark.get_value(response, 'output')
                self.programOutput = output
                result = self.check_output_correctness(output, self.inputs)
                executionScore += result[0]
                self.executionComments += result[1]
                self.outputCheck = result[2]
                if result[0] == 5:
                    self.executionComments += 'Your outputs correctly match the specification.\n'
            else:
                print 'Internal error with the code checking system'

        executionScore = round(min(5.0, max(0.0, executionScore)))

        return executionScore

