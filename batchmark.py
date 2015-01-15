#!/usr/bin/env python 
# vim: et:ts=4:textwidth=80
"""
automark

David Llewellyn-Jones, Posco Tso
Liverpool John Moores University
18/12/2014
Check programs against task requirements

This script allows multiple programs to be checked using the ideone api.
"""

from docx import Document
import xlrd
import os
import subprocess
import argparse
import automark
import automarktask1
import automarktask2
import automarktask3
import time
from zipfile import ZipFile

# Task number
# Folder containing students' folders
# Marker's initials (optional)
# Temp build folder (optional)
# Feedback template (optional)
# Student details list (optional)
# Summary output (optional)

class BatchMark:
    def __init__(self, task, marking_dir, marker_name, build_dir, feedback_doc_name, marking_sheet_name, summary_out):
        print ('Task: ' + str(task))
        print ("Folder to check in: " + marking_dir)
        print ('Marker name: ' + marker_name)
        print ("Build output folder: " + build_dir)
        print ("Feedback template: " + feedback_doc_name)
        print ("Marking sheet: " + marking_sheet_name)
        print ("Summary output: " + summary_out)

        self._task = task
        self._marking_dir = marking_dir
        self._marker_name = marker_name
        self._buid_dir = build_dir
        self._feedback_doc_name = feedback_doc_name
        self._marking_sheet_name = marking_sheet_name
        self._summary_out = summary_out

        # Select the appropriate task
        tasks = [automark, automarktask1, automarktask2, automarktask3]
        if (self._task < len(tasks)) and (self._task >= 0):
            self._taskSpecific = tasks[self._task]
        else:
            self._taskSpecific = tasks[0]
            print 'Task number out of bounds. Applying general checks.'

        #load student feedback form as a template
        self._feedback_document = Document(feedback_doc_name)
        #load my marking sheet 'PT' from workbook
        self._marking_sheet = xlrd.open_workbook(marking_sheet_name).sheet_by_name(marker_name)

    #do things
    def go(self):
        #username to firstname lastname map/dictionary
        self._name_map = {}
        self._construct_name_map()
        with open(self._summary_out, 'w') as self._summary:
            self._output_csv_co(['Username', 'Name'])
            self._output_csv_co(self._taskSpecific.Automark.getScoresStructure())
            self._output_csv_co(self._taskSpecific.Automark.getInternalStatsStructure())
            self._output_csv_nl(self._taskSpecific.Automark.getOutputChecksStructure())
            self._create_new_feedback_document()

    #probably won't work for Windows
    def _unzip_submission(self, student_dir):
        #form unzip command
        #cmd = ['unzip', '-q', '-o', '-d', student_dir + '/', student_dir + '/*.zip']
        #sys_process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #std_out = sys_process.communicate()
        archive_file = ''
        for check_dir, _, file in os.walk(student_dir):
            if '__MACOSX' not in check_dir.split('/'):
                for file_name in file:
                    if file_name.endswith('.zip'):
                        archive_file = os.path.join(check_dir, file_name)
        if archive_file != '':
            with ZipFile(archive_file ,'r') as archive:
                archive.extractall(student_dir)
                archive.close()
        else:
            print ('No zip archive')

    def _output_csv(self, items):
        count = 0
        for item in items:
            self._summary.write('\"')
            self._summary.write(str(item))
            self._summary.write('\"')
            if count < (len(items) - 1):
                self._summary.write(', ')
            count += 1

    def _output_csv_co(self, items):
        self._output_csv(items)
        self._summary.write(', ')

    def _output_csv_nl(self, items):
        self._output_csv(items)
        self._summary.write('\n')

    def _mark (self, directory):
        java_file = ''
        for check_dir, _, file in os.walk(directory):
            if '__MACOSX' not in check_dir.split('/'):
                for file_name in file:
                    if file_name.endswith('.java'):
                        java_file = os.path.join(check_dir, file_name)
        return java_file

    def _create_new_feedback_document(self):
        print
        #marker_directory = os.path.dirname(os.path.realpath(__file__))+'/'+self._marker_name
        for student_dir, _, file in os.walk(self._marking_dir):
            student_dir_name = os.path.relpath(student_dir, self._marking_dir)

            #print student_dir
            if (student_dir_name is not '.') and (student_dir_name in self._name_map):
                print 'Student: {}'.format(student_dir_name)
                student_name = self._name_map[student_dir_name][0] + ' ' + self._name_map[student_dir_name][1]
                self._unzip_submission(student_dir)
                java_path = self._mark(student_dir)
                if java_path == '':
                    print 'No java file'
                    self._write_student_name_to_document(student_dir, student_dir_name, student_name)
                else:
                    #print 'file: {}'.format(java_path)
                    marks = self._taskSpecific.Automark(java_path, 'credentials.txt', self._buid_dir)
                    self._write_details_to_document(student_dir, student_dir_name, student_name, marks)
                    self._write_comments_to_document(student_dir, student_dir_name, marks)
                    self._output_csv_co([student_dir_name, student_name])
                    self._output_csv_co(marks.getScores())
                    self._output_csv_co(marks.getInternalStats())
                    self._output_csv_nl(marks.getOutputChecks())

                #just do something extra
                #self._unzip_submission(student_dir)

    def _write_details_to_document(self, student_dir, student_dir_name, student_name, marks):
        #default cell for student's firstname lastname
        filename = self._feedback_doc_name.replace('username', student_dir_name)
        self._feedback_document.paragraphs[0].text = self._feedback_document.paragraphs[0].text.replace('<task>', str(self._task))
        self._feedback_document.tables[0].cell(1,0).text = student_name
        self._feedback_document.tables[0].cell(1,1).text = student_dir_name
        #self._feedback_document.tables[0].cell(1,2).text = self._marker_name
        self._feedback_document.tables[0].cell(1,2).text = 'auto'
        #print student_dir+'/'+filename
        # Clear tables
        for row in range(1,16):
            self._feedback_document.tables[2].cell(row, 2).text = ''
    
        executionScore = marks.getExecutionScore()
        indentationScore = marks.getIndentationScore()
        variablesScore = marks.getVariablesScore()
        commentScore = marks.getCommentScore()
        totalScore = marks.getTotalScore()
        efficientScore = 0
        if executionScore > 4:
            efficientScore = 1
            executionScore -= 1
        self._feedback_document.tables[2].cell((2 + int(executionScore)), 2).text = '{:g}'.format(executionScore)
        self._feedback_document.tables[2].cell(9, 2).text = str(indentationScore)
        self._feedback_document.tables[2].cell(10, 2).text = str(variablesScore)
        self._feedback_document.tables[2].cell(11, 2).text = str(efficientScore)
        self._feedback_document.tables[2].cell(13 + int(commentScore), 2).text = str(commentScore)


        self._feedback_document.tables[2].cell(16, 2).text = '{:g}'.format(totalScore)
        self._feedback_document.save(student_dir+'/../'+filename)

    def _write_student_name_to_document(self, student_dir, student_dir_name, student_name):
        #default cell for student's firstname lastname
        filename = self._feedback_doc_name.replace('username', student_dir_name)
        self._feedback_document.tables[0].cell(1,0).text = student_name
        self._feedback_document.tables[0].cell(1,1).text = student_dir_name
        self._feedback_document.tables[0].cell(1,2).text = self._marker_name
        self._feedback_document.save(student_dir+'/../'+filename)
        #print student_dir+'/'+filename

    def _write_comments_to_document(self, student_dir, student_dir_name, marks):
        filename = os.path.basename(self._feedback_doc_name).replace('username', student_dir_name)

        feedback_document = Document(student_dir+'/../'+filename)
        feedback_document.add_heading('Program Comments', 2)

        feedback_document.add_heading('Program input', 3)
        inputs = marks.getInput().splitlines()

        for line in inputs:
            feedback_document.add_paragraph(line, style='CodeChunk')

        extraProgramInputs = marks.getExtraProgrammInputs()
        for extra in extraProgramInputs:
            feedback_document.add_heading(extra[0], 3)
            extraLines = extra[1].splitlines()
            for line in extraLines:
                feedback_document.add_paragraph(line, style='CodeChunk')
    
        feedback_document.add_heading('Program output', 3)

        output = marks.getOutput().splitlines()
        for line in output:
            feedback_document.add_paragraph(line, style='CodeChunk')

        extraProgramOutputs = marks.getExtraProgrammOutputs()
        for extra in extraProgramOutputs:
            feedback_document.add_heading(extra[0], 3)
            extraLines = extra[1].splitlines()
            for line in extraLines:
                feedback_document.add_paragraph(line, style='CodeChunk')

        feedback_document.add_heading('Execution comments', 3)

        comments = marks.getExecutionComments().splitlines()
        for line in comments:
            feedback_document.add_paragraph(line, style='CodeChunkComment')

        feedback_document.add_heading('Your code', 3)
        program = marks.getFullProgram().splitlines()
        comments = marks.getErrorList()
        lineNum = 1
        for line in program:
            line_encoded = line.decode('ascii', 'replace')
            highlight = False
            for comment in comments:
                if comment[0] == lineNum:
                    highlight = True
            if highlight:
                feedback_document.add_paragraph(str(lineNum) + '\t: ' + line_encoded, style='CodeChunkHighlight')
                for comment in comments:
                    if comment[0] == lineNum:
                        feedback_document.add_paragraph('\t  ' + comment[1], style='CodeChunkComment')
            else:
                feedback_document.add_paragraph(str(lineNum) + '\t: ' + line_encoded, style='CodeChunk')
            lineNum += 1
        for comment in comments:
            if comment[0] == 0:
                feedback_document.add_paragraph('\t  ' + comment[1], style='CodeChunkComment')

        feedback_document.save(student_dir+'/../'+filename)

    def _construct_name_map(self):
        username_index = 0
        is_constructing_name_map = False

        for i in range(self._marking_sheet.nrows):
            if is_constructing_name_map:
                username =  self._marking_sheet.row_values(i)[username_index]
                firstname = self._marking_sheet.row_values(i)[username_index-1]
                lastname =  self._marking_sheet.row_values(i)[username_index-2]
                self._name_map[username]=[firstname, lastname]

            elif self._marking_sheet.row_values(i).count('Username') is 1:
                username_index = self._marking_sheet.row_values(i).index('Username')
                is_constructing_name_map = True

# Task number
# Folder containing students' folders
# Marker's initials (optional)
# Temp build folder (optional)
# Feedback template (optional)
# Student details list (optional)
# Summary output (optional)

start = time.time()
parser = argparse.ArgumentParser(description='Batch marker for 4001COMP Java programming.')

# Required parameters
parser.add_argument('task', metavar='TASK', type=int, help='Task number (e.g. 1)')
parser.add_argument('workdir', metavar='WORK', type=str, help='Folder containing students\' folders (e.g. ./DLJ)')

# Optional parameters
parser.add_argument('-i', '--initials', metavar='INITIALS', type=str, help='Marker\'s initials (default Master)', default='Master')
parser.add_argument('-b', '--builddir', metavar='BUILD', type=str, help='Folder to output build files to (default ./build)', default='./build')
parser.add_argument('-t', '--template', metavar='TEMPLATE', type=str, help='Word feedback sheeet template (default ./feedback_username.docx)', default='./feedback_username.docx')
parser.add_argument('-d', '--details', metavar='DETAILS', type=str, help='Excel student details list (default ./4001COMP Marking 2014-15.xlsx)', default='./4001COMP Marking 2014-15.xlsx')

parser.add_argument('-s', '--summary', metavar='SUMMARY', type=str, help='Summary of marks as a CSV file (default ./summary.csv)', default='./summary.csv')

# Apply these arguments
args = parser.parse_args()
batchmark = BatchMark(args.task, args.workdir, args.initials, args.builddir, args.template, args.details, args.summary)
batchmark.go()

end = time.time()
duration = end - start
print 'Time taken: {}'.format(duration)

