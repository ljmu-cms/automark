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
		with open(filename) as file:
			self.program = file.read()

		# Initialise the scoring state
		self.commentScore = 0
		self.variableScore = 0
		self.indentationScore = 0
		self.executionScore = 0

		self.commentScore = self.checkCommentQuality()
		self.variableScore = self.checkVariableNameQuality()
		self.executionScore = self.checkExecution()

		print
		print 'Final score: {:d}'.format(self.getTotalScore())

	def getTotalScore(self):
		totalScore = self.commentScore + self.variableScore + self.indentationScore + self.executionScore
		return totalScore

	def getCommentScore(self):
		return commentScore
	
	def getVariableScore(self):
		return variableScore
		
	def getIndentationScore(self):
		return indentationScore

	def getExecutionScore(self):
		return executionScore


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
		lines = self.program.splitlines()
		commentCount = 0.0
		gapSum = 0.0
		gapAve = 0.0
		inCommentBlock = False
		linesSinceLast = -1
		for line in lines:
			linesSinceLast += 1
			if (line.find('/*') >= 0) or (line.find('//') >= 0):
				if (inCommentBlock == False):
					# This is the start of a new comment
					gapSum += linesSinceLast
					linesSinceLast = 0
					commentCount += 1
				inCommentBlock = True
			if line.find('*/') >= 0:
				# End of a block comment
				inCommentBlock = False
				linesSinceLast = 0
			if (inCommentBlock == True) and (line.find('//') < 0):
				inCommentBlock = False
				linesSinceLast = 0
		gapSum += linesSinceLast
		if commentCount > 0:
			gapAve = gapSum / commentCount
		else:
			gapAve = 1000
			commentCount = 1

		gapSumSquared = 0.0
		gapSD = 0.0
		inCommentBlock = False
		linesSinceLast = -1
		for line in lines:
			linesSinceLast += 1
			if (line.find('/*') >= 0) or (line.find('//') >= 0):
				if (inCommentBlock == False):
					# This is the start of a new comment
					gapSumSquared += (linesSinceLast - gapAve)**2.0
					linesSinceLast = 0
				inCommentBlock = True
			if line.find('*/') >= 0:
				# End of a block comment
				inCommentBlock = False
				linesSinceLast = 0
			if (inCommentBlock == True) and (line.find('//') < 0):
				inCommentBlock = False
				linesSinceLast = 0
		gapSumSquared += (linesSinceLast - gapAve)**2.0
		gapSD = (gapSumSquared / commentCount)**0.5
		print 'Comment stats. Gap average: {:f}. Gap SD: {:f}'.format(gapAve, gapSD)
		commentScore = 0.0
		commentScore += max(1.0 - ((max(gapAve - 3.0, 0.0))/2.0), 0.0)
		commentScore += max(1.0 - ((max(gapSD - 2.0, 0.0))/1.0), 0.0)
		commentScore = int(round(commentScore))
		print 'Comment score: {:d}'.format(commentScore)
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
		lines = self.program.splitlines()
		strike = 0
		name = ''
		for line in lines:
			name = self.getVariableName(line)
			if len(name) > 0:
				if len(name) < 3:
					strike += 1
					print name
				if re.search(r'\d+', name) != None:
					if int(re.search(r'\d+', name).group()) > 0:
						strike += 1
						print name
		print 'Variable name strikes: {:d}'.format(strike)
		variableScore = 1
		if strike >= 3:
			variableScore = 0
		print 'Variable name score: {:d}'.format(variableScore)
		return variableScore

	def checkExecution(self):
		executionScore = 0
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
				executionScore += 2
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

am = Automark('task.java', 'credentials.txt')

