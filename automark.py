#!/usr/bin/env python 
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
import plyjext.parser as plyj
import plyjext.model as model
import execcode
import os
import collections
import indentation
import variables
import comments

Program = collections.namedtuple('Program', ['program', 'programLines', 'fullProgram', 'programTree', 'lineNumber', 'lineCharacterStart'])

class Automark:
	def __init__(self, filename, credentialsFile):
		# Read in the credentials from file
		with open(credentialsFile) as file:
			self.user = file.readline().rstrip('\n')
			self.password = file.readline().rstrip('\n')
			self.score = 0
			self.filename = filename
			self.classname = os.path.splitext(os.path.split(filename)[1])[0]
	
		# Load in the program from file
		fullProgram = ''
		with open(filename) as file:
			fullProgram = file.read()

		program = ""
		lineNumber = []
		self.errorList = []
		lineCharacterStart = []
		foundMain = True
		linesRead = 1
		linesAdded = 0
		characterPos = 0
		with open(filename) as file:
			for line in file.xreadlines():
				if not line.startswith('package '):
					if (not foundMain) and (line.find('public class') >= 0):
						line = re.sub(r'(class\s*).*?($|\s|{)', r'\1Main\2', line)
						foundMain = True
					if not (line.isspace() or (len(line) == 0)):
						program += line
						lineNumber.append(linesRead)
						lineCharacterStart.append(characterPos)
						linesAdded += 1
						characterPos += len(line)
				linesRead += 1

		# Store a line-delimited version of the program 
		programLines = program.splitlines()
		
		# Store a AST version of the program
		parser = plyj.Parser()
		programTree = parser.parse_string(fullProgram)

		self.programStructure = Program(program, programLines, fullProgram, programTree, lineNumber, lineCharacterStart)

		# Initialise the inputs
		self.stdin = ''
		self.executionComments = ''

		# Initialise the scoring state
		self.commentScore = 0
		self.variablesScore = 0
		self.indentationScore = 0
		self.executionScore = 0

		# Initialise the internal stats
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

		self.commentScore = self.checkCommentQuality()
		self.variablesScore = self.checkVariableNameQuality()
		self.indentationScore = self.checkIndentation()
		self.executionScore = self.checkExecution()
		
		print 'Final score: {:d}\n'.format(self.getTotalScore())

	def getFullProgram(self):
		return self.programStructure.fullProgram

	def getTotalScore(self):
		totalScore = self.commentScore + self.variablesScore + self.indentationScore + self.executionScore
		return totalScore

	def getCommentScore(self):
		return self.commentScore
	
	def getVariablesScore(self):
		return self.variablesScore
		
	def getIndentationScore(self):
		return self.indentationScore

	def getExecutionScore(self):
		return self.executionScore

	@staticmethod
	def getScoresStructure():
		return ['Execution', 'Indentation', 'Variables', 'Comments', 'Total']

	def getScores(self):
		# Execution score
		# Indentation
		# Variable names
		# Comments
		# Total
		scores = [self.executionScore, self.indentationScore, self.variablesScore, self.commentScore, self.getTotalScore()]
		return scores

	@staticmethod
	def getInternalStatsStructure():
		return ['Gap average', 'Gap SD', 'Variables short', 'Variables enumerated', 'Indentation errors', 'Execution time', 'Memory used', 'Execution input', 'Execution result',  'Execution output', 'Output check 0', 'Output check 1']

	def getInternalStats(self):
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
		# Output check 0
		# Output checl 1
		stats = [self.commentGapAverage, self.commentGapSD, self.variableShort, self.variableEnumeration, self.indentationErrors, self.executionTime, self.memoryUsed, self.stdin, self.executionResult, self.programOutput.encode('ascii', 'replace'), self.outputCheck[0], self.outputCheck[1]]
		return stats

	def getErrorStatus(self, response):
		error = 'OK'
		for item in response['item']:
			if item.key == 'error' and item.value != 'OK':
				error = item.value
		return error

	def getValue(self, response, key):
		value = ''
		for item in response['item']:
			if item.key == key:
				value = item.value
		return value

	def checkErrorStatus(self, response):
		error = self.getErrorStatus(response)
		if error != 'OK':
			print 'Error: ' + error

	def checkSubmissionsStatus(self, status):
		if status < 0:
			print 'Waiting for compilation'
		elif status == 1:
			print 'Compiling'
		elif status == 3:
			print 'Running'
			
	def getInput(self):
		return self.stdin

	def getOutput(self):
		return self.programOutput.encode('ascii', 'replace')
		
	def getExecutionComments(self):
		return self.executionComments
		
	def getErrorList(self):
		return self.errorList

	def printErrorList(self):
		errorList = ''
		for error in self.errorList:
			errorList += str(error[0]) + ' : ' + error[1] + '\n'
		print errorList

	# Prints output and gives result
	# True - Success; the output appears correct
	# False - Failure; the output looks incorrect
	def checkOutputCorrectness(self, output, width, height, depth):
		self.outputCheck[0] = False
		self.outputCheck[1] = False
		outputScore = 0
		output = re.sub("\n\s*\n*", "\n", output)
		lines = output.splitlines()
		volume = -1
		concat = ''

		correctVolume = (width * height * depth)
		correctConcat = '{:d}{:d}{:d}'.format(width, height, depth)
		volumeFound = False
		concatFound = False
		for line in lines:
			if re.search(r'\d+', line) != None:
				volume = int(re.search(r'\d+', line).group())
				if (volume == correctVolume):
					volumeFound = True
			if re.search(r'\d+', line) != None:
				concat = re.search(r'\d+', line).group()
				if (concat == correctConcat):
					concatFound = True

		if volumeFound:
			outputScore += 2
			self.outputCheck[0] = True
		else:
			self.executionComments += 'Volume calculated incorrectly (should be {:d} for these inputs).\n'.format(correctVolume)

		if concatFound:
			outputScore += 2
			self.outputCheck[1] = True
		else:
			self.executionComments += 'Number strings concatenated incorrectly (should be {} for these inputs).\n'.format(correctConcat)

		return outputScore

	def checkCommentQuality(self):
		result = comments.checkCommentQuality(self.programStructure, 0.75, 0.75)
		commentScore = result[0]
		self.commentGapAverage = result[1]
		self.commentGapSD = result[2]
		self.errorList.extend(result[3])
		return commentScore

	def checkVariableNameQuality(self):
		result = variables.checkVariableNameQuality(self.programStructure, 3)
		variablesScore = result[0]
		self.variableShort = result[1]
		self.variableEnumeration = result[2]
		self.errorList.extend(result[3])
		return variablesScore

	def checkIndentation(self):
		result = indentation.checkIndentation(self.programStructure, 3)
		self.indentationErrors = result[0]
		indentationScore = result[1]
		self.errorList.extend(result[2])
		return indentationScore

	def checkExecution(self):
		executionScore = 0
		#return executionScore
		# Creating wsdl client
		#wsdlObject = WSDL.Proxy('http://ideone.com/api/1/service.wsdl')
		wsdlObject = execcode.ExecCode('build', self.classname)

		# Check the available languages
		#response = wsdlObject.getLanguages(user, password);
		#print response['item'][1].value['item']
		#	We don't need to check the languages every time
		#	Just use:
		#		{'value': 'Java (sun-jdk-1.7.0_25)', 'key': 10}
		#		{'value': 'C++11 (gcc-4.8.1)', 'key': 44}

		# Choose random input variables
		width = random.randint(1, 100)
		height = random.randint(1, 100)
		depth = random.randint(1, 100)
		self.stdin = "{}\n{}\n{}\n".format(width, height, depth)
		#print 'Inputs used: {:d}, {:d}, {:d}'.format(width, height, depth)

		error = 'OK'
		response = wsdlObject.createSubmission(self.user, self.password, self.programStructure.program, 10, self.stdin, True, True)
		error = self.getErrorStatus(response)
		if error != 'OK':
			print 'Error: ' + error
		else:
			link = self.getValue(response, 'link')

			# Periodically check the submission status
			status = -1;
			waitTime = 1
			while status != 0:
				time.sleep(waitTime)
				waitTime = 3
				response = wsdlObject.getSubmissionStatus(self.user, self.password, link)
				self.checkErrorStatus(response)
				status = self.getValue(response, 'status')
				self.checkSubmissionsStatus (status)

			# Find out what happened to the program
			result = self.getValue(response, 'result')
			self.executionResult = result
			if result == 11:
				print 'Compilation error'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, True)
				compInfo = self.getValue(response, 'cmpinfo')
				print 'Compilation output: ' + compInfo
				self.programOutput = compInfo
				self.executionComments = 'Program failed to compile.'
			elif result == 12:
				executionScore += 1
				print 'Runtime error'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
				stdErrOutput = self.getValue(response, 'stderr')
				print 'Runtime error: ' + stdErrOutput
				self.programOutput = stdErrOutput
				self.executionComments = 'Runtime error occurred during execution.'
			elif result == 13:
				executionScore += 1
				print 'Time limit exceeded'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, True, False, False)
				self.executionTime = self.getValue(response, 'time')
				output = self.getValue(response, 'output')
				self.programOutput = output
				result = self.checkOutputCorrectness(output, width, height, depth)
				executionScore += result
				if result > 0:
					executionScore -= 1
				self.executionComments = 'Execution failed to complete (time limit exceeded).'
			elif result == 17:
				executionScore += 1
				print 'Memory limit exceeded'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, False)
				self.memoryUsed = self.getValue(response, 'memory')
				print 'Memory used: {} bytes'.format(self.memoryUsed)
				self.executionComments = 'Execution failed to complete (ran out of memory).'
			elif result == 19:
				print 'Illegal system call'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
				stdErrOutput = self.getValue(response, 'stderr')
				print 'Error output: ' + stdErrOutput
				self.programOutput = stdErrOutput
				self.executionComments = 'Execution failed to complete (illegal system call).'
			elif result == 15:
				executionScore += 1
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, True, False, False)
				self.checkErrorStatus(response)
				self.executionTime = self.getValue(response, 'time')
				self.memoryUsed = self.getValue(response, 'memory')
				date = self.getValue(response, 'date')
				output = self.getValue(response, 'output')
				self.programOutput = output
				result = self.checkOutputCorrectness(output, width, height, depth)
				executionScore += result
				if result == 4:
					self.executionComments = 'Your outputs correctly match the specification.\n'
			else:
				print 'Internal error with the code checking system'

		return executionScore		

