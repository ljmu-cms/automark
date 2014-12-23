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
import plyj.parser as plyj

class Automark:
	def __init__(self, filename, credentialsFile):
		# Read in the credentials from file
		with open(credentialsFile) as file:
			self.user = file.readline().rstrip('\n')
			self.password = file.readline().rstrip('\n')
			self.score = 0
			self.filename = filename
	
		# Load in the program from file
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

		self.programLines = self.program.splitlines()
		
		parser = plyj.Parser()
		tree = parser.parse_string(self.program)
		#print tree

		#print self.program
		# Initialise the scoring state
		self.commentScore = 0
		self.variablesScore = 0
		self.indentationScore = 0
		self.executionScore = 0

		self.commentScore = self.checkCommentQuality()
		self.variablesScore = self.checkVariableNameQuality()
		self.indentationScore = self.checkIndentation()
		self.executionScore = self.checkExecution()
		
		print self.getErrorList()

		print
		print 'Final score: {:d}'.format(self.getTotalScore())

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

	def getErrorList(self):
		errorList = ""
		for error in self.errorList:
			errorList += str(error[0]) + ' : ' + error[1] + '\n'
		return errorList

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
		outputScore = 0
		output = re.sub("\n\s*\n*", "\n", output)
		lines = output.splitlines()
		volume = -1
		concat = ''
		if len(lines) < 2:
			result = False
			print 'Insufficient ({:d}) lines of output.'.format(len(lines))
		else:
			volumeLine = lines[len(lines) - 2]
			concatLine = lines[len(lines) - 1]
			if re.search(r'\d+', volumeLine) != None:
				volume = int(re.search(r'\d+', volumeLine).group())
			if re.search(r'\d+', concatLine) != None:
				concat = re.search(r'\d+', concatLine).group()
			correctVolume = (width * height * depth)
			correctConcat = '{:d}{:d}{:d}'.format(width, height, depth)
			print 'Correct volume: {:d}\nOutput  volume: {:d}'.format(correctVolume, volume)
			print 'Correct concat: {}\nOutput  concat: {}'.format(correctConcat, concat)
			if (volume == correctVolume):
				outputScore += 2
			if (concat == correctConcat):
				outputScore += 2
		return outputScore

	def checkCommentQuality(self):
		# Regex expressions search for block comments or full-line comments.
		# Multiple full-line comments without other text are considered as a single match
		blockComments = list(re.finditer(r'/\*.*?\*/|//.*?$(?!\s*//)', self.program, (re.MULTILINE | re.DOTALL)))

		gapAve = 1000.0
		gapSD = 1000.0
		lastCommentLine = 0
		commentCount = len(blockComments)
		if commentCount > 0:
			gapSum = 0
			previousEnd = 0
			for blockComment in blockComments:
				gapSum += self.lineFromCharacterNoSpace(blockComment.start()) - previousEnd
				previousEnd = self.lineFromCharacterNoSpace(blockComment.end()) + 1
			gapSum += len(self.programLines) - previousEnd
			gapAve = gapSum / float(commentCount)
			print 'New comment count: ' + str(commentCount)
			print 'New gap: ' + str(gapSum)
			print 'New gap ave: ' + str(gapAve)

			gapSumSquared = 0.0
			previousEnd = 0
			for blockComment in blockComments:
				gapSumSquared += ((self.lineFromCharacterNoSpace(blockComment.start()) - previousEnd) - gapAve)**2.0
				previousEnd = self.lineFromCharacterNoSpace(blockComment.end()) + 1
			gapSumSquared += ((len(self.programLines) - previousEnd) - gapAve)**2.0
			gapSD = (gapSumSquared / commentCount)**0.5
			print 'New gap squared: ' + str(gapSumSquared)
			
			lastCommentLine = self.lineFromCharacter(blockComments[commentCount - 1].end())

		print 'Comment stats. Gap average: {:f}. Gap SD: {:f}'.format(gapAve, gapSD)
		commentFrequency = max(1.0 - ((max(gapAve - 3.0, 0.0))/2.0), 0.0)
		commentConsistency = max(1.0 - ((max(gapSD - 2.0, 0.0))/1.0), 0.0)
		commentScore = int(round(commentFrequency + commentConsistency))
		#print 'Comment score: {:d}'.format(commentScore)

		if commentFrequency < 0.75:
			self.errorList.append([lastCommentLine, 'Try to include more useful comments in your code'])
		if commentConsistency < 0.75:
			self.errorList.append([lastCommentLine, 'Your comments should be included throughout your code'])
		return commentScore

	def getVariableName(self, line):
		name = ''
		# Collect the variable name using a regular expression
		variable = re.sub(r'.*?(int|float|double|String)\s(.*?)[\s=;].*', r'\2', line)
		#type = re.sub(r'.*?(int|float|double|String)\s(.*?)[\s=;].*', r'\1', line)
		if variable != line:
			name = str(variable)
		return name

	def checkVariableNameQuality(self):
		strike = 0
		name = ''
		lineCount = 0
		for line in self.programLines:
			name = self.getVariableName(line)
			if len(name) > 0:
				if len(name) < 3:
					strike += 1
					if (strike == 3):
						self.errorList.append([self.lineNumber[lineCount], 'Use clear and expressive variable names'])
				if re.search(r'\d+', name) != None:
					if int(re.search(r'\d+', name).group()) > 0:
						strike += 1
						if (strike == 3):
							self.errorList.append([self.lineNumber[lineCount], 'Use clear and expressive variable names'])
			lineCount += 1
		#print 'Variable name strikes: {:d}'.format(strike)
		variablesScore = 1
		if strike >= 3:
			variablesScore = 0
		#print 'Variable name score: {:d}'.format(variablesScore)
		return variablesScore

	def checkIndentation(self):
		indentationErrors = 0
		indent = 0
		lineNum = 0
		preChange = 0
		for line in self.programLines:
			add = line.count('{')
			sub = line.count('}')
			tabs = 0
			while line[tabs] == '\t':
				tabs += 1
			indent -= sub
			if (indent != tabs):
				if (add == 0) and (sub == 0) and (tabs != preChange):
					indentationErrors += 1
					if indentationErrors > 4:
						self.errorList.append([self.lineNumber[lineNum], 'Indentation error'])
					preChange = tabs
				indent = tabs
			indent += add
			lineNum += 1
		if indentationErrors > 4:
			indentatinoScore = 0
		else:
			indentatinoScore = 1
		print 'Indentation score: {:d}'.format(indentatinoScore)
		return indentatinoScore


	def checkExecution(self):
		executionScore = 0
		return executionScore
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
		stdin = "{}\n{}\n{}\n".format(width, height, depth)
		print 'Inputs used: {:d}, {:d}, {:d}'.format(width, height, depth)

		error = 'OK'
		response = wsdlObject.createSubmission(self.user, self.password, self.program, 10, stdin, True, True)
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
			if result == 11:
				print 'Compilation error'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, True)
				compInfo = self.getValue(response, 'cmpinfo')
				print 'Compilation output: ' + compInfo
			elif result == 12:
				executionScore += 1
				print 'Runtime error'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
				stdErrOutput = self.getValue(response, 'stderr')
				print 'Runtime error: ' + stdErrOutput
			elif result == 13:
				executionScore += 1
				print 'Time limit exceeded'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, False)
				executionTime = self.getValue(response, 'time')
				print 'Execution time: {:f}s'.format(executionTime)
			elif result == 17:
				executionScore += 1
				print 'Memory limit exceeded'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, False, False)
				memoryUsed = self.getValue(response, 'memory')
				print 'Memory used: {} bytes'.format(memoryUsed)
			elif result == 19:
				print 'Illegal system call'
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, False, True, False)
				stdErrOutput = self.getValue(response, 'stderr')
				print 'Error output: ' + stdErrOutput
			elif result == 15:
				executionScore += 1
				response = wsdlObject.getSubmissionDetails(self.user, self.password, link, False, False, True, False, False)
				self.checkErrorStatus(response)
				executionTime = self.getValue(response, 'time')
				print 'Execution time: {:f}s'.format(executionTime)
				memoryUsed = self.getValue(response, 'memory')
				print 'Memory used: {} bytes'.format(memoryUsed)
				date = self.getValue(response, 'date')
				print 'Date submitted: ' + date
				output = self.getValue(response, 'output')
				print
				print 'Output: ' + output
				result = self.checkOutputCorrectness(output, width, height, depth)
				executionScore += result
				if result == 4:
					print 'Success!'
				else:
					print 'Failure :('
			else:
				print 'Internal error with the code checking system'

		return executionScore		

#am = Automark('task.java', 'credentials.txt')

