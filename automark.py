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

    def __init__(self, filename, credentials_file, build_dir):
        # Read in the credentials from file
        with open(credentials_file) as file:
            self.user = file.readline().rstrip('\n')
            self.password = file.readline().rstrip('\n')
            self.score = 0
            self.filename = filename
            self.classname = os.path.splitext(os.path.split(filename)[1])[0]

        # Load in the program file
        self.program_structure = srctransform.load_source(filename)

        # Initialise the inputs
        self.stdin = ''
        self.execution_comments = ''

        # Initialise the scoring state
        self.comment_score = 0
        self.variables_score = 0
        self.indentation_score = 0
        self.execution_score = 0

        # Initialise the internal stats
        self.error_list = []
        self.inputs = []
        self.comment_gap_average = 0.0
        self.comment_gap_sd = 0.0
        self.variable_short = 0
        self.variable_enumeration = 0
        self.indentation_errors = 0
        self.execution_time = 0.0
        self.memory_used = 0
        self.execution_result = 0
        self.program_output = ''
        self.output_check = []
        self.output_check.append(False)
        self.output_check.append(False)
        self.build_dir = build_dir
        self.extra_program_input = []
        self.extra_program_output = []

        self.comment_score = self.check_comment_quality()
        self.variables_score = self.check_variable_name_quality()
        self.indentation_score = self.check_indentation()
        self.execution_score = self.check_execution()
        
        print 'Final score: {:g}\n'.format(self.get_total_score())

    def get_full_program(self):
        return self.program_structure.full_program

    def get_total_score(self):
        total_score = self.comment_score + self.variables_score + self.indentation_score + self.execution_score
        return total_score

    def get_comment_score(self):
        return self.comment_score
    
    def get_variables_score(self):
        return self.variables_score
        
    def get_indentation_score(self):
        return self.indentation_score

    def get_execution_score(self):
        return self.execution_score

    def get_extra_program_inputs(self):
        return self.extra_program_input

    def get_extra_program_outputs(self):
        return self.extra_program_output

    @staticmethod
    def get_scores_structure():
        return ['Execution', 'Indentation', 'Variables', 'Comments', 'Total']

    def get_scores(self):
        # Execution score
        # Indentation
        # Variable names
        # Comments
        # Total
        scores = [self.execution_score, self.indentation_score, self.variables_score, self.comment_score, self.get_total_score()]
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
        stats = [self.comment_gap_average, self.comment_gap_sd, self.variable_short, self.variable_enumeration, self.indentation_errors, self.execution_time, self.memory_used, self.stdin, self.execution_result, Automark.clean_text(self.program_output)]
        return stats

    def get_output_checks(self):
        return self.output_check

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
        return Automark.clean_text(self.program_output)
        
    def get_execution_comments(self):
        return self.execution_comments
        
    def get_error_list(self):
        return self.error_list

    @staticmethod
    def print_error_list(error_list):
        error_text = ''
        for error in error_list:
            error_text += str(error[0]) + ' : ' + error[1] + '\n'
        print error_text

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
        output_check = []
        output_score = 0
        output = re.sub("\n\s*\n*", "\n", output)
        lines = output.splitlines()
        execution_comments = ''

        return [output_score, execution_comments, output_check]

    def check_execute_result(self, result):
        output_score = 0
        if execcode.ExecCode.response_check_compiled(result):
            output_score += 1
        return output_score

    def check_comment_quality(self):
        result = comments.check_comment_quality(self.program_structure, 0.75, 0.75, 5.0, 2.0, 0.5)
        comment_score = result[0]
        self.comment_gap_average = result[1]
        self.comment_gap_sd = result[2]
        self.error_list.extend(result[3])
        return comment_score

    def check_variable_name_quality(self):
        result = variables.check_variable_name_quality(self.program_structure, 3)
        variables_score = result[0]
        self.variable_short = result[1]
        self.variable_enumeration = result[2]
        self.error_list.extend(result[3])
        return variables_score

    def check_indentation(self):
        result = indentation.check_indentation(self.program_structure, 3, 3)
        self.indentation_errors = result[0]
        indentation_score = result[1]
        self.error_list.extend(result[2])
        return indentation_score

    def check_execution(self):
        execution_score = 0
        #return execution_score
        # Creating wsdl client
        #wsdl_object = WSDL.Proxy('http://ideone.com/api/1/service.wsdl')
        wsdl_object = execcode.ExecCode(self.build_dir, self.classname)

        # Check the available languages
        #response = wsdl_object.getLanguages(self.user, self.password);
        #print response['item'][1].value['item']
        #    We don't need to check the languages every time
        #    Just use:
        #        {'value': 'Java (sun-jdk-1.7.0_25)', 'key': 10}
        #        {'value': 'C++11 (gcc-4.8.1)', 'key': 44}

        # Choose random input variables
        self.inputs = self.setup_inputs()
        self.stdin = self.inputs[0]

        error = 'OK'
        response = wsdl_object.createSubmission(self.user, self.password, self.program_structure.program, 10, self.stdin, True, True)
        error = Automark.get_error_status(response)
        if error != 'OK':
            print 'Error: ' + error
        else:
            link = Automark.get_value(response, 'link')

            # Periodically check the submission status
            status = -1;
            wait_time = 1
            while status != 0:
                time.sleep(wait_time)
                wait_time = 3
                response = wsdl_object.getSubmissionStatus(self.user, self.password, link)
                Automark.check_error_status(response)
                status = Automark.get_value(response, 'status')
                Automark.check_submissions_status (status)

            # Find out what happened to the program
            result = Automark.get_value(response, 'result')
            self.execution_result = result
            execution_score += self.check_execute_result(result)
            if result == 11:
                print 'Compilation error'
                response = wsdl_object.getSubmissionDetails(self.user, self.password, link, False, False, False, False, True)
                cmpinfo = Automark.get_value(response, 'cmpinfo')
                #print 'Compilation output: ' + cmpinfo
                self.program_output = cmpinfo
                self.execution_comments = 'Program failed to compile.'
            elif result == 12:
                print 'Runtime error'
                response = wsdl_object.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
                stderr_output = Automark.get_value(response, 'stderr')
                #print 'Runtime error: ' + stderr_output
                self.program_output = stderr_output
                self.execution_comments = 'Runtime error occurred during execution.'
            elif result == 13:
                print 'Time limit exceeded'
                response = wsdl_object.getSubmissionDetails(self.user, self.password, link, False, False, True, False, False)
                self.execution_time = Automark.get_value(response, 'time')
                output = Automark.get_value(response, 'output')
                self.program_output = output
                result = self.check_output_correctness(output, self.inputs)
                execution_score += result[0]
                self.execution_comments += result[1]
                self.output_check = result[2]
                if result[0] > 0:
                    execution_score -= 1
                self.execution_comments = 'Execution failed to complete (time limit exceeded).'
            elif result == 17:
                print 'Memory limit exceeded'
                response = wsdl_object.getSubmissionDetails(self.user, self.password, link, False, False, False, False, False)
                self.memory_used = Automark.get_value(response, 'memory')
                print 'Memory used: {} bytes'.format(self.memory_used)
                self.execution_comments = 'Execution failed to complete (ran out of memory).'
            elif result == 19:
                print 'Illegal system call'
                response = wsdl_object.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
                stderr_output = Automark.get_value(response, 'stderr')
                print 'Error output: ' + stderr_output
                self.program_output = stderr_output
                self.execution_comments = 'Execution failed to complete (illegal system call).'
            elif result == 15:
                response = wsdl_object.getSubmissionDetails(self.user, self.password, link, False, False, True, False, False)
                Automark.check_error_status(response)
                self.execution_time = Automark.get_value(response, 'time')
                self.memory_used = Automark.get_value(response, 'memory')
                date = Automark.get_value(response, 'date')
                output = Automark.get_value(response, 'output')
                self.program_output = output
                result = self.check_output_correctness(output, self.inputs)
                execution_score += result[0]
                self.execution_comments += result[1]
                self.output_check = result[2]
                if result[0] == 5:
                    self.execution_comments += 'Your outputs correctly match the specification.\n'
            else:
                print 'Internal error with the code checking system'

        execution_score = round(min(5.0, max(0.0, execution_score)))

        return execution_score

