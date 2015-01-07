#!/usr/bin/env python 
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
import string

class Automark(automark.Automark):
	outputChecks = 5

	def __init__(self, filename, credentialsFile, build_dir):
		automark.Automark.__init__(self, filename, credentialsFile, build_dir)

	def setupInputs(self):
		# Establish the name of the input file
		findFileInput = InstanceCreationParamVisitor('FileReader')
		if self.programStructure.programTree != None:
			self.programStructure.programTree.accept(findFileInput)

		# Replace the input file with "input.txt" so we can control it
		filename = findFileInput.getParamList()
		if len(filename) > 0:
			transformed = re.sub(r'(FileReader\s*\(\s*)(' + re.escape(filename[0][0]) + ')(\s*\))', r'\1"input.txt"\3', self.programStructure.program)
			self.programStructure = self.programStructure._replace(program = transformed)

		# Establish the name of the output file
		findFileOutput = InstanceCreationParamVisitor('PrintWriter')
		if self.programStructure.programTree != None:
			self.programStructure.programTree.accept(findFileOutput)

		# Replace the output file with "output.txt" so we can control it
		filename = findFileInput.getParamList()
		if len(filename) > 0:
			transformed = re.sub(r'(PrintWriter\s*\(\s*)(' + re.escape(filename[0][0]) + ')(\s*\))', r'\1"output.txt"\3', self.programStructure.program)
			self.programStructure = self.programStructure._replace(program = transformed)



		# Generate the input file
		journeyCosts = []
		inputContents = ''
		numOfShips = random.randint(5,9)
		shipIDs = []
		for ship in range(0, numOfShips):
			shipID = random.choice(['Monarch', 'Princess', 'Empire', 'Crown', 'Bootle'])
			shipIDs.append(shipID)
			inputContents += '{}\n'.format(shipID)
			journeyID = random.choice(string.ascii_letters) + str(random.randint(10, 999))
			inputContents += '{}\n'.format(journeyID)
			journeyLength = random.randint(4, 30)
			inputContents += '{:d}\n'.format(journeyLength)
			crewNum = random.randint(1, 10)
			inputContents += '{:d}\n'.format(crewNum)
			journeyCost = 0
			for crewMember in range(0, crewNum):
				rate = random.randint(100, 500) / 10.0
				inputContents += '{:f}\n'.format(rate)
				journeyCost += rate * journeyLength
			inputContents += '\n'
			journeyCosts.append(journeyCost)

		# Find median journey cost
		recommendedMax = int ((journeyCosts[int (numOfShips / 2)] + journeyCosts[int (numOfShips / 2) + 1]) / 2.0)

		if not os.path.exists(self.build_dir):
			os.makedirs(self.build_dir)

		fileToWrite = os.path.join(self.build_dir, "input.txt")
		with open(fileToWrite, 'w') as inputFile:
			inputFile.write(inputContents)

		stdin = '{:d}\n'.format(recommendedMax)

		return [stdin, numOfShips, shipIDs, journeyCosts, recommendedMax]


	@staticmethod
	def find_keywords(line, words):
		found = False
		for keyword in words:
			if re.search(re.escape(keyword), line) != None:
				found = True
		return found

	def checkOutputCorrectness(self, output, inputs):
		numOfShips = inputs[1]
		shipISs = inputs[2]
		journeyCostss = inputs[3]
		recommendedMax = inputs[4]

		outputCheck = [False, False, False, False, False]
		outputScore = 0

		output = re.sub("\n\s*\n*", "\n", output)
		lines = output.splitlines()
	
		executionComments = ''

		return [outputScore, executionComments, outputCheck]

class InstanceCreationParamVisitor(model.Visitor):
	def __init__(self, className, paramNum=0, verbose=False):
		super(InstanceCreationParamVisitor, self).__init__()
		self.className = className
		self.paramNum = paramNum
		self.params = []

	def leave_InstanceCreation(self, element):
		if element.type.name.value == self.className:
			param = [element.arguments[self.paramNum].value, element.lineno]
			self.params.append(param)
		return True
		
	def getParamList(self):
		return self.params


