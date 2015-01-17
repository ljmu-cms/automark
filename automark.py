# vim: et:ts=4:textwidth=80

# Automark
#
# David Llewellyn-Jones
# Liverpool John Moores University
# 18/12/2014
# Released under the GPL v.3. See the LICENSE file for more details.

"""
Provide an interface used by BatchMark for defining automarking tasks.

Check a program against task requirements.

Tasks are created by inheriting Automark and overriding the __init__, 
setup_inputs, check_output_correctness, check_execute_result, 
check_indentation and check_comment_quality methods. The resulting
modules can then be registered in BatchMark for use by the batch marking
process.
"""

import os
import re

from time import sleep

from comments import check_comment_quality
from execcode import ExecCode
from variables import check_variable_name_quality
from indentation import check_indentation
from srctransform import load_source

from SOAPpy import WSDL

__all__ = ('Automark')


class Automark(object):
    """
    Check a program against task requirements.

    Tasks are created by inheriting Automark and overriding the __init__, 
    setup_inputs, check_output_correctness, check_execute_result, 
    check_indentation and check_comment_quality methods. The resulting
    modules can then be registered in BatchMark for use by the batch marking
    process.
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
        # Read in the credentials from file
        with open(credentials_file) as file:
            self._user = file.readline().rstrip('\n')
            self._password = file.readline().rstrip('\n')

        self._score = 0
        self._filename = filename
        self._classname = os.path.splitext(os.path.split(filename)[1])[0]

        # Load in the program file
        self._program_structure = load_source(filename)

        # Initialise the inputs
        self._stdin = ''
        self._execution_comments = ''

        # Initialise the scoring state
        self._comment_score = 0
        self._variables_score = 0
        self._indentation_score = 0
        self._execution_score = 0

        # Initialise the internal stats
        self._error_list = []
        self._inputs = []
        self._comment_gap_average = 0.0
        self._comment_gap_sd = 0.0
        self._variable_short = 0
        self._variable_enumeration = 0
        self._indentation_errors = 0
        self._execution_time = 0.0
        self._memory_used = 0
        self._execution_result = 0
        self._program_output = ''
        self._output_check = []
        self._output_check.append(False)
        self._output_check.append(False)
        self._build_dir = build_dir
        self._extra_program_input = []
        self._extra_program_output = []

        self._comment_score = self.check_comment_quality()
        self._variables_score = self.check_variable_name_quality()
        self._indentation_score = self.check_indentation()
        self._execution_score = self.check_execution()
        
        print 'Final score: {:g}\n'.format(self.get_total_score())

    def setup_inputs(self):
        """
        Set up the inputs needed for marking the code.
        
        The default implementation provides no input on stdin. This should 
        therefore be overriden for any more complex tasks that expect 
        input to be provided during execution.
        """
        stdin = ""
        return [stdin]

    def check_output_correctness(self, output, inputs):
        """
        Checks whether outputs generated conform to the task requirements.
        
        The default implementation doesn't perform any checks. This should 
        therefore be overriden for any more complex tasks that generate 
        output to be checked during marking.
        """
        output_check = []
        output_score = 0
        output = re.sub("\n\s*\n*", "\n", output)
        lines = output.splitlines()
        execution_comments = ''

        return [output_score, execution_comments, output_check]

    def check_execute_result(self, result):
        """
        Assigns marks based on execution results.
        
        The default implementation adds one mark if the code compiles 
        without errors. This should be overriden if a different mark
        or more complex process is needed.
        """
        output_score = 0
        if ExecCode.response_check_compiled(result):
            output_score += 1
        return output_score

    def check_comment_quality(self):
        """
        Assigns marks based on comment quality.
        
        The default implementation adds marks based on the following
        parameters:
            frequency_threshold = 0.75
            consistency_threshold = 0.75
            ave_offset = 5.0
            sd_offset = 2.0
            ave_weight= 0.5 
        If either parameters or a more complex process is needed, the
        method should be overriden.
        """
        result = check_comment_quality(
            self._program_structure, 0.75, 0.75, 5.0, 2.0, 0.5)
        comment_score = result[0]
        self._comment_gap_average = result[1]
        self._comment_gap_sd = result[2]
        self._error_list.extend(result[3])
        return comment_score

    def check_variable_name_quality(self):
        """
        Assigns marks based on variable quality.
        
        The default implementation adds one mark if no more than three
        badly named variables are found. This should be overriden if a 
        different mark or more complex process is needed.
        """
        result = check_variable_name_quality(
            self._program_structure, 3)
        variables_score = result[0]
        self._variable_short = result[1]
        self._variable_enumeration = result[2]
        self._error_list.extend(result[3])
        return variables_score

    def check_indentation(self):
        """
        Assigns marks based on indentation quality.
        
        The default implementation adds two marks if no more than three
        badly indented lines are found. This should be overriden if a 
        different mark or more complex process is needed.
        """
        result = check_indentation(self._program_structure, 3, 3)
        self._indentation_errors = result[0]
        indentation_score = result[1]
        self._error_list.extend(result[2])
        return indentation_score

    def get_full_program(self):
        """
        Return the full program source code, including blank lines.
        """
        return self._program_structure.full_program

    def get_total_score(self):
        """
        Return the total mark achieved by the code.
        """
        total_score = (self._comment_score + self._variables_score + 
            self._indentation_score + self._execution_score)
        return total_score

    def get_comment_score(self):
        """
        Return the mark for comment quality.
        """
        return self._comment_score
    
    def get_variables_score(self):
        """
        Return the mark for variable quality.
        """
        return self._variables_score
        
    def get_indentation_score(self):
        """
        Return the mark for indentation quality.
        """
        return self._indentation_score

    def get_execution_score(self):
        """
        Return the mark for execution correctness.
        """
        return self._execution_score

    def get_extra_program_inputs(self):
        """
        Return the extra program inputs that were needed, beyond stdin.
        
        These inputs might include data passed using a separate file.
        """
        return self._extra_program_input

    def get_extra_program_outputs(self):
        """
        Return the extra program oututs generted, beyond stdout.

        These outputs might include data generated into a separate file.
        """
        return self._extra_program_output

    @staticmethod
    def get_scores_structure():
        """
        Return titles for data returned by get_scores().
        """
        return ['Execution', 'Indentation', 'Variables', 'Comments', 'Total']

    def get_scores(self):
        """
        Return the marks list for the code.
        
        Use get_scores_structure() to establish what each item in the list
        represents.
        """
        # Execution score
        # Indentation
        # Variable names
        # Comments
        # Total
        scores = [self._execution_score, self._indentation_score, 
            self._variables_score, self._comment_score, self.get_total_score()]
        return scores

    @staticmethod
    def get_internal_stats_structure():
        """
        Return titles for data returned by get_internal_stats().
        """
        return ['Gap average', 'Gap SD', 'Variables short', 
            'Variables enumerated', 'Indentation errors', 'Execution time', 
            'Memory used', 'Execution input', 'Execution result',  
            'Execution output']

    @classmethod
    def get_output_checks_structure(cls):
        """
        Return titles for data returned by get_output_checks().
        """
        structure = []
        count = 0
        for output in range(0, cls.OUTPUT_CHECKS):
            structure.append('Output check {:d}'.format(count))
            count += 1
        return structure

    def get_internal_stats(self):
        """
        Return statistics from the various internal checks.
        
        Use get_internal_stats_structure() to establish what each item in 
        the list represents.
        """
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
        stats = [self._comment_gap_average, self._comment_gap_sd, 
            self._variable_short, self._variable_enumeration, 
            self._indentation_errors, self._execution_time, self._memory_used, 
            self._stdin, self._execution_result, 
            Automark.clean_text(self._program_output)]
        return stats

    def get_output_checks(self):
        """
        Return results of the various output checks.
        
        Use get_output_checks_structure() to establish what each item in 
        the list represents.
        """
        return self._output_check

    @staticmethod
    def get_error_status(response):
        """
        Check the internal error status of the marking process.
        
        Returns OK if everything is fine.
        """
        error = 'OK'
        for item in response['item']:
            if item.key == 'error' and item.value != 'OK':
                error = item.value
        return error

    @staticmethod
    def _get_value(response, key):
        """
        Extract value for given key in a list.
        
        Internal method, extracts the value associated with the given key 
        for the data returned, either from the local checks or the Sphere 
        Engine Web Service.
        """
        value = ''
        for item in response['item']:
            if item.key == key:
                value = item.value
        return value

    @staticmethod
    def check_error_status(response):
        """
        Prints out something sensible based on the error status.
        """
        error = Automark.get_error_status(response)
        if error != 'OK':
            print 'Error: ' + error

    @staticmethod
    def check_submissions_status(status):
        """
        Prints out something sensible based on current progress.
        """
        if status < 0:
            print 'Waiting for compilation'
        elif status == 1:
            print 'Compiling'
        elif status == 3:
            print 'Running'
            
    def get_input(self):
        """
        Return the stdin input used for the program.
        """
        return self._stdin

    def get_output(self):
        """
        Return the stdout output from the program.
        """
        return Automark.clean_text(self._program_output)
        
    def get_execution_comments(self):
        """
        Return human-readable comments generated by the marking process.
        """
        return self._execution_comments
        
    def get_error_list(self):
        """
        Return a list of errors generated from the marking process.
        """
        return self._error_list

    @staticmethod
    def print_error_list(error_list):
        """
        Print out a list of all the errors.
        
        This is really just a convenience method helpful for debugging.
        """
        error_text = ''
        for error in error_list:
            error_text += str(error[0]) + ' : ' + error[1] + '\n'
        print error_text

    # coding: utf-8
    # from http://stackoverflow.com/questions/16469318/convert-raw-byte-string-
    # to-unicode-without-knowing-the-codepage-beforehand/16469811#16469811
    @staticmethod
    def clean_text(s):
        """
        Replaces any unicode characters in a string.
        """
        if isinstance(s, unicode): return s.encode('ascii', 'replace')

        from locale import getpreferredencoding
        try:
            return unicode(s, getpreferredencoding()).encode(
                'ascii', 'replace')
        except UnicodeDecodeError:
            pass
        return unicode(s, getpreferredencoding(), "replace").encode(
            'ascii', 'replace')

    def check_execution(self):
        """
        Generate inputs, execute code, check outputs and assign marks.
        
        Perform the actual process of marking some code. The full process 
        involves generating any inputs, compiling and executing the code, 
        checking any outputs, then calculating a mark as a result.
        Other factors including checking indentation quality, variable 
        quality and comment quality are also performed.
        
        Although it can be, in general it's not expected that this method 
        should need to be overriden, since replicating the it requires 
        lots of work. Instead, the other methods (e.g. check_indentation(), 
        setup_inputs() etc.) should be overriden instead. This method 
        calls all of them to do the marking calculations.
        
        Returns the resulting mark from performing all of these operations.
        """
        execution_score = 0
        #return execution_score
        # Creating wsdl client
        #wsdl_object = WSDL.Proxy('http://ideone.com/api/1/service.wsdl')
        wsdl_object = ExecCode(self._build_dir, self._classname)

        # Check the available languages
        #response = wsdl_object.getLanguages(self._user, self._password);
        #print response['item'][1].value['item']
        #    We don't need to check the languages every time
        #    Just use:
        #        {'value': 'Java (sun-jdk-1.7.0_25)', 'key': 10}
        #        {'value': 'C++11 (gcc-4.8.1)', 'key': 44}

        # Choose random input variables
        self._inputs = self.setup_inputs()
        self._stdin = self._inputs[0]

        error = 'OK'
        response = wsdl_object.createSubmission(self._user, self._password, 
            self._program_structure.program, 10, self._stdin, True, True)
        error = Automark.get_error_status(response)
        if error != 'OK':
            print 'Error: ' + error
        else:
            link = Automark._get_value(response, 'link')

            # Periodically check the submission status
            status = -1;
            wait_time = 1
            while status != 0:
                sleep(wait_time)
                wait_time = 3
                response = wsdl_object.getSubmissionStatus(
                    self._user, self._password, link)
                Automark.check_error_status(response)
                status = Automark._get_value(response, 'status')
                Automark.check_submissions_status (status)

            # Find out what happened to the program
            result = Automark._get_value(response, 'result')
            self._execution_result = result
            execution_score += self.check_execute_result(result)
            if result == 11:
                print 'Compilation error'
                response = wsdl_object.getSubmissionDetails(
                    self._user, self._password, link, False, False, False, 
                    False, True)
                cmpinfo = Automark._get_value(response, 'cmpinfo')
                #print 'Compilation output: ' + cmpinfo
                self._program_output = cmpinfo
                self._execution_comments = 'Program failed to compile.'
            elif result == 12:
                print 'Runtime error'
                response = wsdl_object.getSubmissionDetails(
                    self._user, self._password, link, False, False, False, 
                    True, False)
                stderr_output = Automark._get_value(response, 'stderr')
                #print 'Runtime error: ' + stderr_output
                self._program_output = stderr_output
                self._execution_comments = \
                    'Runtime error occurred during execution.'
            elif result == 13:
                print 'Time limit exceeded'
                response = wsdl_object.getSubmissionDetails(
                    self._user, self._password, link, False, False, True, 
                    False, False)
                self._execution_time = Automark._get_value(response, 'time')
                output = Automark._get_value(response, 'output')
                self._program_output = output
                result = self.check_output_correctness(output, self._inputs)
                execution_score += result[0]
                self._execution_comments += result[1]
                self._output_check = result[2]
                if result[0] > 0:
                    execution_score -= 1
                self._execution_comments = \
                    'Execution failed to complete (time limit exceeded).'
            elif result == 17:
                print 'Memory limit exceeded'
                response = wsdl_object.getSubmissionDetails(
                    self._user, self._password, link, False, False, False, 
                    False, False)
                self._memory_used = Automark._get_value(response, 'memory')
                print 'Memory used: {} bytes'.format(self._memory_used)
                self._execution_comments = \
                    'Execution failed to complete (ran out of memory).'
            elif result == 19:
                print 'Illegal system call'
                response = wsdl_object.getSubmissionDetails(
                    self._user, self._password, link, False, False, False, 
                    True, False)
                stderr_output = Automark._get_value(response, 'stderr')
                print 'Error output: ' + stderr_output
                self._program_output = stderr_output
                self._execution_comments = \
                    'Execution failed to complete (illegal system call).'
            elif result == 15:
                response = wsdl_object.getSubmissionDetails(
                    self._user, self._password, link, False, False, True, 
                    False, False)
                Automark.check_error_status(response)
                self._execution_time = Automark._get_value(response, 'time')
                self._memory_used = Automark._get_value(response, 'memory')
                date = Automark._get_value(response, 'date')
                output = Automark._get_value(response, 'output')
                self._program_output = output
                result = self.check_output_correctness(output, self._inputs)
                execution_score += result[0]
                self._execution_comments += result[1]
                self._output_check = result[2]
                if result[0] == 5:
                    self._execution_comments += \
                        'Your outputs correctly match the specification.\n'
            else:
                print 'Internal error with the code checking system'

        execution_score = round(min(5.0, max(0.0, execution_score)))

        return execution_score

