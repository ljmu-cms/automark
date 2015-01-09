#!/usr/bin/env python 
"""
automark

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Check a program against task requirements

This script allows a program to be checked using the ideone api.
"""

import re

def lineFromCharacterNoSpace(program, charPos):
	line = 0
	while (line < len(program.lineCharacterStart)) and (charPos >= program.lineCharacterStart[line]):
		line += 1
	return line

def lineFromCharacter(program, charPos):
	return program.lineNumber[lineFromCharacterNoSpace(program, charPos) - 1]

def checkCommentQuality(program, frequencyThreshold, consistencyThreshold, aveOffset, sdOffset, aveWeight):
	# Regex expressions search for block comments or full-line comments.
	# Multiple full-line comments without other text are considered as a single match
	blockComments = list(re.finditer(r'/\*.*?\*/|//.*?$(?!\s*//)', program.program, (re.MULTILINE | re.DOTALL)))

	errorList = []
	commentGapAverage = 1000.0
	commentGapSD = 1000.0
	lastCommentLine = 0
	commentCount = len(blockComments)
	if commentCount > 0:
		gapSum = 0
		previousEnd = 0
		for blockComment in blockComments:
			gapSum += lineFromCharacterNoSpace(program, blockComment.start()) - previousEnd
			previousEnd = lineFromCharacterNoSpace(program, blockComment.end()) + 1
		gapSum += len(program.programLines) - previousEnd
		commentGapAverage = gapSum / float(commentCount)

		gapSumSquared = 0.0
		previousEnd = 0
		for blockComment in blockComments:
			gapSumSquared += ((lineFromCharacterNoSpace(program, blockComment.start()) - previousEnd) - commentGapAverage)**2.0
			previousEnd = lineFromCharacterNoSpace(program, blockComment.end()) + 1
		gapSumSquared += ((len(program.programLines) - previousEnd) - commentGapAverage)**2.0
		commentGapSD = (gapSumSquared / commentCount)**0.5
		
		lastCommentLine = lineFromCharacter(program, blockComments[commentCount - 1].end())

	commentFrequency = max(1.0 - ((max(commentGapAverage - aveOffset, 0.0)) * aveWeight), 0.0)
	commentConsistency = max(1.0 - ((max(commentGapSD - sdOffset, 0.0)) * 1.0), 0.0)
	commentScore = int(round(commentFrequency + commentConsistency))

	if commentFrequency < frequencyThreshold:
		errorList.append([lastCommentLine, 'Try to include more comments in your code'])
	if commentConsistency < consistencyThreshold:
		errorList.append([lastCommentLine, 'Include comments evenly throughout your code, not just in a few places'])
	return [commentScore, commentGapAverage, commentGapSD, errorList]




