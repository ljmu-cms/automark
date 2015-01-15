#!/usr/bin/env python
# vim: et:ts=4:textwidth=80

"""
automark

David Llewellyn-Jones
Liverpool John Moores University
18/12/2014
Check a program against task requirements

This script allows a program to be checked using the ideone api.
"""

import re

def _line_from_character_no_space(program, charPos):
	line = 0
	while (line < len(program.lineCharacterStart)) and (charPos >= program.lineCharacterStart[line]):
		line += 1
	return line

def _line_from_character(program, charPos):
	return program.lineNumber[_line_from_character_no_space(program, charPos) - 1]

def check_comment_quality(program, frequencyThreshold, consistencyThreshold, aveOffset, sdOffset, aveWeight):
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
			gapSum += _line_from_character_no_space(program, blockComment.start()) - previousEnd
			previousEnd = _line_from_character_no_space(program, blockComment.end()) + 1
		gapSum += len(program.programLines) - previousEnd
		commentGapAverage = gapSum / float(commentCount)

		gapSumSquared = 0.0
		previousEnd = 0
		for blockComment in blockComments:
			gapSumSquared += ((_line_from_character_no_space(program, blockComment.start()) - previousEnd) - commentGapAverage)**2.0
			previousEnd = _line_from_character_no_space(program, blockComment.end()) + 1
		gapSumSquared += ((len(program.programLines) - previousEnd) - commentGapAverage)**2.0
		commentGapSD = (gapSumSquared / commentCount)**0.5
		
		lastCommentLine = _line_from_character(program, blockComments[commentCount - 1].end())

	commentFrequency = max(1.0 - ((max(commentGapAverage - aveOffset, 0.0)) * aveWeight), 0.0)
	commentConsistency = max(1.0 - ((max(commentGapSD - sdOffset, 0.0)) * 1.0), 0.0)
	commentScore = int(round(commentFrequency + commentConsistency))

	if commentFrequency < frequencyThreshold:
		errorList.append([lastCommentLine, 'Try to include more comments in your code'])
	if commentConsistency < consistencyThreshold:
		errorList.append([lastCommentLine, 'Include comments evenly throughout your code, not just in a few places'])
	return [commentScore, commentGapAverage, commentGapSD, errorList]




