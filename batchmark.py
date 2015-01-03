#!/usr/bin/env python 
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
import time

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

		self.task = task
		self.marking_dir = marking_dir
		self.marker_name = marker_name
		self.buid_dir = build_dir
		self.feedback_doc_name = feedback_doc_name
		self.marking_sheet_name = marking_sheet_name
		self.summary_out = summary_out

		# Select the appropriate task
		tasks = [automark, automarktask1, automarktask2]
		if (self.task < len(tasks)) and (self.task >= 0):
			self.taskSpecific = tasks[self.task]
		else:
			self.taskSpecific = tasks[0]
			print 'Task number out of bounds. Applying general checks.'

		#load student feedback form as a template
		self.feedback_document = Document(feedback_doc_name)
		#load my marking sheet 'PT' from workbook
		self.marking_sheet = xlrd.open_workbook(marking_sheet_name).sheet_by_name(marker_name)

	#do things
	def go(self):
		#username to firstname lastname map/dictionary
		self.name_map = {}
		self.construct_name_map()
		with open(self.summary_out, 'w') as self.summary:
			self.outputcsv_co(['Username', 'Name'])
			self.outputcsv_co(self.taskSpecific.Automark.getScoresStructure())
			self.outputcsv_co(self.taskSpecific.Automark.getInternalStatsStructure())
			self.outputcsv_nl(self.taskSpecific.Automark.getOutputChecksStructure())
			self.create_new_feedback_document()

	#probably won't work for Windows
	def unzip_submission(self, student_dir):
		#form unzip command
		cmd = ['unzip', '-q', '-o', '-d', student_dir + '/', student_dir + '/*.zip']
		#print cmd, '\n\n'
		sys_process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		std_out = sys_process.communicate()
		#std_out = sys_process.stdout.read().strip()
		#print std_out

	def outputcsv(self, items):
		count = 0
		for item in items:
			self.summary.write('\"')
			self.summary.write(str(item))
			self.summary.write('\"')
			if count < (len(items) - 1):
				self.summary.write(', ')
			count += 1

	def outputcsv_co(self, items):
		self.outputcsv(items)
		self.summary.write(', ')

	def outputcsv_nl(self, items):
		self.outputcsv(items)
		self.summary.write('\n')

	def mark (self, directory):
		java_file = ''
		for check_dir, _, file in os.walk(directory):
			if '__MACOSX' not in check_dir.split('/'):
				for file_name in file:
					if file_name.endswith('.java'):
						java_file = os.path.join(check_dir, file_name)
		return java_file

	def create_new_feedback_document(self):
		print
		#marker_directory = os.path.dirname(os.path.realpath(__file__))+'/'+self.marker_name
		for student_dir, _, file in os.walk(self.marking_dir):
			student_dir_name = os.path.relpath(student_dir, self.marking_dir)

			#print student_dir
			if (student_dir_name is not '.') and (student_dir_name in self.name_map):
				print 'Student: {}'.format(student_dir_name)
				student_name = self.name_map[student_dir_name][0] + ' ' + self.name_map[student_dir_name][1]
				self.unzip_submission(student_dir)
				java_path = self.mark(student_dir)
				if java_path == '':
					print 'No java file'
					self.write_student_name_to_document(student_dir, student_dir_name, student_name)
				else:
					#print 'file: {}'.format(java_path)
					marks = self.taskSpecific.Automark(java_path, 'credentials.txt', self.buid_dir)
					self.write_details_to_document(student_dir, student_dir_name, student_name, marks)
					self.write_comments_to_document(student_dir, student_dir_name, marks)
					self.outputcsv_co([student_dir_name, student_name])
					self.outputcsv_co(marks.getScores())
					self.outputcsv_co(marks.getInternalStats())
					self.outputcsv_nl(marks.getOutputChecks())

				#just do something extra
				#self.unzip_submission(student_dir)

	def write_details_to_document(self, student_dir, student_dir_name, student_name, marks):
		#default cell for student's firstname lastname
		filename = self.feedback_doc_name.replace('username', student_dir_name)
		self.feedback_document.paragraphs[0].text = self.feedback_document.paragraphs[0].text.replace('<task>', str(self.task))
		self.feedback_document.tables[0].cell(1,0).text = student_name
		self.feedback_document.tables[0].cell(1,1).text = student_dir_name
		#self.feedback_document.tables[0].cell(1,2).text = self.marker_name
		self.feedback_document.tables[0].cell(1,2).text = 'auto'
		#print student_dir+'/'+filename
		# Clear tables
		for row in range(1,16):
			self.feedback_document.tables[2].cell(row, 2).text = ''
	
		executionScore = marks.getExecutionScore()
		indentationScore = marks.getIndentationScore()
		variablesScore = marks.getVariablesScore()
		commentScore = marks.getCommentScore()
		totalScore = marks.getTotalScore()
		efficientScore = 0
		if executionScore > 5:
			efficientScore = 1
			executionScore -= 1
		self.feedback_document.tables[2].cell((2 + executionScore), 2).text = str(executionScore)
		self.feedback_document.tables[2].cell(9, 2).text = str(indentationScore)
		self.feedback_document.tables[2].cell(10, 2).text = str(variablesScore)
		self.feedback_document.tables[2].cell(11, 2).text = str(efficientScore)
		self.feedback_document.tables[2].cell(13 + commentScore, 2).text = str(commentScore)
		self.feedback_document.tables[2].cell(16, 2).text = str(totalScore)
		self.feedback_document.save(student_dir+'/../'+filename)

	def write_student_name_to_document(self, student_dir, student_dir_name, student_name):
		#default cell for student's firstname lastname
		filename = self.feedback_doc_name.replace('username', student_dir_name)
		self.feedback_document.tables[0].cell(1,0).text = student_name
		self.feedback_document.tables[0].cell(1,1).text = student_dir_name
		self.feedback_document.tables[0].cell(1,2).text = self.marker_name
		self.feedback_document.save(student_dir+'/../'+filename)
		#print student_dir+'/'+filename

	def write_comments_to_document(self, student_dir, student_dir_name, marks):
		filename = os.path.basename(self.feedback_doc_name).replace('username', student_dir_name)

		feedback_document = Document(student_dir+'/../'+filename)
		feedback_document.add_heading('Program Comments', 2)

		feedback_document.add_heading('Program input', 3)
		inputs = marks.getInput().splitlines()

		for line in inputs:
			feedback_document.add_paragraph(line, style='CodeChunk')

		feedback_document.add_heading('Program output', 3)

		output = marks.getOutput().splitlines()
		for line in output:
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

	def construct_name_map(self):
		username_index = 0
		is_constructing_name_map = False

		for i in range(self.marking_sheet.nrows):
			if is_constructing_name_map:
				username =  self.marking_sheet.row_values(i)[username_index]
				firstname = self.marking_sheet.row_values(i)[username_index-1]
				lastname =  self.marking_sheet.row_values(i)[username_index-2]
				self.name_map[username]=[firstname, lastname]

			elif self.marking_sheet.row_values(i).count('Username') is 1:
				username_index = self.marking_sheet.row_values(i).index('Username')
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
hk = BatchMark(args.task, args.workdir, args.initials, args.builddir, args.template, args.details, args.summary)
hk.go()

end = time.time()
duration = end - start
print 'Time taken: {}'.format(duration)

