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
import comments
import indentation
import execcode

class Automark(automark.Automark):
	outputChecks = 2

	def __init__(self, filename, credentialsFile, build_dir):
		automark.Automark.__init__(self, filename, credentialsFile, build_dir)

	def setupInputs(self):
		width = random.randint(1, 100)
		height = random.randint(1, 100)
		depth = random.randint(1, 100)
		stdin = "{}\n{}\n{}\n".format(width, height, depth)
		return [stdin, width, height, depth]

	# Prints output and gives result
	# True - Success; the output appears correct
	# False - Failure; the output looks incorrect
	def checkOutputCorrectness(self, output, inputs):
		width = inputs[1]
		height = inputs[2]
		depth = inputs[3]
		outputCheck = [False, False]
		outputScore = 0
		output = re.sub("\n\s*\n*", "\n", output)
		lines = output.splitlines()
		volume = -1
		concat = ''
		executionComments = ''

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
			outputScore += 1.5
			outputCheck[0] = True
		else:
			executionComments += 'Volume calculated incorrectly (should be {:d} for these inputs).\n'.format(correctVolume)

		if concatFound:
			outputScore += 1.5
			outputCheck[1] = True
		else:
			executionComments += 'Number strings concatenated incorrectly (should be {} for these inputs).\n'.format(correctConcat)

		return [outputScore, executionComments, outputCheck]

	def checkExecuteResult(self, result):
		outputScore = 0
		if execcode.ExecCode.responseCheckCompiled(result):
			outputScore += 1.5
		return outputScore

	def checkIndentation(self):
		result = indentation.checkIndentation(self.programStructure, 1, 5)
		self.indentationErrors = result[0]
		indentationScore = result[1]
		self.errorList.extend(result[2])
		return indentationScore

	def checkCommentQuality(self):
		result = comments.checkCommentQuality(self.programStructure, 0.75, 0.75, 1.0, 3.0, 0.01)
		commentScore = result[0]
		self.commentGapAverage = result[1]
		self.commentGapSD = result[2]
		self.errorList.extend(result[3])
		return commentScore


