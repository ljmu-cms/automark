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

class Automark:
	def __init__(self, filename, credentialsFile):
		# Read in the credentials from file
		with open(credentialsFile) as file:
			self.user = file.readline().rstrip('\n')
			self.password = file.readline().rstrip('\n')
			self.score = 0
			self.filename = filename
	
		# Load in the program from file
		self.fullProgram = ''
		with open(filename) as file:
			self.fullProgram = file.read()

		self.program = ""
		self.lineNumber = []
		self.errorList = []
		self.lineCharacterStart = []
		foundMain = False
		linesRead = 1
		linesAdded = 0
		characterPos = 0
		with open(filename) as file:
			for line in file.xreadlines():
				if not line.startswith('package '):
					if (not foundMain) and (line.find('public class') >= 0):
						line = re.sub(r'(class\s*).*?($|\s|{)', r'\1Main\2', line)
						#line = line.replace('public class', 'class', 1)
						foundMain = True
					if not (line.isspace() or (len(line) == 0)):
						self.program += line
						self.lineNumber.append(linesRead)
						self.lineCharacterStart.append(characterPos)
						linesAdded += 1
						characterPos += len(line)
				linesRead += 1

		# Store a line-delimited version of the program 
		self.programLines = self.program.splitlines()
		
		# Store a AST version of the program
		parser = plyj.Parser()
		self.programTree = parser.parse_string(self.fullProgram)

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
		
		self.printErrorList()

		print 'Final score: {:d}\n'.format(self.getTotalScore())

	def getFullProgram(self):
		return self.fullProgram

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


	def lineFromCharacterNoSpace(self, charPos):
		line = 0
		while (line < len(self.lineCharacterStart)) and (charPos >= self.lineCharacterStart[line]):
			line += 1
		return line

	def lineFromCharacter(self, charPos):
		return self.lineNumber[self.lineFromCharacterNoSpace(charPos) - 1]

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
		if len(lines) < 2:
			result = False
			#print 'Insufficient ({:d}) lines of output.'.format(len(lines))
		else:
			volumeLine = lines[len(lines) - 2]
			concatLine = lines[len(lines) - 1]
			if re.search(r'\d+', volumeLine) != None:
				volume = int(re.search(r'\d+', volumeLine).group())
			if re.search(r'\d+', concatLine) != None:
				concat = re.search(r'\d+', concatLine).group()
			correctVolume = (width * height * depth)
			correctConcat = '{:d}{:d}{:d}'.format(width, height, depth)
			#print 'Correct volume: {:d}\nOutput  volume: {:d}'.format(correctVolume, volume)
			#print 'Correct concat: {}\nOutput  concat: {}'.format(correctConcat, concat)
			if (volume == correctVolume):
				outputScore += 2
				self.outputCheck[0] = True
			else:
				self.executionComments += 'Volume calculated incorrectly.\n'
			if (concat == correctConcat):
				outputScore += 2
				self.outputCheck[1] = True
			else:
				self.executionComments += 'Concatenated string calculated incorrectly.\n'			
		return outputScore

	def checkCommentQuality(self):
		# Regex expressions search for block comments or full-line comments.
		# Multiple full-line comments without other text are considered as a single match
		blockComments = list(re.finditer(r'/\*.*?\*/|//.*?$(?!\s*//)', self.program, (re.MULTILINE | re.DOTALL)))

		self.commentGapAverage = 1000.0
		self.commentGapSD = 1000.0
		lastCommentLine = 0
		commentCount = len(blockComments)
		if commentCount > 0:
			gapSum = 0
			previousEnd = 0
			for blockComment in blockComments:
				gapSum += self.lineFromCharacterNoSpace(blockComment.start()) - previousEnd
				previousEnd = self.lineFromCharacterNoSpace(blockComment.end()) + 1
			gapSum += len(self.programLines) - previousEnd
			self.commentGapAverage = gapSum / float(commentCount)

			gapSumSquared = 0.0
			previousEnd = 0
			for blockComment in blockComments:
				gapSumSquared += ((self.lineFromCharacterNoSpace(blockComment.start()) - previousEnd) - self.commentGapAverage)**2.0
				previousEnd = self.lineFromCharacterNoSpace(blockComment.end()) + 1
			gapSumSquared += ((len(self.programLines) - previousEnd) - self.commentGapAverage)**2.0
			self.commentGapSD = (gapSumSquared / commentCount)**0.5
			
			lastCommentLine = self.lineFromCharacter(blockComments[commentCount - 1].end())

		#print 'Comment stats. Gap average: {:f}. Gap SD: {:f}'.format(self.commentGapAverage, self.commentGapSD)
		commentFrequency = max(1.0 - ((max(self.commentGapAverage - 3.0, 0.0))/2.0), 0.0)
		commentConsistency = max(1.0 - ((max(self.commentGapSD - 2.0, 0.0))/1.0), 0.0)
		commentScore = int(round(commentFrequency + commentConsistency))
		#print 'Comment score: {:d}'.format(commentScore)

		if commentFrequency < 0.75:
			self.errorList.append([lastCommentLine, 'Try to include more comments in your code'])
		if commentConsistency < 0.75:
			self.errorList.append([lastCommentLine, 'Include comments evenly throughout your code, not just in a few places'])
		return commentScore

	def checkVariableNameQuality(self):
		findVars = VariableVisitor()
		self.programTree.accept(findVars)
		self.variableShort = 0
		self.variableEnumeration = 0
		
		strike = 0
		name = ''
		for variable in findVars.variables:
			name = variable[0]
			if len(name) > 0:
				if len(name) < 3:
					self.variableShort += 1
					strike += 1
					if (strike == 3):
						self.errorList.append([variable[1], 'Use variable names that represent what they\'re being used for'])
				if re.search(r'\d+', name) != None:
					if int(re.search(r'\d+', name).group()) > 0:
						self.variableEnumeration += 1
						strike += 1
						if (strike == 3):
							self.errorList.append([variable[1], 'Avoid using sequentially numbered variables names'])
		#print 'Variable name strikes: {:d}'.format(strike)
		variablesScore = 1
		if strike >= 3:
			variablesScore = 0
		#print 'Variable name score: {:d}'.format(variablesScore)
		return variablesScore

	def checkIndentation(self):
		self.indentationErrors = 0
		indent = 0
		lineNum = 0
		firstError = 0
		for line in self.programLines:
			add = line.count('{')
			sub = line.count('}')
			tabs = 0
			while line[tabs] == '\t':
				tabs += 1
			indent -= sub
			if (indent != tabs) or ((len(line) > tabs) and (line[tabs] == ' ')):
				self.indentationErrors += 1
				if self.indentationErrors <= 1:
					firstError = lineNum
				if self.indentationErrors == 4:
					self.errorList.append([self.lineNumber[firstError], 'Indentation error'])
				indent = tabs
			indent += add
			lineNum += 1
		if self.indentationErrors > 3:
			indentatinoScore = 0
		else:
			indentatinoScore = 1
		#print 'Indentation score: {:d} with {:d} errors'.format(indentatinoScore, self.indentationErrors)
		return indentatinoScore


	def checkExecution(self):
		executionScore = 0
		#return executionScore
		# Creating wsdl client
		wsdlObject = WSDL.Proxy('http://ideone.com/api/1/service.wsdl')

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
		response = wsdlObject.createSubmission(self.user, self.password, self.program, 10, self.stdin, True, True)
		error = self.getErrorStatus(response)
		if error != 'OK':
			print 'Error: ' + error
		else:
			link = self.getValue(response, 'link')

			# Periodically check the submission status
			status = -1;
			waitTime = 0
			while status != 0:
				time.sleep(waitTime)
				waitTime = 3
				response = wsdlObject.getSubmissionStatus(self.user, self.password, link)
				self.checkErrorStatus(response)
				status = self.getValue(response, 'status')
				self.checkSubmissionsStatus (status)

			print
		
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
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, False)
				self.executionTime = self.getValue(response, 'time')
				#print 'Execution time: {:f}s'.format(self.executionTime)
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
				#print 'Execution time: {:f}s'.format(self.executionTime)
				self.memoryUsed = self.getValue(response, 'memory')
				#print 'Memory used: {} bytes'.format(self.memoryUsed)
				date = self.getValue(response, 'date')
				#print 'Date submitted: ' + date
				output = self.getValue(response, 'output')
				print
				print 'Output: ' + output
				self.programOutput = output
				result = self.checkOutputCorrectness(output, width, height, depth)
				executionScore += result
				if result == 4:
					self.executionComments = 'Your outputs correctly match the specification.\n'
			else:
				print 'Internal error with the code checking system'

		return executionScore		

class VariableVisitor(model.Visitor):

	def __init__(self, verbose=False):
		super(VariableVisitor, self).__init__()
		self.variables = []

	def leave_VariableDeclaration(self, element):
		#msg = 'Variable type ({}); name ({}); line no ({})'
		#print msg.format(element.type, element.variable_declarators[0].variable.name, element.variable_declarators[0].variable.lineno)
		self.variables.append([element.variable_declarators[0].variable.name, element.variable_declarators[0].variable.lineno])
		return True


#am = Automark('task.java', 'credentials.txt')

